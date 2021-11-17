#!/bin/sh

CONF=/etc/supervisor/supervisor.d/$1.conf

if [ ! -f $CONF ]; then
    echo "Configuration file not found: $CONF"
    echo ""
    echo "Available configurations: " $(ls $PWD/supervisor/)
    exit 1
fi

exec supervisord -c $CONF
