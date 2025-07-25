import os
import json
from datetime import datetime, timedelta

from flask import Flask, render_template
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pytz

app = Flask(__name__)

CACHE_FILE = os.path.join(os.path.dirname(__file__), '..', 'cache', 'meals.json')
CALENDAR_ID = os.getenv('GOOGLE_CALENDAR_ID')
CREDENTIALS_FILE = os.getenv('GOOGLE_CREDENTIALS_JSON')


class MealFetcher:
    def __init__(self, calendar_id, credentials_file):
        self.calendar_id = calendar_id
        self.credentials_file = credentials_file
        self.creds = None
        if credentials_file and os.path.exists(credentials_file):
            self.creds = service_account.Credentials.from_service_account_file(
                credentials_file,
                scopes=['https://www.googleapis.com/auth/calendar.readonly'],
            )

    def fetch_meals(self):
        if not self.creds or not self.calendar_id:
            return None
        service = build('calendar', 'v3', credentials=self.creds)
        now = datetime.now().date()
        time_min = (now - timedelta(days=7)).isoformat() + 'T00:00:00Z'
        time_max = (now + timedelta(days=7)).isoformat() + 'T23:59:59Z'
        try:
            events_result = (
                service.events()
                .list(
                    calendarId=self.calendar_id,
                    timeMin=time_min,
                    timeMax=time_max,
                    singleEvents=True,
                    orderBy='startTime',
                )
                .execute()
            )
            events = events_result.get('items', [])
            meals = {}
            tzinfo = pytz.utc
            for event in events:
                start = event.get('start', {}).get('date') or event.get('start', {}).get('dateTime')
                if not start:
                    continue
                date = datetime.fromisoformat(start).astimezone(tzinfo).date().isoformat()
                meals[date] = event.get('summary', 'No dinner planned')
            return meals
        except HttpError:
            return None


def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE) as f:
            return json.load(f)
    return {}


def save_cache(data):
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    with open(CACHE_FILE, 'w') as f:
        json.dump(data, f)


@app.route('/')
def index():
    fetcher = MealFetcher(CALENDAR_ID, CREDENTIALS_FILE)
    meals = fetcher.fetch_meals()
    if meals is None:
        meals = load_cache()
    else:
        save_cache(meals)

    today = datetime.now().date()
    dates = [(today - timedelta(days=i)) for i in range(7, 0, -1)]
    dates.append(today)
    dates.extend([(today + timedelta(days=i)) for i in range(1, 8)])

    meal_plan = []
    for d in dates:
        iso = d.isoformat()
        meal = meals.get(iso, 'No dinner planned')
        meal_plan.append({'date': d, 'meal': meal, 'today': d == today})

    return render_template('index.html', meal_plan=meal_plan)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
