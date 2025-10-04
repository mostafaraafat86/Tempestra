#!/usr/bin/env python3
"""
Standalone test script for the chatbot functionality
"""

import sys
import os
from datetime import date

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

try:
    from services.chatbot_service_v2 import WeatherChatbotV2
    print("✅ Successfully imported WeatherChatbotV2")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

def test_chatbot():
    print("🤖 Testing Enhanced Weather Chatbot...")
    print("=" * 60)
    
    # Initialize chatbot
    chatbot = WeatherChatbotV2()
    print("✅ Chatbot initialized successfully")
    
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
        },
        {
            "name": "General weather query",
            "query": "What's the weather like for outdoor activities?",
            "location": {"lat": 30.0444, "lng": 31.2357, "name": "Cairo, Egypt"}
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print(f"Query: {test_case['query']}")
        print(f"Location: {test_case['location']}")
        print("-" * 40)
        
        try:
            # Test query analysis
            analysis = chatbot.analyze_query(test_case['query'], test_case['location'])
            print(f"✅ Query Analysis:")
            print(f"   User Type: {analysis.get('user_type', 'Unknown')}")
            print(f"   Needs Location: {analysis.get('needs_location', False)}")
            print(f"   Intent: {analysis.get('query_intent', 'Unknown')}")
            print(f"   Extracted Location: {analysis.get('extracted_location', 'None')}")
            
            # Test weather analysis if location is provided
            if test_case['location']:
                weather_analysis = chatbot.get_weather_analysis(
                    analysis.get('user_type', 'general'),
                    test_case['location'],
                    date.today()
                )
                
                if weather_analysis['success']:
                    print(f"✅ Weather Analysis:")
                    print(f"   Parameters analyzed: {list(weather_analysis['analysis'].keys())}")
                    for param, data in weather_analysis['analysis'].items():
                        if 'error' not in data:
                            print(f"   {param}: {data.get('mean', 'N/A')} ({data.get('suitability', 'unknown')})")
                        else:
                            print(f"   {param}: Error - {data['error']}")
                else:
                    print(f"❌ Weather Analysis Failed: {weather_analysis['error']}")
                
                # Test response generation
                response = chatbot.generate_response(
                    weather_analysis,
                    analysis['query_intent'],
                    analysis.get('user_type', 'general'),
                    test_case['query']
                )
                print(f"✅ Response Generated:")
                print(f"   Length: {len(response)} characters")
                print(f"   Preview: {response[:100]}...")
            else:
                # Test location prompt
                response = chatbot._generate_location_prompt(
                    analysis.get('user_type', 'general'),
                    analysis.get('extracted_location')
                )
                print(f"✅ Location Prompt Generated:")
                print(f"   Length: {len(response)} characters")
                print(f"   Preview: {response[:100]}...")
                
        except Exception as e:
            print(f"❌ Test failed: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("🎯 Testing location detection...")
    
    # Test location detection
    location_tests = [
        "I'm farming in Cairo, Egypt",
        "I'm fishing in Alexandria",
        "Is it good to cruise in the Red Sea?",
        "What's the weather like in Sharm El Sheikh?",
        "I'm in Hurghada and want to go fishing"
    ]
    
    for query in location_tests:
        try:
            analysis = chatbot.analyze_query(query)
            extracted = analysis.get('extracted_location')
            if extracted:
                print(f"✅ '{query}' -> {extracted}")
            else:
                print(f"❌ '{query}' -> No location detected")
        except Exception as e:
            print(f"❌ '{query}' -> Error: {e}")
    
    print("\n🎉 Chatbot testing completed!")

if __name__ == "__main__":
    test_chatbot()
