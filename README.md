# Homeassistant-DSL-Watchdog
## Synopsis
Checks your Internet connection and sends out to homeassistant to trigger a automation, that shuts the router plug off and on again.

## Prerequisits
- Router plugged into a smart-plag that is setup with homeassistant
- Automation configured in homeassistant like in automation.example.yaml

## Configuration 

| Variable                  | Description | Default |
|---------------------------|-------------|---------|
| WATCHDOG_LOGLEVEL         | Python log level (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`) |  `INFO` |
| WATCHDOG_ERROR_THRESHOLD  | How many times the ping command need to fail, before triggering the automation. | 1 |
| WATCHDOG_INTERVAL         | How many seconds to wait between runs of this watchdog. | 30 |
| WATCHDOG_COOLDOWN         | How many seconds to wait before the next run of this watchdog after triggering the automation. | 300 |
| WATCHDOG_FORCE_INTERVAL   | Ingore the interval warning and force to use a value lower than recommended. | `False`|
| WATCHDOG_PING_TARGET      | The target to run ping against. | `1.1.1.1` |
| WATCHDOG_HA_AUTOMATION_ID | **Required** The id of the automation, that turns the switch off and on again. | `""` |
| WATCHDOG_HA_INSTANCE      | **Required** Base-url of your Homeassistant instace, e.g. https://homeassistant.my-domain.com | `""` |
| WATCHDOG_HA_TOKEN         | **Required** Long-lived access token from your Homeassistant instance. | `""` |

## Run
Fill a env-file with your details
```
vi .env
```

Run the container 
```
docker compose up -d
```

## Healthchecks
This image provides **two** healthchecks.  
- `health.sh` for all systems that can handle healthchecks sanely, like Kubernetes, Docker Swarm, etc.  
- `health-compose.sh` is intended for `docker compose`, which currently lacks handling of unhealthy containers. It kills the entrypoint-process once the built-in check fails **once**! This causes PID 1 to get terminated and the container stops.
Depending in the restart-policy (e.g. `restart: always`) the container gets restarted.  
Please be aware, that using `health-compose.sh` renders `healthcheck.retries` useless. PID 1 gets killed if the healthcheck fails once. 

# Build locally
```
cd source
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```