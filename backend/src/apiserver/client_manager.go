// Copyright 2018 Google LLC
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
// https://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

package main

import (
	"database/sql"
	"fmt"
	"github.com/kubeflow/pipelines/backend/src/apiserver/common"
	v1 "k8s.io/client-go/kubernetes/typed/core/v1"
	"os"
	"time"

	workflowclient "github.com/argoproj/argo/pkg/client/clientset/versioned/typed/workflow/v1alpha1"
	"github.com/cenkalti/backoff"
	"github.com/golang/glog"

	"github.com/jinzhu/gorm"
	_ "github.com/jinzhu/gorm/dialects/sqlite"
	"github.com/kubeflow/pipelines/backend/src/apiserver/client"
	"github.com/kubeflow/pipelines/backend/src/apiserver/model"
	"github.com/kubeflow/pipelines/backend/src/apiserver/storage"
	"github.com/kubeflow/pipelines/backend/src/common/util"
	scheduledworkflowclient "github.com/kubeflow/pipelines/backend/src/crd/pkg/client/clientset/versioned/typed/scheduledworkflow/v1beta1"
	"github.com/minio/minio-go"
)

const (
	minioServiceHost       = "MINIO_SERVICE_SERVICE_HOST"
	minioServicePort       = "MINIO_SERVICE_SERVICE_PORT"
	mysqlServiceHost       = "DBConfig.Host"
	mysqlServicePort       = "DBConfig.Port"
	mysqlUser              = "DBConfig.User"
	mysqlPassword          = "DBConfig.Password"
	mysqlDBName            = "DBConfig.DBName"
	mysqlGroupConcatMaxLen = "DBConfig.GroupConcatMaxLen"
	kfamServiceHost        = "PROFILES_KFAM_SERVICE_HOST"
	kfamServicePort        = "PROFILES_KFAM_SERVICE_PORT"

	visualizationServiceHost = "ML_PIPELINE_VISUALIZATIONSERVER_SERVICE_HOST"
	visualizationServicePort = "ML_PIPELINE_VISUALIZATIONSERVER_SERVICE_PORT"

	podNamespace          = "POD_NAMESPACE"
	initConnectionTimeout = "InitConnectionTimeout"
)

// Container for all service clients
type ClientManager struct {
	db                     *storage.DB
	experimentStore        storage.ExperimentStoreInterface
	pipelineStore          storage.PipelineStoreInterface
	jobStore               storage.JobStoreInterface
	runStore               storage.RunStoreInterface
	resourceReferenceStore storage.ResourceReferenceStoreInterface
	dBStatusStore          storage.DBStatusStoreInterface
	defaultExperimentStore storage.DefaultExperimentStoreInterface
	objectStore            storage.ObjectStoreInterface
	wfClient               workflowclient.WorkflowInterface
	swfClient              scheduledworkflowclient.ScheduledWorkflowInterface
	podClient              v1.PodInterface
	kfamClient             client.KFAMClientInterface
	time                   util.TimeInterface
	uuid                   util.UUIDGeneratorInterface
}

func (c *ClientManager) ExperimentStore() storage.ExperimentStoreInterface {
	return c.experimentStore
}

func (c *ClientManager) PipelineStore() storage.PipelineStoreInterface {
	return c.pipelineStore
}

func (c *ClientManager) JobStore() storage.JobStoreInterface {
	return c.jobStore
}

func (c *ClientManager) RunStore() storage.RunStoreInterface {
	return c.runStore
}

func (c *ClientManager) ResourceReferenceStore() storage.ResourceReferenceStoreInterface {
	return c.resourceReferenceStore
}

func (c *ClientManager) DBStatusStore() storage.DBStatusStoreInterface {
	return c.dBStatusStore
}

func (c *ClientManager) DefaultExperimentStore() storage.DefaultExperimentStoreInterface {
	return c.defaultExperimentStore
}

func (c *ClientManager) ObjectStore() storage.ObjectStoreInterface {
	return c.objectStore
}

func (c *ClientManager) Workflow() workflowclient.WorkflowInterface {
	return c.wfClient
}

func (c *ClientManager) ScheduledWorkflow() scheduledworkflowclient.ScheduledWorkflowInterface {
	return c.swfClient
}

func (c *ClientManager) PodClient() v1.PodInterface {
	return c.podClient
}

func (c *ClientManager) KFAMClient() client.KFAMClientInterface {
	return c.kfamClient
}

func (c *ClientManager) Time() util.TimeInterface {
	return c.time
}

func (c *ClientManager) UUID() util.UUIDGeneratorInterface {
	return c.uuid
}

