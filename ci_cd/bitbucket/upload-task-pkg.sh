#!/bin/bash

set -e

# Usage: upload-task-pkg.sh <api_basepath> <api_token> <workspace_id> <task_package_id> <bundle_filename>
#
# Example:
#   upload-task-pkg.sh \
#     "https://api.eu1.robocorp.com/robot-v2" \
#     "[redacted]" \
#     "d11caa0a-0cc2-4b2b-abe6-7df53213f3ac" \
#     "30202" \
#     "./robot.zip"
api_basepath=$1
api_token=$2
workspace_id=$3
task_package_id=$4
bundle_filename=$5

api_response=$(
  curl -s \
    --request GET \
    --url "${api_basepath}/workspaces/${workspace_id}/robots/${task_package_id}/file/uploadlink" \
    --header "Authorization: RC-WSKEY ${api_token}"
)

form_fields=$(echo "$api_response" | jq -r '.fields')

form_data_args=()
for key in $(echo "$form_fields" | jq -r 'keys | .[]'); do
  value=$(echo "$form_fields" | jq -r --arg k "$key" '.[$k]')
  form_data_args+=(--form "$key=$value")
done

upload_url=$(echo "$api_response" | jq -r '.url')

curl -v "${form_data_args[@]}" --form "file=@${bundle_filename}" "$upload_url"
