#!/bin/bash
minio_address=$1
minio_admin=$2
minio_password=$3
minio_bucket=$4
adaptor_task=$5
env_task=$6
minio_download_path=$7
logs=/data/logs
echo 'start pull minio tasks' > $logs/minio_info.log

python /data/bin/minio_script.py "$minio_address" "$minio_admin" "$minio_password" "$minio_bucket" "$adaptor_task" "$env_task" "$minio_download_path" > $logs/minio_info.log 2>&1 &
echo $?