#!/bin/bash

start() {
    x-neid -p 60009 &
    echo "Sever start"
}

stop() {
        pid="$(ps aux | grep x-neid | grep -v grep | grep -v x-neid-server | awk '{ print $2 }'  | xargs)"
        if [[ $pid != "" ]];then
                echo "$(ps aux | grep x-neid | grep -v grep | grep -v x-neid-server )"
                echo "found pid : $pid"
                kill -9 $pid;
                echo "kill the x-neid"
        else
                echo "not start"
        fi

}


if [[ $1 == "start" ]];then
    start
else
    stop
fi
