import pytz
import pandas as pd
from datetime import datetime, timedelta, time
import uuid
import csv
# Database connection setup
import mysql.connector

DEFAULT_TIMEZONE = 'America/Chicago'

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="1234",
    database="store_monitoring"
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
    cursor.execute("SELECT * FROM store_status limit 4000")
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

def get_store_timezone(store_id, timezones):
    """Get timezone for a store with default handling."""
    timezone_data = timezones[timezones['store_id'] == store_id]
    if timezone_data.empty:
        print(f"No timezone found for store {store_id}. Using default: {DEFAULT_TIMEZONE}")
        return DEFAULT_TIMEZONE
    return timezone_data['timezone_str'].iloc[0]

def get_default_business_hours():
    """Returns default business hours (24/7 for all days)."""
    default_hours = []
    for day in range(7):
        default_hours.append({
            'day_of_week': day,
            'start_time_local': time(0, 0),  # 12 AM
            'end_time_local': time(23, 59, 59)    # 11:59:59 PM
        })
    return pd.DataFrame(default_hours)

def calculate_uptime_downtime(store_id, store_status, timezone, business_hours, current_time):
    """Calculates uptime and downtime for a given store."""
    if store_status.empty:
        print(f"Warning: No status data found for store {store_id}")
        return {
            'uptime_last_hour': 0,
            'uptime_last_day': 0,
            'uptime_last_week': 0,
            'downtime_last_hour': 0,
            'downtime_last_day': 0,
            'downtime_last_week': 0
        }

    df = store_status.copy()
    
    # Convert timestamps to local time
    try:
        tz = pytz.timezone(timezone)
        df.loc[:, 'timestamp_local'] = df['timestamp_utc'].dt.tz_convert(tz)
    except pytz.exceptions.UnknownTimeZoneError:
        print(f"Warning: Invalid timezone {timezone} for store {store_id}. Using {DEFAULT_TIMEZONE}.")
        tz = pytz.timezone(DEFAULT_TIMEZONE)
        df.loc[:, 'timestamp_local'] = df['timestamp_utc'].dt.tz_convert(tz)
    
    # Make sure current_time is timezone-aware
    if not current_time.tzinfo:
        current_time = pytz.utc.localize(current_time)
    
    # Use default business hours if none are provided
    if business_hours.empty:
        business_hours = get_default_business_hours()
        print(f"Using default business hours for store {store_id}")
    
    # Filter by business hours
    filtered_status = filter_business_hours(df, business_hours)
    
    # Define timeframes in UTC
    last_hour = current_time - timedelta(hours=1)
    last_day = current_time - timedelta(days=1)
    last_week = current_time - timedelta(weeks=1)
    
    # Calculate uptime and downtime
    results = {}
    for timeframe, start_time in [("last_hour", last_hour), ("last_day", last_day), ("last_week", last_week)]:
        uptime, downtime = calculate_time(filtered_status, start_time, current_time)
        results[f"uptime_{timeframe}"] = uptime
        results[f"downtime_{timeframe}"] = downtime
    
    return results

def filter_business_hours(store_status, business_hours):
    """Filters status data to include only intervals within business hours."""
    filtered = []
    
    for _, row in store_status.iterrows():
        local_time = row['timestamp_local']
        day_of_week = local_time.weekday()
        
        bh = business_hours[business_hours['day_of_week'] == day_of_week]
        
        if not bh.empty:
            start_time = bh['start_time_local'].iloc[0]
            end_time = bh['end_time_local'].iloc[0]
            current_time = local_time.time()
            
            if start_time <= current_time <= end_time:
                filtered.append(row)
    
    return pd.DataFrame(filtered) if filtered else pd.DataFrame(columns=store_status.columns)

