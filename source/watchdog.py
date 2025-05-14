import logging, os, signal, sys, time, requests, threading
from pythonping import ping
from datetime import datetime


PING_TARGET     = os.environ.get("WATCHDOG_PING_TARGET", "1.1.1.1") # The target to run ping against.
PING_COUNT      = 1                                                 # How many request should pythonping make?
LOGLEVEL        = os.environ.get("WATCHDOG_LOGLEVEL", "INFO")       # Log level severity to log.
INTERVAL        = int(os.environ.get("WATCHDOG_INTERVAL", 30))      # How long to wait between runs of this watchdog.
FORCE_INTERVAL  = os.environ.get("WATCHDOG_FORCE_INTERVAL", False)  # Ingore interval warning.
SWITCH_TOGGLE_INTERVAL = 10                                         # Time to wait between turning the plug off and back on again.
COOLDOWN        = int(os.environ.get("WATCHDOG_COOLDOWN", 300))     # Time to wait with the next loop run after running the automation.
HA_INSTANCE     = os.environ.get("WATCHDOG_HA_INSTANCE")            # Base-url of your Homeassistant instace, e.g. https://homeassistant.my-domain.com
HA_TOKEN        = os.environ.get("WATCHDOG_HA_TOKEN")               # long-lived access token from your Homeassistant instance.
HA_AUTOMATION_ID= os.environ.get("WATCHDOG_HA_AUTOMATION_ID")       # The id of the automation, that turns the switch off and on again.
ERROR_THRESHOLD = int(os.environ.get("WATCHDOG_ERROR_THRESHOLD", 1))# How many times the ping command need to fail, before be want to trigger the automation.


logging.basicConfig(format='%(asctime)s %(levelname)s\t%(message)s', encoding='utf-8')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
logging.getLogger().setLevel(LOGLEVEL)

def signal_handler(sig, frame):
  logging.info("Recevied signal " + str((signal.Signals(sig).name)) + ". Shutting down.")
  sys.exit(0)

def multilineLogging(message, level: int = logging.DEBUG):
  logger = logging.getLogger()
  for line in str(message).splitlines():
    if line.strip():  # Log only non-empty lines
      logger.log(level, line)
    else:
      logger.log(level, '')  # Maintain blank lines with proper prefix

def checkSettings():
  error = False
  if (PING_TARGET is None):
    logging.critical("WATCHDOG_PING_TARGET is not set. This is required. Exiting.")
    error = True
  if (HA_INSTANCE is None):
    logging.critical("WATCHDOG_HA_INSTANCE is not set. This is required. Exiting.")
    error = True
  if (HA_TOKEN is None):
    logging.critical("WATCHDOG_HA_TOKEN is not set. This is required. Exiting.")
  if (HA_AUTOMATION_ID is None):
    logging.critical("WATCHDOG_HA_AUTOMATION_ID is not set. This is required. Exiting.")
    error = True
  if (INTERVAL < 10 and FORCE_INTERVAL == False):
    logging.info("It's not recommended to set WATCHDOG_INTERVAL to a value less than 10. Your value is %s. Default value is 10.", INTERVAL)
    logging.info("Set WATCHDOG_FORCE_INTERVAL = True to ignore this warning.")
    error = True
  if error is True:
      return 1
  else:
    return 0
  
def checkHaConnection(haInstance, haToken):
  header = {"Authorization": f"Bearer {haToken}"}
  r = requests.get(haInstance, headers=header)
  return r.status_code

def pingTarget(target, count):
  response = ping(target, count=count, verbose=False)
  return response

def haTriggerAutomation(haInstance, haToken, automationId):
  header = {"Authorization": f"Bearer {haToken}",
            "Content-Type": "application/json"}
  object = {'entity_id': f'{automationId}'}
  url = haInstance+"/api/services/automation/trigger"
  requests.post(url, json=object, headers=header)

def wrapperHaTriggerAutomation():
  haTriggerAutomation(HA_INSTANCE, HA_TOKEN, HA_AUTOMATION_ID)


def main():
  logging.info("Running with this configuration:")
  logging.info("LOGLEVEL:\t%s", LOGLEVEL)
  logging.debug("HA_INSTANCE:\t%s", HA_INSTANCE)
  logging.debug("HA_TOKEN:\t%s", HA_TOKEN[:4] + "... (truncated)")
  logging.debug("HA_SWITCH_ENTITY_ID:\t%s", HA_AUTOMATION_ID)
  logging.debug("PING_TARGET:\t%s", PING_TARGET)
  logging.debug("PING_COUNT:\t%s", PING_COUNT)
  logging.debug("INTERVAL:\t%s", INTERVAL)
  logging.debug("COOLDOWN:\t%s", COOLDOWN)
  logging.debug("FORCE_INTERVAL:\t%s", FORCE_INTERVAL)
  logging.debug("ERROR_THRESHOLD:\t%s", ERROR_THRESHOLD)
  errorCount = 0

  if (checkSettings() != 0):
    logging.error("Failed settings check. Exit.")
    sys.exit(1)

  if  checkHaConnection(HA_INSTANCE, HA_TOKEN) != 200:
    logging.error("Error reaching "+HA_INSTANCE+". Exiting.")
    sys.exit(2)

  while(True):
    logging.info("Starting watchdog run.")
    f = open("./lastRun.epoch", "w")     # Relevant for health.sh / health-compose.sh
    f.write(str(round(datetime.now().timestamp())))
    f.close()

    response = pingTarget(PING_TARGET, PING_COUNT)
    replys = [resp for resp in response if "Reply from "+PING_TARGET in str(response)]

    if len(replys) == 1:
      logging.debug("Got healthy response from target. Resetting errorCount.")
      multilineLogging(response, logging.DEBUG)
      errorCount = 0  # reset errorCount
    elif len(replys) == 0:
      logging.error("Can't reach "+PING_TARGET)
      errorCount += 1 # increase errorCount

    if errorCount >= ERROR_THRESHOLD:
      logging.error("Could not reach "+PING_TARGET+" for "+ f'{errorCount}' +" tries.")
      logging.error("Triggering automation "+HA_AUTOMATION_ID)
      threading.Thread(target=wrapperHaTriggerAutomation, daemon=True).start()
      errorCount = 0  # reset errorCount
      logging.info("Sleeping for "+ f'{COOLDOWN}' +"s before starting next watchdog run.")
      time.sleep(COOLDOWN)
    else:
      logging.debug("Threshold not reached. Continue.")
      logging.debug("errorCount: %s", errorCount)

    
    logging.info("Nothing to do. Sleeping for %ss.", INTERVAL)
    time.sleep(INTERVAL)




if __name__ == "__main__":
  signal.signal(signal.SIGINT, signal_handler)
  signal.signal(signal.SIGHUP, signal_handler)
  signal.signal(signal.SIGTERM, signal_handler)

  main()