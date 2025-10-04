# 🤖 Weather Chatbot Feature

## Overview

The Weather Chatbot is an intelligent assistant that provides personalized weather advice for farmers and fishermen based on NASA weather data. It can understand natural language queries and provide location-specific recommendations.

## Features

### 🌾 For Farmers
- **Crop Planning**: Advice on planting, harvesting, and irrigation timing
- **Weather Suitability**: Analysis of temperature, precipitation, and wind conditions
- **Risk Assessment**: Evaluation of weather risks for farming activities
- **Location-Specific**: Tailored advice based on farm location

### 🎣 For Fishermen
- **Safety Assessment**: Wind and weather conditions for safe fishing
- **Visibility Analysis**: Weather conditions affecting fishing visibility
- **Maritime Conditions**: Specific advice for sea fishing and cruising
- **Location-Aware**: Recommendations based on fishing location (e.g., Red Sea, Mediterranean)

### 🗣️ Natural Language Processing
- **Intent Recognition**: Understands farming vs fishing queries
- **Location Extraction**: Automatically detects location mentions
- **Context Awareness**: Maintains conversation context
- **Smart Prompting**: Asks for location when needed

## How It Works

### 1. Query Analysis
The chatbot analyzes user queries to:
- Identify user type (farmer, fisherman, general)
- Extract location information
- Determine intent (suitability check, timing advice, risk assessment)
- Assess if location information is needed

### 2. Weather Analysis
When location is provided, the chatbot:
- Fetches historical NASA weather data
- Analyzes relevant parameters (temperature, precipitation, wind)
- Compares against activity-specific thresholds
- Calculates suitability scores

### 3. Response Generation
The chatbot generates personalized responses including:
- Weather condition analysis
- Activity-specific recommendations
- Risk assessments
- Location prompts when needed

## API Endpoints

### POST `/api/chatbot`
Main chatbot endpoint for processing queries.

**Request Body:**
```json
{
  "query": "I'm a farmer and want to know if it's good to farm right now",
  "location": {
    "lat": 30.0444,
    "lng": 31.2357,
    "name": "Cairo, Egypt"
  },
  "target_date": "2024-01-15"
}
```

**Response:**
```json
{
  "response": "🌾 **Farming Analysis for Cairo, Egypt on 2024-01-15**\n\n🌧️ **Rain conditions**: Excellent! Expected 8.2mm of rain - perfect for irrigation and crop growth.\n\n🌡️ **Temperature**: Perfect farming weather! Max temperature around 22.1°C.\n\n💨 **Wind**: Calm conditions with 5.3 km/h winds - ideal for spraying and fieldwork.\n\n✅ **Overall**: Excellent conditions for farming! This is a great time for outdoor agricultural activities.",
  "user_type": "farmer",
  "needs_location": false,
  "extracted_location": null
}
```

### GET `/api/chatbot/suggestions`
Returns example queries for different user types.

**Response:**
```json
{
  "farmer_examples": [
    "I'm a farmer and want to know if it's good to plant crops today",
    "Is it safe to harvest in my field right now?",
    "Should I delay irrigation due to weather conditions?"
  ],
  "fisher_examples": [
    "I'm a fisherman and want to know if it's safe to go fishing today",
    "Is it good to cruise in the Red Sea, Egypt right now?",
    "Should I delay my fishing trip due to weather?"
  ],
  "general_examples": [
    "Tell me about the weather conditions for outdoor activities",
    "Is it safe to be outside today?"
  ]
}
```

## Example Queries

### Farmer Queries
- "I'm a farmer and want to know if it's good to farm right now"
- "Is it safe to harvest in my field right now?"
- "Should I delay irrigation due to weather conditions?"
- "I'm farming in Cairo, Egypt - is the weather suitable for outdoor work?"
- "What's the best time to plant crops in my area?"

### Fisherman Queries
- "I'm a fisherman and want to know if it's safe to go fishing today"
- "Is it good to cruise in the Red Sea, Egypt right now?"
- "Should I delay my fishing trip due to weather?"
- "I'm fishing in Alexandria, Egypt - are conditions safe?"
- "What's the best time to go fishing in my area?"

