
# Store Monitoring System

## Overview

This project builds a system to monitor restaurant activity based on their operational status. The system processes data from CSV files and stores it in a MySQL database. It also provides a FastAPI-based backend that enables users to generate CSV reports about the uptime and downtime of stores based on their business hours.

## Features

- **Data Ingestion**: Reads and stores data from CSV files into a MySQL database.
- **Report Generation**: Generates reports based on store data and exports them to CSV files.
- **Background Tasks**: Uses FastAPI’s background tasks to generate reports asynchronously.
- **Report Status**: Polling mechanism to check the report generation status.

## Prerequisites

Before running the project, ensure you have the following installed:

- Python 3.7+ (recommended)
- MySQL
- FastAPI
- Uvicorn
- Other dependencies listed in `requirements.txt`

## Project Structure

```
store_monitoring/
├── src/
│   ├── database.py         # Handles MySQL database connection and table creation.
│   ├── ingest_data.py      # Reads CSV data and inserts it into the database.
│   └── __init__.py         # Marks src as a package.
│
├── data/
│   ├── store_status.csv    # Store activity status.
│   ├── menu_hours.csv      # Store business hours.
│   ├── timezones.csv       # Store timezone information.
│
├── app/
│   ├── __init__.py
│   ├── api.py              # Main FastAPI app and routes.
│   ├── generate_report.py  # Report generation logic.
│
├── reports/                # Folder to store generated CSV reports.
├── requirements.txt        # List of dependencies.
├── .env                    # Environment variables for database configuration.
└── README.md               # Project documentation.
```

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/store_monitoring.git
```

### 2. Install Dependencies
Navigate to the project folder and install the required dependencies using `pip`:
```bash
cd store_monitoring
pip install -r requirements.txt
```

### 3. Set Up the Database

Create a MySQL database and configure the connection in the `.env` file:
```
DB_HOST=your_host
DB_USER=your_user
DB_PASSWORD=your_password
DB_NAME=your_database
```

### 4. Prepare the Reports Directory
The reports will be stored in a folder named `reports` inside the project directory. If it doesn't exist, it will be created automatically during the first report generation.

## Running the Application

### Run the Backend Server
To start the FastAPI application locally, use the following command:
```bash
uvicorn app.api:app --reload
```
The application will be available at `http://127.0.0.1:8000`.

### Optional: Run with Multiple Workers
If you expect a high load or large dataset, you can increase the number of workers for better performance:
```bash
uvicorn app.api:app --reload --workers 4
```
This will run the server with 4 worker processes.

## API Endpoints

### 1. `/trigger_report` [POST]
Triggers the generation of a report.

#### Request:
No input parameters.

#### Response:
Returns a JSON object with the `report_id`.
```json
{
  "report_id": "unique_report_id"
}
```

### 2. `/get_report` [GET]
Allows users to retrieve the status of the report or the completed CSV file.

#### Request Parameters:
- `report_id`: The unique identifier for the report, returned from the `/trigger_report` endpoint.

#### Responses:
- **If the report is still being generated**:
  ```json
  {
    "status": "Running"
  }
  ```
- **If the report is completed**:
  Returns the CSV file.
- **If there is an error or failure**:
  ```json
  {
    "status": "Failed",
    "error": "Error message"
  }
  ```

## License

This project is licensed under the MIT License.

## Acknowledgments

- **FastAPI**: For building modern, high-performance APIs.
- **Uvicorn**: For serving the FastAPI application.
