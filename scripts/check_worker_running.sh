#!/bin/bash

container_id=$(docker container list | grep "worker" | awk '{print$1}')

echo "container_id=$container_id"
if [ -z "$container_id" ]; 
then
	echo "worker is not running";
	docker container start worker
else 
	echo "worker is running"; 
fi
