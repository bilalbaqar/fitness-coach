#!/usr/bin/env python3
"""
Test script for getCurrentMetrics endpoint
"""

import httpx
import json

async def test_get_current_metrics():
    """Test the getCurrentMetrics endpoint"""
    
    # Your Railway backend URL
    base_url = "https://fitness-coach-production.up.railway.app"
    
    # Test data
    test_data = {
        "user_id": None  # Will use demo user
    }
    
    # Headers with agent token
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer your-agent-token-change-in-production"  # Use your actual agent token
    }
    
    try:
        async with httpx.AsyncClient() as client:
            # Test the endpoint
            response = await client.post(
                f"{base_url}/tools/getCurrentMetrics",
                json=test_data,
                headers=headers
            )
            
            print(f"Status Code: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            
            if response.status_code == 200:
                print("✅ getCurrentMetrics endpoint working!")
            else:
                print("❌ getCurrentMetrics endpoint failed!")
                
    except Exception as e:
        print(f"Error testing endpoint: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_get_current_metrics())
