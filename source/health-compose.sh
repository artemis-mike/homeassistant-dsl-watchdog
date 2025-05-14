#!/bin/sh

export $(cat .env | xargs)

if [ -z $WATCHDOG_COOLDOWN ]; then 
    WATCHDOG_COOLDOWN=300
fi

SECONDS_SINCE_LAST_RUN=$(expr $(date +%s) - $(cat lastRun.epoch))
THRESHOLD=$(expr $WATCHDOG_COOLDOWN \* 2)

if [ "$SECONDS_SINCE_LAST_RUN" -lt "$THRESHOLD" ]; then 
    exit 0; 
else
    kill 1;
fi