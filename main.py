from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv
from mixpanel_client import MixpanelClient

load_dotenv()

app = FastAPI(title="ZenML LaMetric App")

# Initialize Mixpanel client
mixpanel_client = MixpanelClient(
    project_id=os.getenv("MIXPANEL_PROJECT_ID"),
    service_account_username=os.getenv("MIXPANEL_SERVICE_ACCOUNT_USERNAME"),
    service_account_secret=os.getenv("MIXPANEL_SERVICE_ACCOUNT_SECRET")
)

class LaMetricFrame(BaseModel):
    text: str
    icon: Optional[int] = None  # LaMetric icon ID (number) or null

class LaMetricResponse(BaseModel):
    frames: List[LaMetricFrame]

@app.get("/")
async def root():
    return {"message": "ZenML LaMetric App"}

@app.get("/debug")
async def debug():
    """Debug endpoint to test Mixpanel connectivity"""
    if not mixpanel_client.service_account_username or not mixpanel_client.service_account_secret:
        return {"error": "Service account credentials not configured"}
    
    try:
        await mixpanel_client._test_api_connectivity()
        return {"message": "Check logs for API test results"}
    except Exception as e:
        return {"error": str(e)}

@app.get("/metrics", response_model=LaMetricResponse)
async def get_metrics():
    """
    LaMetric polling endpoint that returns metrics in the required format
    """
    try:
        # Get metrics from Mixpanel
        metrics = await get_mixpanel_metrics()
        
        # Format for LaMetric
        frames = []
        for metric in metrics:
            frame = LaMetricFrame(
                text=f"{metric['name']}: {metric['value']}",
                icon=metric.get('icon')  # Will be None if not provided
            )
            frames.append(frame)
        
        return LaMetricResponse(frames=frames)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def get_mixpanel_metrics():
    """
    Fetch metrics from Mixpanel API
    """
    if not mixpanel_client.project_id or not mixpanel_client.service_account_username or not mixpanel_client.service_account_secret:
        # Return mock data if credentials not configured
        return [
            {"name": "Active Users", "value": "123"},
            {"name": "Events Today", "value": "456"}
        ]
    
    try:
        # Get actual metrics from Mixpanel
        pipeline_runs = await mixpanel_client.get_pipeline_runs(days=7)
        pipeline_runs_today = await mixpanel_client.get_pipeline_runs(days=1)
        
        return [
            {"name": "Pipeline Runs (7d)", "value": str(pipeline_runs)},
            {"name": "Pipeline Runs Today", "value": str(pipeline_runs_today)}
        ]
    except Exception as e:
        print(f"Error fetching Mixpanel metrics: {e}")
        # Return fallback data on error
        return [
            {"name": "Error", "value": "N/A"}
        ]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)