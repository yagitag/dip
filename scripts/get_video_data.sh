#!/usr/bin/env bash

set -o nounset
set -o errexit
set -o pipefail

VIDEO_DATA_PATH=~/dip_data/video_data
FIELD=$1
shift

for field_data in "$@" ; do
  echo $field_data:
  LINES=$( fgrep -ni "$field_data" $VIDEO_DATA_PATH/$FIELD | sed 's/:.*//' )
  for line in $LINES ; do
    echo LINE:$line
    for field_location in $( ls $VIDEO_DATA_PATH/* | grep -v "^$FIELD$" ) ; do
        echo -e "\t$( basename $field_location):$( sed "$line!d" $field_location )"
    done
  done
done
