FROM python:3.13-rc-alpine3.18

RUN ["mkdir", "/homeassistant-dsl-watchdog"]
RUN ["python3", "-m", "pip", "install", "requests", "pythonping", "chardet"]
WORKDIR /homeassistant-dsl-watchdog
COPY ./source .
RUN rm -rf .venv

ENTRYPOINT ["./entrypoint.sh"]