func (c *ClientManager) init() {
	glog.Info("Initializing client manager")
	db := initDBClient(common.GetDurationConfig(initConnectionTimeout))

	// time
	c.time = util.NewRealTime()

	// UUID generator
	c.uuid = util.NewUUIDGenerator()

	c.db = db
	c.experimentStore = storage.NewExperimentStore(db, c.time, c.uuid)
	c.pipelineStore = storage.NewPipelineStore(db, c.time, c.uuid)
	c.jobStore = storage.NewJobStore(db, c.time)
	c.resourceReferenceStore = storage.NewResourceReferenceStore(db)
	c.dBStatusStore = storage.NewDBStatusStore(db)
	c.defaultExperimentStore = storage.NewDefaultExperimentStore(db)
	c.objectStore = initMinioClient(common.GetDurationConfig(initConnectionTimeout))

	c.wfClient = client.CreateWorkflowClientOrFatal(
		common.GetStringConfig(podNamespace), common.GetDurationConfig(initConnectionTimeout))

	c.swfClient = client.CreateScheduledWorkflowClientOrFatal(
		common.GetStringConfig(podNamespace), common.GetDurationConfig(initConnectionTimeout))

	c.podClient = client.CreatePodClientOrFatal(
		common.GetStringConfig(podNamespace), common.GetDurationConfig(initConnectionTimeout))

	runStore := storage.NewRunStore(db, c.time)
	c.runStore = runStore

	if common.IsMultiUserMode() {
		c.kfamClient = client.NewKFAMClient(common.GetStringConfig(kfamServiceHost), common.GetStringConfig(kfamServicePort))
	}
	glog.Infof("Client manager initialized successfully")
}

func (c *ClientManager) Close() {
	c.db.Close()
}

func initDBClient(initConnectionTimeout time.Duration) *storage.DB {
	driverName := common.GetStringConfig("DBConfig.DriverName")
	var arg string

	switch driverName {
	case "mysql":
		arg = initMysql(driverName, initConnectionTimeout)
	default:
		glog.Fatalf("Driver %v is not supported", driverName)
	}

	// db is safe for concurrent use by multiple goroutines
	// and maintains its own pool of idle connections.
	db, err := gorm.Open(driverName, arg)
	util.TerminateIfError(err)

	// If pipeline_versions table is introduced into DB for the first time,
	// it needs initialization or data backfill.
	var tableNames []string
	var initializePipelineVersions = true
	db.Raw(`show tables`).Pluck("Tables_in_mlpipeline", &tableNames)
	for _, tableName := range tableNames {
		if tableName == "pipeline_versions" {
			initializePipelineVersions = false
			break
		}
	}

	// Create table
	response := db.AutoMigrate(
		&model.Experiment{},
		&model.Job{},
		&model.Pipeline{},
		&model.PipelineVersion{},
		&model.ResourceReference{},
		&model.RunDetail{},
		&model.RunMetric{},
		&model.DBStatus{},
		&model.DefaultExperiment{})

	if response.Error != nil {
		glog.Fatalf("Failed to initialize the databases.")
	}

	response = db.Model(&model.ResourceReference{}).ModifyColumn("Payload", "longtext not null")
	if response.Error != nil {
		glog.Fatalf("Failed to update the resource reference payload type. Error: %s", response.Error)
	}

	response = db.Model(&model.RunMetric{}).
		AddForeignKey("RunUUID", "run_details(UUID)", "CASCADE" /* onDelete */, "CASCADE" /* update */)
	if response.Error != nil {
		glog.Fatalf("Failed to create a foreign key for RunID in run_metrics table. Error: %s", response.Error)
	}
	response = db.Model(&model.PipelineVersion{}).
		AddForeignKey("PipelineId", "pipelines(UUID)", "CASCADE" /* onDelete */, "CASCADE" /* update */)
	if response.Error != nil {
		glog.Fatalf("Failed to create a foreign key for PipelineId in pipeline_versions table. Error: %s", response.Error)
	}

	// Data backfill for pipeline_versions if this is the first time for
	// pipeline_versions to enter mlpipeline DB.
	if initializePipelineVersions {
		initPipelineVersionsFromPipelines(db)
	}

	response = db.Model(&model.Pipeline{}).ModifyColumn("Description", "longtext not null")
	if response.Error != nil {
		glog.Fatalf("Failed to update pipeline description type. Error: %s", response.Error)
	}

	// If the old unique index idx_pipeline_version_uuid_name on pipeline_versions exists, remove it.
	rows, err := db.Raw(`show index from pipeline_versions where Key_name="idx_pipeline_version_uuid_name"`).Rows()
	if err != nil {
		glog.Fatalf("Failed to query pipeline_version table's indices. Error: %s", err)
	}
	if rows.Next() {
		db.Exec(`drop index idx_pipeline_version_uuid_name on pipeline_versions`)
	}
	rows.Close()

	return storage.NewDB(db.DB(), storage.NewMySQLDialect())
}

