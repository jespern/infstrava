FROM python:3.6-alpine

ADD requirements.txt .

RUN pip install -r requirements.txt

ADD daemon.py .
ADD config.toml .

ENTRYPOINT ["python3", "-u", "daemon.py"]