### General Queries
- "Tell me about the weather conditions for outdoor activities"
- "Is it safe to be outside today?"
- "What's the weather like for my planned activity?"

## Weather Thresholds

### Farming Thresholds
- **Precipitation**: 0-10 mm/day (optimal for irrigation)
- **Temperature**: 15-35°C (comfortable for outdoor work)
- **Wind**: <20 km/h (safe for spraying and fieldwork)
- **Humidity**: 40-80% (comfortable working conditions)

### Fishing Thresholds
- **Wind**: <15 km/h (safe for boating)
- **Precipitation**: <5 mm/day (light rain acceptable)
- **Temperature**: 5-40°C (wide range acceptable)
- **Visibility**: >10 km (good visibility for navigation)

## Frontend Integration

The chatbot is integrated into the main application with:

### UI Components
- **Chat Interface**: Real-time messaging with the weather assistant
- **Suggestion Buttons**: Quick access to common queries
- **Location Integration**: Automatic location detection from map
- **Responsive Design**: Works on desktop and mobile devices

### Features
- **Real-time Communication**: Instant responses to user queries
- **Location Awareness**: Uses map location for weather analysis
- **Context Preservation**: Maintains conversation history
- **Error Handling**: Graceful error messages and recovery

## Usage Examples

### 1. Farmer Asking About Farming
```
User: "I'm a farmer and want to know if it's good to farm right now"
Bot: "🌾 I'd be happy to help with farming weather advice! To provide accurate recommendations, I need to know your location..."
```

### 2. Fisherman with Location
```
User: "I'm a fisherman and want to know if it's safe to go fishing in Alexandria, Egypt"
Bot: "🎣 **Fishing Analysis for Alexandria, Egypt on 2024-01-15**\n\n💨 **Wind**: Perfect fishing conditions! Light winds at 8.2 km/h - safe for boating..."
```

### 3. Location Prompting
```
User: "Is it good to cruise in the Red Sea right now?"
Bot: "🎣 I understand you're asking about fishing in Red Sea. To give you accurate weather advice, I need the exact coordinates (latitude and longitude) of your fishing location..."
```

## Technical Implementation

### Backend Components
- **WeatherChatbot Class**: Main chatbot logic and analysis
- **Query Analysis**: Natural language processing for intent detection
- **Weather Analysis**: Integration with NASA POWER API
- **Response Generation**: Contextual response creation

### Frontend Components
- **Chat Interface**: Real-time messaging UI
- **Location Integration**: Map-based location detection
- **API Communication**: RESTful API calls to backend
- **Error Handling**: User-friendly error messages

## Data Sources

The chatbot uses NASA POWER (Prediction of Worldwide Energy Resources) data:
- **Historical Weather Data**: 1981-present
- **Parameters**: Temperature, precipitation, wind speed, humidity
- **Resolution**: Daily data with 0.5° spatial resolution
- **Coverage**: Global coverage including Egypt and Red Sea region

## Future Enhancements

### Planned Features
- **Multi-language Support**: Arabic and other languages
- **Advanced Analytics**: Trend analysis and forecasting
- **Mobile App**: Dedicated mobile application
- **Voice Interface**: Speech-to-text and text-to-speech
- **Push Notifications**: Weather alerts and recommendations

### Potential Integrations
- **IoT Sensors**: Real-time farm/boat sensor data
- **Market Data**: Crop prices and fishing market conditions
- **Social Features**: Community sharing and advice
- **Expert Consultation**: Connect with agricultural/maritime experts

## Testing

Run the test script to verify chatbot functionality:

```bash
python test_chatbot.py
```

This will test various query types and verify the API responses.

## Support

For issues or questions about the chatbot feature:
1. Check the API documentation
2. Review the example queries
3. Test with the provided test script
4. Check server logs for detailed error information

The chatbot is designed to be robust and user-friendly, providing accurate weather advice based on NASA's comprehensive weather database.