// Initialize the connection string for connecting to Mysql database
// Format would be something like root@tcp(ip:port)/dbname?charset=utf8&loc=Local&parseTime=True
func initMysql(driverName string, initConnectionTimeout time.Duration) string {
	mysqlConfig := client.CreateMySQLConfig(
		common.GetStringConfigWithDefault(mysqlUser, "root"),
		common.GetStringConfigWithDefault(mysqlPassword, ""),
		common.GetStringConfigWithDefault(mysqlServiceHost, "mysql"),
		common.GetStringConfigWithDefault(mysqlServicePort, "3306"),
		"",
		common.GetStringConfigWithDefault(mysqlGroupConcatMaxLen, "1024"),
	)

	var db *sql.DB
	var err error
	var operation = func() error {
		db, err = sql.Open(driverName, mysqlConfig.FormatDSN())
		if err != nil {
			return err
		}
		return nil
	}
	b := backoff.NewExponentialBackOff()
	b.MaxElapsedTime = initConnectionTimeout
	err = backoff.Retry(operation, b)

	defer db.Close()
	util.TerminateIfError(err)

	// Create database if not exist
	dbName := common.GetStringConfig(mysqlDBName)
	operation = func() error {
		_, err = db.Exec(fmt.Sprintf("CREATE DATABASE IF NOT EXISTS %s", dbName))
		if err != nil {
			return err
		}
		return nil
	}
	b = backoff.NewExponentialBackOff()
	b.MaxElapsedTime = initConnectionTimeout
	err = backoff.Retry(operation, b)

	util.TerminateIfError(err)
	mysqlConfig.DBName = dbName
	return mysqlConfig.FormatDSN()
}

func initMinioClient(initConnectionTimeout time.Duration) storage.ObjectStoreInterface {
	// Create minio client.
	minioServiceHost := common.GetStringConfigWithDefault(
		"ObjectStoreConfig.Host", os.Getenv(minioServiceHost))
	minioServicePort := common.GetStringConfigWithDefault(
		"ObjectStoreConfig.Port", os.Getenv(minioServicePort))
	accessKey := common.GetStringConfig("ObjectStoreConfig.AccessKey")
	secretKey := common.GetStringConfig("ObjectStoreConfig.SecretAccessKey")
	bucketName := common.GetStringConfig("ObjectStoreConfig.BucketName")
	disableMultipart := common.GetBoolConfigWithDefault("ObjectStoreConfig.Multipart.Disable", true)

	minioClient := client.CreateMinioClientOrFatal(minioServiceHost, minioServicePort, accessKey,
		secretKey, initConnectionTimeout)
	createMinioBucket(minioClient, bucketName)

	return storage.NewMinioObjectStore(&storage.MinioClient{Client: minioClient}, bucketName, disableMultipart)
}

func createMinioBucket(minioClient *minio.Client, bucketName string) {
	// Create bucket if it does not exist
	err := minioClient.MakeBucket(bucketName, "")
	if err != nil {
		// Check to see if we already own this bucket.
		exists, err := minioClient.BucketExists(bucketName)
		if err == nil && exists {
			glog.Infof("We already own %s\n", bucketName)
		} else {
			glog.Fatalf("Failed to create Minio bucket. Error: %v", err)
		}
	}
	glog.Infof("Successfully created bucket %s\n", bucketName)
}

// newClientManager creates and Init a new instance of ClientManager
func newClientManager() ClientManager {
	clientManager := ClientManager{}
	clientManager.init()

	return clientManager
}

// Data migration in 2 steps to introduce pipeline_versions table. This
// migration shall be called only once when pipeline_versions table is created
// for the first time in DB.
func initPipelineVersionsFromPipelines(db *gorm.DB) {
	tx := db.Begin()

	// Step 1: duplicate pipelines to pipeline versions.
	// The pipeline versions created here are not through KFP pipeine version
	// API, and are only for the legacy pipelines that are created
	// before pipeline version API is introduced.
	// For those legacy pipelines, who don't have versions before, we create one
	// implicit version for each of them. Given a legacy pipeline, the implicit
	// version created here is assigned an ID the same as the pipeline ID. This
	// way we don't need to move the minio file of pipeline package around,
	// since the minio file's path is based on the pipeline ID (and now on the
	// implicit version ID too). Meanwhile, IDs are required to be unique inside
	// the same resource type, so pipeline and pipeline version as two different
	// resources useing the same ID is OK.
	// On the other hand, pipeline and its pipeline versions created after
	// pipeline version API is introduced will have different Ids; and the minio
	// file will be put directly into the directories for pipeline versions.
	tx.Exec(`INSERT INTO
	pipeline_versions (UUID, Name, CreatedAtInSec, Parameters, Status, PipelineId)
	SELECT UUID, Name, CreatedAtInSec, Parameters, Status, UUID FROM pipelines;`)

	// Step 2: modifiy pipelines table after pipeline_versions are populated.
	tx.Exec("update pipelines set DefaultVersionId=UUID;")

	tx.Commit()
}
