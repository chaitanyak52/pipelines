#!/bin/bash -e
image_name=alejacma/databricks_submit_run # Specify the image name here
image_tag="v0.1"
full_image_name=${image_name}:${image_tag}

cd "$(dirname "$0")" 
docker build -t "${full_image_name}" .
docker push "$full_image_name"

# Output the strict image name (which contains the sha256 image digest)
strict_image_name=$(docker inspect --format="{{index .RepoDigests 0}}" "${full_image_name}")
echo $strict_image_name

# Replace the image name in the component definition with the strict image name
# If you modify component.yaml, ensure the line number used in sed remains the same
sed -i "12s,.*,    image: $strict_image_name," component.yaml

# Don't forget to make the script executable with chmod +x build_image.sh
