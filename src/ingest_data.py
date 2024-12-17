import os
import pandas as pd
import mysql.connector
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Fetch MySQL credentials from environment variables
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')

# Connect to MySQL database
connection = mysql.connector.connect(
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME
)

cursor = connection.cursor()

# Define the path to your CSV files
BASE_PATH = "data"
STORE_STATUS_CSV = os.path.join(BASE_PATH, "store_status.csv")
BUSINESS_HOURS_CSV = os.path.join(BASE_PATH, "menu_hours.csv")
TIMEZONES_CSV = os.path.join(BASE_PATH, "timezones.csv")

# Load CSV files into Pandas DataFrames
store_status_df = pd.read_csv(STORE_STATUS_CSV)
business_hours_df = pd.read_csv(BUSINESS_HOURS_CSV)
timezones_df = pd.read_csv(TIMEZONES_CSV)

# Function to insert data into MySQL
def insert_data():
    # Insert store_status data
    for _, row in store_status_df.iterrows():
        cursor.execute("""
            INSERT INTO store_status (store_id, timestamp_utc, status)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE status=%s
        """, (row['store_id'], row['timestamp_utc'], row['status'], row['status']))

    # Insert business_hours data
    for _, row in business_hours_df.iterrows():
        cursor.execute("""
            INSERT INTO business_hours (store_id, day_of_week, start_time_local, end_time_local)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE start_time_local=%s, end_time_local=%s
        """, (row['store_id'], row['dayOfWeek'], row['start_time_local'], row['end_time_local'],
              row['start_time_local'], row['end_time_local']))

    # Insert timezones data
    for _, row in timezones_df.iterrows():
        cursor.execute("""
            INSERT INTO timezones (store_id, timezone_str)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE timezone_str=%s
        """, (row['store_id'], row['timezone_str'], row['timezone_str']))

    connection.commit()
    print("Data loaded successfully into MySQL!")

# Run the function to insert data
if __name__ == "__main__":
    insert_data()

# Close connection
def close_connection():
    cursor.close()
    connection.close()
