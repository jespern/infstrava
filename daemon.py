import time
import toml
import requests

from datetime import datetime

from influxdb import InfluxDBClient
from stravalib.client import Client as StravaClient
from stravalib.exc import AccessUnauthorized

CONST_CFG_FN = 'config.toml'

def new_token(config):
    # Get a new access token
    refresh_resp = strava.refresh_access_token(
        client_id=config['client_id'],
        client_secret=config['client_secret'],
        refresh_token=refresh_token)

    if isinstance(refresh_resp, dict) and 'expires_at' in refresh_resp:
        return refresh_resp['access_token'], refresh_resp['refresh_token']
    else:
        raise Exception(f"Failed to obtain refresh token: {refresh_resp}")

if __name__ == '__main__':
    delay = 60
    config = {}

    with open(CONST_CFG_FN) as fp:
        config = toml.load(fp)
        delay = int(config['delay'])

    client = InfluxDBClient('172.16.1.56', 8086, 'username', 'password', 'telegraf')
    client.create_database('strava')

    access_token = config['access_token']
    refresh_token = config['refresh_token']

    while True:
        strava = StravaClient(access_token=access_token)

        now = datetime.utcnow()

        try:
            athlete = strava.get_athlete()
        except AccessUnauthorized:
            print("Failed to get token, attempting to get a new one.")
        else:
            rides = athlete.stats.all_ride_totals

            json_body = [
                {
                    "measurement": "athlete",
                    "tags": {
                        "athlete": athlete.username,
                    },
                    "time": now.strftime('%Y-%m-%dT%H:%M:%SZ'),
                    "fields": {
                        "duration": rides.moving_time.total_seconds(),
                        "distance": float(rides.distance),
                        "elevation": float(rides.elevation_gain),
                        "count": float(rides.count),
                    },
                }
            ]

            print(json_body)

            client.write_points(json_body)

            time.sleep(delay)

        access_token, refresh_token = new_token(config)

