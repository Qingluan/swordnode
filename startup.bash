#!/bin/bash

if [ !  -d /var/log/supervisord ];then
    mkdir /var/log/supervisord
fi


if [ ! "$(which supervisord)" ];then
    echo "install supervisord ..."
    pip3 install -U git+https://github.com/Supervisor/supervisor.git 1>/dev/null 2>/dev/null;
    echo -n " ok"
fi

start() {
    supervisord -c ~/.config/SwordNode/supervisord.conf
    echo "Start Server "
}

stop() {
    supervisorctl stop x-neid
}

restart() {
    supervisorctl restart x-neid   
}

if [[ $1 == "start" ]];then
    start
else
    stop
fi
