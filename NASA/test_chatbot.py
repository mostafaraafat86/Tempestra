#!/usr/bin/env python3
"""
Simple test script for the chatbot functionality
"""

import requests
import json
from datetime import date

def test_chatbot():
    base_url = "http://localhost:8000"
    
    print("🤖 Testing Weather Chatbot...")
    print("=" * 50)
    
    # Test cases
    test_cases = [
        {
            "name": "Farmer asking about farming",
            "query": "I'm a farmer and want to know if it's good to farm right now",
            "location": {"lat": 30.0444, "lng": 31.2357, "name": "Cairo, Egypt"}
        },
        {
            "name": "Fisherman asking about Red Sea",
            "query": "I'm a fisherman and want to know if it's good to cruise in the Red Sea, Egypt",
            "location": {"lat": 27.9158, "lng": 34.3300, "name": "Sharm El Sheikh, Egypt"}
        },
        {
            "name": "Farmer without location",
            "query": "I'm a farmer and want to know if it's good to plant crops today",
            "location": None
        },
        {
            "name": "Fisherman without location",
            "query": "I'm a fisherman and want to know if it's safe to go fishing",
            "location": None
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print(f"Query: {test_case['query']}")
        print(f"Location: {test_case['location']}")
        print("-" * 30)
        
        try:
            # Prepare request data
            request_data = {
                "query": test_case['query'],
                "location": test_case['location'],
                "target_date": date.today().isoformat()
            }
            
            # Send request
            response = requests.post(
                f"{base_url}/api/chatbot",
                json=request_data,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Response: {data['response'][:200]}...")
                print(f"User Type: {data.get('user_type', 'Unknown')}")
                print(f"Needs Location: {data.get('needs_location', False)}")
            else:
                print(f"❌ Error: {response.status_code} - {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Testing suggestions endpoint...")
    
    try:
        response = requests.get(f"{base_url}/api/chatbot/suggestions", timeout=10)
        if response.status_code == 200:
            suggestions = response.json()
            print("✅ Suggestions loaded successfully!")
            print(f"Farmer examples: {len(suggestions.get('farmer_examples', []))}")
            print(f"Fisher examples: {len(suggestions.get('fisher_examples', []))}")
            print(f"General examples: {len(suggestions.get('general_examples', []))}")
        else:
            print(f"❌ Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_chatbot()
