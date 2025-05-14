#!/bin/sh

export $(cat .env | xargs)

if [ -z $WATCHDOG_INTERVAL ]; then 
    WATCHDOG_INTERVAL=30
fi

SECONDS_SINCE_LAST_RUN=$(expr $(date +%s) - $(cat lastRun.epoch))
THRESHOLD=$(expr $WATCHDOG_INTERVAL \* 2)

if [ "$SECONDS_SINCE_LAST_RUN" -lt "$THRESHOLD" ]; then 
    exit 0; 
else
    exit 1;
fi