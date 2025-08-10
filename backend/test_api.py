import httpx
import asyncio
from datetime import datetime

async def test_api():
    """Test the API endpoints"""
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient() as client:
        print("Testing API endpoints...")
        
        # Test root endpoint
        response = await client.get(f"{base_url}/")
        print(f"Root endpoint: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # Test dev login
        response = await client.post(f"{base_url}/dev/login")
        print(f"Dev login: {response.status_code}")
        if response.status_code == 200:
            token_data = response.json()
            token = token_data["access_token"]
            print(f"Got token: {token[:20]}...")
            print(f"Got token: {token}")
            
            # Test protected endpoints
            headers = {"Authorization": f"Bearer {token}"}
            
            # Test /api/me
            response = await client.get(f"{base_url}/api/me", headers=headers)
            print(f"/api/me: {response.status_code}")
            if response.status_code == 200:
                user_data = response.json()
                print(f"User: {user_data['name']}")
            
            # Test /api/readiness/today
            response = await client.get(f"{base_url}/api/readiness/today", headers=headers)
            print(f"/api/readiness/today: {response.status_code}")
            if response.status_code == 200:
                readiness_data = response.json()
                print(f"Readiness: {readiness_data['recommendation']}")
            
            # Test /api/goals
            response = await client.get(f"{base_url}/api/goals", headers=headers)
            print(f"/api/goals: {response.status_code}")
            if response.status_code == 200:
                goals = response.json()
                print(f"Goals count: {len(goals)}")
        
        # Test tool endpoint (with agent token)
        agent_headers = {"Authorization": "Bearer your-agent-token-change-in-production"}
        tool_request = {
            "user_id": "demo@example.com",
            "date": datetime.now().strftime("%Y-%m-%d")
        }
        
        response = await client.post(
            f"{base_url}/tools/getReadinessScore",
            json=tool_request,
            headers=agent_headers
        )
        print(tool_request)
        print(f"/tools/getReadinessScore: {response.status_code}")
        if response.status_code == 200:
            tool_data = response.json()
            print(f"Tool response: {tool_data['readiness_score']['score']}")
        
        print("\nAPI testing completed!")

if __name__ == "__main__":
    asyncio.run(test_api())
