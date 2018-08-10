#!/bin/bash

start() {
    x-neid -p 60009 &
    echo "Sever start"
}

stop() {
    ps aux | grep x-neid | grep -v grep | awk '{ print $2 }' | xargs kill -9;
}


if [[ $1 == "start" ]];then
    start
else
    stop
fi

