import requests
import os
from datetime import datetime, timedelta
import base64
import json
import time
from typing import Dict, List, Any

class MixpanelClient:
    def __init__(self, project_id: str, service_account_username: str, service_account_secret: str):
        self.project_id = project_id
        self.service_account_username = service_account_username
        self.service_account_secret = service_account_secret
        self.base_url = "https://eu.mixpanel.com/api/2.0"
        self._cache = {}
        self._cache_duration = 72  # 1.2 minutes in seconds
        
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
                "unit": "day",
                "project_id": self.project_id
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
                "unit": "day",
                "project_id": self.project_id
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
                "unit": "day",
                "project_id": self.project_id
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
    
    async def get_all_time_runs(self) -> int:
        """Get today's pipeline runs count with caching"""
        cache_key = "today_runs"
        current_time = time.time()
        
        # Check cache first
        if cache_key in self._cache:
            cached_data, cached_time = self._cache[cache_key]
            if current_time - cached_time < self._cache_duration:
                return cached_data
        
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            params = {
                "event": json.dumps(["Pipeline run ended"]),
                "from_date": today,
                "to_date": today,
                "unit": "day",
                "project_id": self.project_id
            }
            
            response = requests.get(
                f"{self.base_url}/events",
                params=params,
                headers=self._get_auth_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                # Get today's count
                event_data = data.get("data", {}).get("values", {}).get("Pipeline run ended", {})
                if isinstance(event_data, dict):
                    result = event_data.get(today, 0)
                    # Cache the result
                    self._cache[cache_key] = (result, current_time)
                    return result
                return 0
            else:
                print(f"Failed to get today's runs: {response.status_code}")
                print(f"Response content: {response.text}")
                return 0
                
        except Exception as e:
            print(f"Error fetching today's runs: {e}")
            return 0
    
    
