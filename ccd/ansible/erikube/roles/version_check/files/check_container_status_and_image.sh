#!/bin/bash
set -e
container=$1
image=$2
current_image=$(docker inspect --format='{{.Config.Image}}' $container)
if [[ "$container"x == x ]] || [[ "$image"x == x ]] || [[ "$current_image"x == x ]];then
  echo "[`basename $0`][`date -R`] Wrong parameter: container: $container, image: $image, current_image: $current_image" >&2
  exit 1
fi

if [[ "$current_image" != "$image" ]];then
  echo "[`basename $0`][`date -R`] The images are not matching current_image: $current_image != image: $image" >&2
  exit 1
fi

if [[ "$(docker inspect -f {{.State.Running}} $container)" != true ]];then
  echo "[`basename $0`][`date -R`] The container $container is not running" >&2
  exit 1
fi