def calculate_time(filtered_status, start_time, end_time):
    """Calculates uptime and downtime within the specified timeframe."""
    if filtered_status.empty:
        return 0, 0
    
    # Ensure timestamps are in UTC for comparison
    filtered_status = filtered_status.copy()
    start_time = start_time.astimezone(pytz.UTC)
    end_time = end_time.astimezone(pytz.UTC)
    
    uptime, downtime = 0, 0
    previous_time = start_time
    last_status = 'inactive'  # Default status
    
    for _, row in filtered_status.iterrows():
        current_time = row['timestamp_utc']
        if current_time > end_time:
            break
            
        if current_time >= start_time:
            interval = (current_time - previous_time).total_seconds()
            if row['status'] == 'active':
                uptime += interval
            else:
                downtime += interval
            previous_time = current_time
            last_status = row['status']
    
    # Add last interval
    if previous_time < end_time:
        last_interval = (end_time - previous_time).total_seconds()
        if last_status == 'active':
            uptime += last_interval
        else:
            downtime += last_interval
    
    return round(uptime / 60, 2), round(downtime / 60, 2)  # Return minutes

def generate_report():
    """Processes all stores and generates a report."""
    store_status, timezones, business_hours = fetch_data()
    
    if store_status.empty:
        raise ValueError("No store status data available")
        
    current_time = store_status['timestamp_utc'].max()
    report_id = str(uuid.uuid4())
    results = []

    # Print some debug information
    print(f"Total number of stores in status data: {len(store_status['store_id'].unique())}")
    print(f"Total number of stores in timezone data: {len(timezones['store_id'].unique())}")
    print(f"Total number of stores in business hours data: {len(business_hours['store_id'].unique())}")

    for store_id in store_status['store_id'].unique():
        store_timezone = get_store_timezone(store_id, timezones)
        store_hours = business_hours[business_hours['store_id'] == store_id]
        store_data = store_status[store_status['store_id'] == store_id]
        
        try:
            metrics = calculate_uptime_downtime(store_id, store_data, store_timezone, store_hours, current_time)
            results.append({"store_id": store_id, **metrics})
        except Exception as e:
            print(f"Error processing store {store_id}: {str(e)}")
            # Add default values for this store
            results.append({
                "store_id": store_id,
                "uptime_last_hour": 0,
                "uptime_last_day": 0,
                "uptime_last_week": 0,
                "downtime_last_hour": 0,
                "downtime_last_day": 0,
                "downtime_last_week": 0
            })
    
    # Save to CSV
    csv_filename = f"report_{report_id}.csv"
    with open(csv_filename, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
    
    return report_id, csv_filename

def generate_report_df():
    """Processes all stores and generates a report as a DataFrame."""
    store_status, timezones, business_hours = fetch_data()
    
    if store_status.empty:
        raise ValueError("No store status data available")
        
    current_time = store_status['timestamp_utc'].max()
    results = []

    # Print some debug information
    print(f"Total number of stores in status data: {len(store_status['store_id'].unique())}")
    print(f"Total number of stores in timezone data: {len(timezones['store_id'].unique())}")
    print(f"Total number of stores in business hours data: {len(business_hours['store_id'].unique())}")

    for store_id in store_status['store_id'].unique():
        store_timezone = get_store_timezone(store_id, timezones)
        store_hours = business_hours[business_hours['store_id'] == store_id]
        store_data = store_status[store_status['store_id'] == store_id]
        
        try:
            metrics = calculate_uptime_downtime(store_id, store_data, store_timezone, store_hours, current_time)
            results.append({"store_id": store_id, **metrics})
        except Exception as e:
            print(f"Error processing store {store_id}: {str(e)}")
            # Add default values for this store
            results.append({
                "store_id": store_id,
                "uptime_last_hour": 0,
                "uptime_last_day": 0,
                "uptime_last_week": 0,
                "downtime_last_hour": 0,
                "downtime_last_day": 0,
                "downtime_last_week": 0
            })
    
    return pd.DataFrame(results)


if __name__ == "__main__":
    try:
        report_id, csv_file = generate_report()
        print(f"Report generated successfully!")
        print(f"Report ID: {report_id}")
        print(f"File: {csv_file}")
    except Exception as e:
        print(f"Error generating report: {str(e)}")
        exit(1)