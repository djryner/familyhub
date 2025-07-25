# Family Hub Meal Plan

This project displays a 15-day dinner plan pulled from a shared Google Calendar.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set environment variables for your Google Calendar:
   - `GOOGLE_CALENDAR_ID` – ID of the shared calendar.
   - `GOOGLE_CREDENTIALS_JSON` – path to a service account JSON credentials file.

3. Run the server:
   ```bash
   python -m app.app
   ```

The app will fetch meals for the past 7 days, today, and the next 7 days. If fetching fails, it will use cached data stored in `cache/meals.json`.
