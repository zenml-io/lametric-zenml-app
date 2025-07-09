from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv
from mixpanel_client import MixpanelClient
from github_client import GitHubClient

load_dotenv()

app = FastAPI(title="ZenML LaMetric App")

# Initialize clients
mixpanel_client = MixpanelClient(
    project_id=os.getenv("MIXPANEL_PROJECT_ID"),
    service_account_username=os.getenv("MIXPANEL_SERVICE_ACCOUNT_USERNAME"),
    service_account_secret=os.getenv("MIXPANEL_SERVICE_ACCOUNT_SECRET")
)

github_client = GitHubClient(
    github_token=os.getenv("GITHUB_TOKEN")  # Optional - works without token but has lower rate limits
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
                icon=metric.get('icon')  # LaMetric icon ID number
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
            {"name": "Runs", "value": "2847", "icon": 2620},  # Gear/settings icon for pipeline runs
            {"name": "ZenML", "value": "3900", "icon": 2739}  # Star icon for GitHub stars
        ]
    
    try:
        # Get all-time runs count and GitHub stars
        all_time_runs = await mixpanel_client.get_all_time_runs()
        github_stars = await github_client.get_repo_stars("zenml-io", "zenml")
        
        return [
            {"name": "Runs", "value": str(all_time_runs), "icon": 2620},  # Gear/settings icon for pipeline runs
            {"name": "ZenML", "value": str(github_stars), "icon": 2739}  # Star icon for GitHub stars
        ]
    except Exception as e:
        print(f"Error fetching Mixpanel metrics: {e}")
        # Return fallback data on error
        return [
            {"name": "Runs", "value": "2847", "icon": 2620},  # Gear/settings icon for pipeline runs
            {"name": "ZenML", "value": "3900", "icon": 2739}  # Star icon for GitHub stars
        ]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)