from datetime import time
import os
import mysql.connector
from dotenv import load_dotenv
import pandas as pd
# Load environment variables from .env file
load_dotenv()


db = mysql.connector.connect(
    host=os.getenv('DB_HOST'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    database=os.getenv('DB_NAME')
)

def convert_timedelta_to_time(td):
    """Convert timedelta to time object."""
    seconds = td.total_seconds()
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    return time(hours, minutes, seconds)

def fetch_data():
    """Fetches store data from the database."""
    cursor = db.cursor(dictionary=True)
    
    # Fetch store status data
    cursor.execute("SELECT * FROM store_status limit 10000000")
    store_status = pd.DataFrame(cursor.fetchall())
    if not store_status.empty:
        store_status['timestamp_utc'] = pd.to_datetime(store_status['timestamp_utc'].str.replace(' UTC', ''))
        store_status['timestamp_utc'] = store_status['timestamp_utc'].dt.tz_localize('UTC')
    
    # Fetch timezone data
    cursor.execute("SELECT * FROM timezones")
    timezones = pd.DataFrame(cursor.fetchall())
    
    # Fetch business hours
    cursor.execute("SELECT * FROM business_hours")
    business_hours = pd.DataFrame(cursor.fetchall())
    
    if not business_hours.empty:
        business_hours['start_time_local'] = business_hours['start_time_local'].apply(convert_timedelta_to_time)
        business_hours['end_time_local'] = business_hours['end_time_local'].apply(convert_timedelta_to_time)
    
    return store_status, timezones, business_hours

