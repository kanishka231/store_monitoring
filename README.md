# Store Monitoring System

This project builds a system to monitor restaurant activity based on their operational status. The system processes data from CSV files and stores it in a MySQL database. 

## Project Structure

```
store_monitoring/
│
├── src/
│   ├── database.py         # Handles MySQL database connection and table creation.
│   ├── ingest_data.py      # Reads CSV data and inserts it into the database.
│   └── __init__.py         # Marks src as a package.
│
├── data/
│   ├── store_status.csv    # Store activity status.
│   ├── business_hours.csv  # Store business hours.
│   ├── timezones.csv       # Store timezone information.
│
├── requirements.txt        # List of dependencies.
├── .env                    # Environment variables for database configuration.
└── README.md               # Project documentation.
```

## Progress So Far

### Features Implemented

1. **MySQL Database Integration**:
   - Created tables for `store_status`, `business_hours`, and `timezones`.
   - Used `VARCHAR` type for `store_id` to accommodate UUIDs.

2. **Data Ingestion**:
   - Read CSV files (`store_status.csv`, `business_hours.csv`, `timezones.csv`).
   - Inserted data into the MySQL database.

3. **Environment Management**:
   - Configured a virtual environment for dependency isolation.
   - Used `.env` file to store database credentials securely.

### How to Run

1. **Set up the Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Set up the Database**:
   - Ensure MySQL is installed and running.
   - Create a database named `store_monitoring`:
     ```sql
     CREATE DATABASE store_monitoring;
     ```

3. **Configure Environment Variables**:
   - Add your database credentials to the `.env` file:
     ```
     DB_USER=<your_db_user>
     DB_PASSWORD=<your_db_password>
     DB_HOST=localhost
     DB_PORT=3306
     DB_NAME=store_monitoring
     ```

4. **Create Database Tables**:
   Run the following command to create tables:
   ```bash
   python src/database.py
   ```

5. **Ingest Data from CSVs**:
   Run the following command to populate the database with CSV data:
   ```bash
   python src/ingest_data.py
   ```
