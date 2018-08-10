#!/bin/bash

if [ !  -d /var/log/supervisord ];then
    mkdir /var/log/supervisord
fi


if [ ! "$(which supervisord)" ];then
    echo "install supervisord ..."
    pip3 install -U git+https://github.com/Supervisor/supervisor.git 1>/dev/null 2>/dev/null;
    echo -n " ok"
fi

if [ ! "$(ps aux | grep supervisord | grep -v grep | xargs )" ];then
    echo "[+] Startup supervisord"
    supervisord -c ~/.config/SwordNode/supervisord.conf
    if [ $? -eq 0 ];then 
        echo -n " successful"
    else
        echo -n " failed"
    fi
fi

start() {
    supervisorctl start x-neid
    echo "Start Server "
}

stop() {
    supervisorctl stop x-neid
}

restart() {
    supervisorctl restart x-neid   
}

upgrade() {
    echo "[+] upgrade ..."
    pip3 install -U git+https://github.com/Qingluan/SwordNode.git 1>/dev/null 2>/dev/null;
    echo -n " ok"
}

if [[ $1 == "start" ]];then
    start
elif [[ $1 == "stop" ]];then
    stop
elif [[ $1 == "restart" ]];then
    restart
elif [[ $1 == "upgrade" ]];then
    upgrade
fi
