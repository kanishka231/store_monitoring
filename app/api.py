import pandas as pd
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
import uuid
from datetime import datetime
import os
from typing import Dict, Optional
import asyncio
from fastapi.middleware.cors import CORSMiddleware
# Import your existing code
from app.main import generate_report_df

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Store report status and file paths
report_status: Dict[str, Dict] = {}
def save_report(report: pd.DataFrame, output_path: str):
    """Save the generated report to a CSV file."""
    try:
        report.to_csv(output_path, index=False)
        print(f"Report saved successfully to {output_path}")
    except Exception as e:
        print(f"Error saving report: {str(e)}")
        raise
async def generate_report_task(report_id: str):
    """Background task to generate report"""
    try:
        # Generate report using existing function
        report_df = generate_report_df()
        
        # Create reports directory if it doesn't exist
        os.makedirs('reports', exist_ok=True)
        
        # Save report to CSV
        output_path = f"reports/report_{report_id}.csv"
        save_report(report_df, output_path)
        
        # Update report status
        report_status[report_id]["status"] = "Complete"
        report_status[report_id]["file_path"] = output_path
        
    except Exception as e:
        report_status[report_id]["status"] = "Failed"
        report_status[report_id]["error"] = str(e)

@app.post("/trigger_report")
async def trigger_report(background_tasks: BackgroundTasks):
    """
    Trigger report generation
    Returns a report_id that can be used to fetch the report status and result
    """
    try:
        # Generate unique report ID
        report_id = str(uuid.uuid4())
        
        # Initialize report status
        report_status[report_id] = {
            "status": "Running",
            "timestamp": datetime.utcnow(),
            "file_path": None
        }
        
        # Trigger background task
        background_tasks.add_task(generate_report_task, report_id)
        
        return {"report_id": report_id}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get_report/{report_id}")
async def get_report(report_id: str):
    """
    Get report status and result
    If report is complete, returns the CSV file
    If report is running, returns status
    """
    try:
        # Check if report ID exists
        if report_id not in report_status:
            raise HTTPException(status_code=404, detail="Report ID not found")
            
        status = report_status[report_id]["status"]
        
        # If report is still running
        if status == "Running":
            return {"status": "Running"}
            
        # If report failed
        elif status == "Failed":
            error = report_status[report_id].get("error", "Unknown error")
            raise HTTPException(status_code=500, detail=f"Report generation failed: {error}")
            
        # If report is complete
        elif status == "Complete":
            file_path = report_status[report_id]["file_path"]
            if not os.path.exists(file_path):
                raise HTTPException(status_code=404, detail="Report file not found")
                
            return FileResponse(
                file_path,
                media_type="text/csv",
                filename=f"store_report_{report_id}.csv"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    
