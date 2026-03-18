FROM python:3.14-alpine

RUN ["mkdir", "/homeassistant-dsl-watchdog"]
WORKDIR /homeassistant-dsl-watchdog
COPY ./source .
RUN ["python3", "-m", "pip", "install", "-r", "requirements.txt"]

ENTRYPOINT ["./entrypoint.sh"]