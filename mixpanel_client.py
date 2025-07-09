import requests
import os
from datetime import datetime, timedelta
import base64
import json
from typing import Dict, List, Any

class MixpanelClient:
    def __init__(self, project_id: str, service_account_username: str, service_account_secret: str):
        self.project_id = project_id
        self.service_account_username = service_account_username
        self.service_account_secret = service_account_secret
        self.base_url = "https://mixpanel.com/api/2.0"
        
    def _get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for Mixpanel API using service account"""
        auth_string = f"{self.service_account_username}:{self.service_account_secret}"
        encoded_auth = base64.b64encode(auth_string.encode()).decode()
        return {
            "Authorization": f"Basic {encoded_auth}",
            "Content-Type": "application/json"
        }
    
    async def get_daily_active_users(self, days: int = 7) -> int:
        """Get daily active users for the last N days"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            params = {
                "event": ["$identify", "$signup", "track"],  # Common events for DAU
                "from_date": start_date.strftime("%Y-%m-%d"),
                "to_date": end_date.strftime("%Y-%m-%d"),
                "unit": "day"
            }
            
            response = requests.get(
                f"{self.base_url}/insights",
                params=params,
                headers=self._get_auth_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                # Return the latest day's count or sum if multiple events
                return data.get("data", {}).get("values", {}).get("All Events", [0])[-1]
            else:
                return 0
        except Exception as e:
            print(f"Error fetching DAU: {e}")
            return 0
    
    async def get_total_events(self, days: int = 1) -> int:
        """Get total events for the last N days"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            params = {
                "from_date": start_date.strftime("%Y-%m-%d"),
                "to_date": end_date.strftime("%Y-%m-%d"),
                "unit": "day"
            }
            
            response = requests.get(
                f"{self.base_url}/events",
                params=params,
                headers=self._get_auth_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                total = sum(data.get("data", {}).values())
                return total
            else:
                return 0
        except Exception as e:
            print(f"Error fetching total events: {e}")
            return 0
    
    async def get_custom_metric(self, event_name: str, days: int = 7) -> int:
        """Get count for a specific event over the last N days"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            params = {
                "event": [event_name],
                "from_date": start_date.strftime("%Y-%m-%d"),
                "to_date": end_date.strftime("%Y-%m-%d"),
                "unit": "day"
            }
            
            response = requests.get(
                f"{self.base_url}/insights",
                params=params,
                headers=self._get_auth_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                return sum(data.get("data", {}).get("values", {}).get(event_name, []))
            else:
                return 0
        except Exception as e:
            print(f"Error fetching custom metric {event_name}: {e}")
            return 0
    
    async def get_pipeline_runs(self, days: int = 7) -> int:
        """Get pipeline runs from the specific report"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Use the specific event name from your pipeline runs report
            params = {
                "event": ["pipeline_run_completed", "pipeline_run_started"],  # Common pipeline events
                "from_date": start_date.strftime("%Y-%m-%d"),
                "to_date": end_date.strftime("%Y-%m-%d"),
                "unit": "day"
            }
            
            response = requests.get(
                f"{self.base_url}/insights",
                params=params,
                headers=self._get_auth_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                # Sum all pipeline-related events
                total_runs = 0
                for event_name in ["pipeline_run_completed", "pipeline_run_started"]:
                    event_data = data.get("data", {}).get("values", {}).get(event_name, [])
                    total_runs += sum(event_data)
                return total_runs
            else:
                print(f"Error response: {response.status_code} - {response.text}")
                return 0
        except Exception as e:
            print(f"Error fetching pipeline runs: {e}")
            return 0