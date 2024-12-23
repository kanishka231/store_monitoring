import os
from dotenv import load_dotenv
import mysql.connector

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

# Create tables for store_status, business_hours, and timezones
def create_tables():
    # Create store_status table with store_id as VARCHAR
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS store_status (
            store_id VARCHAR(255) NOT NULL,
            timestamp_utc VARCHAR(50) NOT NULL,
            status VARCHAR(10) NOT NULL,
            PRIMARY KEY (store_id, timestamp_utc)
        )
    """)

    # Create business_hours table with store_id as VARCHAR
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS business_hours (
            store_id VARCHAR(255) NOT NULL,
            day_of_week INT NOT NULL,
            start_time_local TIME NOT NULL,
            end_time_local TIME NOT NULL,
            PRIMARY KEY (store_id, day_of_week)
        )
    """)

    # Create timezones table with store_id as VARCHAR
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS timezones (
            store_id VARCHAR(255) NOT NULL,
            timezone_str VARCHAR(50) NOT NULL,
            PRIMARY KEY (store_id)
        )
    """)

    connection.commit()
    print("Tables created successfully!")

# Run the function to create tables
if __name__ == "__main__":
    create_tables()

# Close connection
def close_connection():
    cursor.close()
    connection.close()