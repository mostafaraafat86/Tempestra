#!/usr/bin/env python3
"""
Simple chatbot server using Flask for testing
"""

import json
import logging
from datetime import date, datetime
from typing import Dict, List, Optional, Any
import re

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from flask import Flask, request, jsonify
    from flask_cors import CORS
except ImportError:
    print("Flask not available, using mock responses")
    
    class MockFlask:
        def __init__(self, *args, **kwargs):
            pass
        def route(self, *args, **kwargs):
            def decorator(func):
                return func
            return decorator
        def run(self, *args, **kwargs):
            print("Mock Flask server - not actually running")
    
    Flask = MockFlask
    jsonify = lambda x: x
    request = type('MockRequest', (), {'json': lambda: {}})()

# Simple chatbot implementation
class SimpleWeatherChatbot:
    """Simple weather chatbot with mock data for testing"""
    
    def __init__(self):
        self.farmer_keywords = [
            'farmer', 'farming', 'crop', 'plant', 'harvest', 'irrigation', 
            'agriculture', 'field', 'farm', 'grow', 'cultivate'
        ]
        self.fisher_keywords = [
            'fisher', 'fishing', 'fish', 'boat', 'sea', 'ocean', 'cruise',
            'maritime', 'sail', 'catch', 'fisherman', 'angler'
        ]
        
        # Mock weather data for common locations
        self.mock_weather_data = {
            'cairo': {
                'T2M_MAX': 28.5,  # Max temperature
                'T2M_MIN': 18.2,  # Min temperature
                'T2M': 23.4,      # Average temperature
                'PRECTOTCORR': 2.1,  # Precipitation
                'WS10M': 8.5      # Wind speed
            },
            'red_sea': {
                'T2M_MAX': 32.1,
                'T2M_MIN': 22.8,
                'T2M': 27.5,
                'PRECTOTCORR': 0.5,
                'WS10M': 12.3
            },
            'alexandria': {
                'T2M_MAX': 26.8,
                'T2M_MIN': 16.9,
                'T2M': 21.9,
                'PRECTOTCORR': 3.2,
                'WS10M': 15.7
            }
        }
    
    def analyze_query(self, query: str, location: Optional[Dict] = None) -> Dict:
        """Analyze user query"""
        try:
            query_lower = query.lower().strip()
            
            # Determine user type
            user_type = self._detect_user_type(query_lower)
            
            # Extract location if mentioned
            extracted_location = self._extract_location(query_lower)
            
            # Determine if location is needed
            needs_location = self._needs_location(query_lower, location, extracted_location)
            
            return {
                'user_type': user_type,
                'extracted_location': extracted_location,
                'needs_location': needs_location,
                'query_intent': self._analyze_intent(query_lower, user_type)
            }
        except Exception as e:
            logger.error(f"Error analyzing query: {e}")
            return {
                'user_type': None,
                'extracted_location': None,
                'needs_location': True,
                'query_intent': 'general_advice'
            }
    
    def _detect_user_type(self, query: str) -> Optional[str]:
        """Detect if user is farmer or fisherman"""
        farmer_score = sum(1 for keyword in self.farmer_keywords if keyword in query)
        fisher_score = sum(1 for keyword in self.fisher_keywords if keyword in query)
        
        if farmer_score > fisher_score and farmer_score > 0:
            return 'farmer'
        elif fisher_score > farmer_score and fisher_score > 0:
            return 'fisher'
        return None
    
    def _extract_location(self, query: str) -> Optional[Dict]:
        """Extract location from query"""
        locations = {
            'cairo': {'lat': 30.0444, 'lng': 31.2357, 'name': 'Cairo, Egypt'},
            'red sea': {'lat': 27.9158, 'lng': 34.3300, 'name': 'Red Sea, Egypt'},
            'alexandria': {'lat': 31.2001, 'lng': 29.9187, 'name': 'Alexandria, Egypt'},
            'sharm el sheikh': {'lat': 27.9158, 'lng': 34.3300, 'name': 'Sharm El Sheikh, Egypt'},
            'hurghada': {'lat': 27.2574, 'lng': 33.8129, 'name': 'Hurghada, Egypt'}
        }
        
        for location_name, location_data in locations.items():
            if location_name in query:
                return location_data
        
        return None
    
    def _needs_location(self, query: str, provided_location: Optional[Dict], 
                       extracted_location: Optional[Dict]) -> bool:
        """Determine if location is needed"""
        if provided_location and 'lat' in provided_location and 'lng' in provided_location:
            return False
        if extracted_location:
            return False
        
        location_required_activities = ['farm', 'fish', 'cruise', 'sail', 'plant', 'harvest']
        return any(activity in query for activity in location_required_activities)
    
    def _analyze_intent(self, query: str, user_type: Optional[str]) -> str:
        """Analyze query intent"""
        if 'good' in query or 'suitable' in query or 'safe' in query:
            return 'suitability_check'
        elif 'delay' in query or 'postpone' in query:
            return 'timing_advice'
        elif 'when' in query or 'best time' in query:
            return 'optimal_timing'
        elif 'risk' in query or 'danger' in query:
            return 'risk_assessment'
        else:
            return 'general_advice'
    
    def get_weather_analysis(self, user_type: str, location: Dict, 
                           target_date: Optional[date] = None) -> Dict:
        """Get mock weather analysis"""
        try:
            if not target_date:
                target_date = date.today()
            
            lat = float(location.get('lat', 0))
            lon = float(location.get('lng', 0))
            
            # Determine location key for mock data
            location_key = 'cairo'  # Default
            if 27 <= lat <= 28 and 33 <= lon <= 35:  # Red Sea area
                location_key = 'red_sea'
            elif 31 <= lat <= 32 and 29 <= lon <= 30:  # Alexandria area
                location_key = 'alexandria'
            
            mock_data = self.mock_weather_data[location_key]
            
            # Analyze parameters
            analysis = {}
            for param, value in mock_data.items():
                analysis[param] = self._analyze_parameter(param, [value], user_type, target_date)
            
            return {
                'success': True,
                'analysis': analysis,
                'location': location,
                'target_date': target_date,
                'user_type': user_type
            }
            
        except Exception as e:
            logger.error(f"Error in weather analysis: {e}")
            return {
                'success': False,
                'error': f'Weather analysis failed: {str(e)}',
                'location': location,
                'target_date': target_date,
                'user_type': user_type
            }
    
    def _analyze_parameter(self, param: str, samples: List[float], 
                          user_type: str, target_date: date) -> Dict:
        """Analyze a weather parameter"""
        try:
            if not samples:
                return {'error': 'No data available'}
            
            value = samples[0]
            
            # Simple suitability assessment
            if param == 'WS10M':  # Wind
                if value < 10:
                    suitability = 'excellent'
                elif value < 20:
                    suitability = 'good'
                else:
                    suitability = 'poor'
            elif param == 'PRECTOTCORR':  # Precipitation
                if value < 5:
                    suitability = 'excellent'
                elif value < 15:
                    suitability = 'good'
                else:
                    suitability = 'poor'
            elif param in ['T2M_MAX', 'T2M_MIN', 'T2M']:  # Temperature
                if 15 <= value <= 30:
                    suitability = 'excellent'
                elif 10 <= value <= 35:
                    suitability = 'good'
                else:
                    suitability = 'poor'
            else:
                suitability = 'unknown'
            
            return {
                'mean': round(value, 2),
                'min': round(value, 2),
                'max': round(value, 2),
                'suitability': suitability,
                'sample_count': 1
            }
        except Exception as e:
            return {'error': f'Analysis failed: {str(e)}'}
    
    def generate_response(self, analysis_result: Dict, intent: str, 
                         user_type: str, query: str) -> str:
        """Generate response"""
        try:
            if not analysis_result['success']:
                return f"❌ **Sorry, I encountered an error**: {analysis_result['error']}\n\nPlease try again or check if the location coordinates are valid."
            
            analysis = analysis_result['analysis']
            location = analysis_result['location']
            target_date = analysis_result['target_date']
            
            location_name = location.get('name', f"{location.get('lat', 0):.2f}°, {location.get('lng', 0):.2f}°")
            
            if user_type == 'farmer':
                return self._generate_farmer_response(analysis, location_name, target_date)
            elif user_type == 'fisher':
                return self._generate_fisher_response(analysis, location_name, target_date)
            else:
                return self._generate_general_response(analysis, location_name, target_date)
                
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"❌ **Sorry, I encountered an error**: {str(e)}\n\nPlease try again."
    
    def _generate_farmer_response(self, analysis: Dict, location_name: str, target_date: date) -> str:
        """Generate farmer response"""
        responses = []
        
        if 'PRECTOTCORR' in analysis and 'error' not in analysis['PRECTOTCORR']:
            precip = analysis['PRECTOTCORR']
            if precip['suitability'] == 'excellent':
                responses.append(f"🌧️ **Rain conditions**: Excellent! Expected {precip['mean']:.1f}mm of rain - perfect for irrigation and crop growth.")
            elif precip['suitability'] == 'good':
                responses.append(f"🌧️ **Rain conditions**: Good with {precip['mean']:.1f}mm expected - suitable for farming activities.")
            else:
                responses.append(f"🌧️ **Rain conditions**: Challenging with {precip['mean']:.1f}mm expected - consider irrigation needs.")
        
        if 'T2M_MAX' in analysis and 'error' not in analysis['T2M_MAX']:
            temp = analysis['T2M_MAX']
            if temp['suitability'] == 'excellent':
                responses.append(f"🌡️ **Temperature**: Perfect farming weather! Max temperature around {temp['mean']:.1f}°C.")
            elif temp['suitability'] == 'good':
                responses.append(f"🌡️ **Temperature**: Good conditions with max temperature around {temp['mean']:.1f}°C.")
            else:
                responses.append(f"🌡️ **Temperature**: Challenging with max temperature around {temp['mean']:.1f}°C - consider heat protection.")
        
        if 'WS10M' in analysis and 'error' not in analysis['WS10M']:
            wind = analysis['WS10M']
            if wind['suitability'] == 'excellent':
                responses.append(f"💨 **Wind**: Calm conditions with {wind['mean']:.1f} km/h winds - ideal for spraying and fieldwork.")
            elif wind['suitability'] == 'good':
                responses.append(f"💨 **Wind**: Moderate winds at {wind['mean']:.1f} km/h - suitable for most farming activities.")
            else:
                responses.append(f"💨 **Wind**: Strong winds at {wind['mean']:.1f} km/h - avoid spraying and be cautious with equipment.")
        
        # Overall recommendation
        overall_suitability = self._calculate_overall_suitability(analysis)
        if overall_suitability >= 0.8:
            recommendation = "✅ **Overall**: Excellent conditions for farming! This is a great time for outdoor agricultural activities."
        elif overall_suitability >= 0.6:
            recommendation = "⚠️ **Overall**: Good conditions with some considerations. Monitor weather closely and plan accordingly."
        else:
            recommendation = "❌ **Overall**: Challenging conditions expected. Consider delaying outdoor farming activities or take extra precautions."
        
        responses.append(recommendation)
        
        if not responses:
            return f"🌾 **Farming Analysis for {location_name} on {target_date}**\n\n❌ Unable to analyze weather conditions at this time. Please try again later."
        
        return f"🌾 **Farming Analysis for {location_name} on {target_date}**\n\n" + "\n\n".join(responses)
    
    def _generate_fisher_response(self, analysis: Dict, location_name: str, target_date: date) -> str:
        """Generate fisher response"""
        responses = []
        
        if 'WS10M' in analysis and 'error' not in analysis['WS10M']:
            wind = analysis['WS10M']
            if wind['suitability'] == 'excellent':
                responses.append(f"💨 **Wind**: Perfect fishing conditions! Light winds at {wind['mean']:.1f} km/h - safe for boating.")
            elif wind['suitability'] == 'good':
                responses.append(f"💨 **Wind**: Good conditions with {wind['mean']:.1f} km/h winds - suitable for fishing.")
            else:
                responses.append(f"💨 **Wind**: Strong winds at {wind['mean']:.1f} km/h - consider staying ashore or fishing in protected areas.")
        
        if 'PRECTOTCORR' in analysis and 'error' not in analysis['PRECTOTCORR']:
            precip = analysis['PRECTOTCORR']
            if precip['suitability'] == 'excellent':
                responses.append(f"🌧️ **Rain**: Clear conditions with {precip['mean']:.1f}mm expected - excellent visibility.")
            elif precip['suitability'] == 'good':
                responses.append(f"🌧️ **Rain**: Light rain possible ({precip['mean']:.1f}mm) - still good for fishing.")
            else:
                responses.append(f"🌧️ **Rain**: Heavy rain expected ({precip['mean']:.1f}mm) - consider indoor activities or wait for better weather.")
        
        if 'T2M' in analysis and 'error' not in analysis['T2M']:
            temp = analysis['T2M']
            if temp['suitability'] == 'excellent':
                responses.append(f"🌡️ **Temperature**: Comfortable fishing weather at {temp['mean']:.1f}°C.")
            elif temp['suitability'] == 'good':
                responses.append(f"🌡️ **Temperature**: Good conditions at {temp['mean']:.1f}°C.")
            else:
                responses.append(f"🌡️ **Temperature**: Extreme temperatures at {temp['mean']:.1f}°C - dress appropriately.")
        
        # Overall recommendation
        overall_suitability = self._calculate_overall_suitability(analysis)
        if overall_suitability >= 0.8:
            recommendation = "✅ **Overall**: Excellent fishing conditions! Safe winds and good visibility - perfect for a fishing trip."
        elif overall_suitability >= 0.6:
            recommendation = "⚠️ **Overall**: Good fishing conditions with some considerations. Check local weather updates before heading out."
        else:
            recommendation = "❌ **Overall**: Challenging conditions expected. Consider staying ashore or fishing in protected areas."
        
        responses.append(recommendation)
        
        if not responses:
            return f"🎣 **Fishing Analysis for {location_name} on {target_date}**\n\n❌ Unable to analyze weather conditions at this time. Please try again later."
        
        return f"🎣 **Fishing Analysis for {location_name} on {target_date}**\n\n" + "\n\n".join(responses)
    
    def _generate_general_response(self, analysis: Dict, location_name: str, target_date: date) -> str:
        """Generate general response"""
        return f"📍 **Weather Analysis for {location_name} on {target_date}**\n\nBased on the current weather conditions, outdoor activities should be generally safe. Please check local weather updates for the most current information."
    
    def _calculate_overall_suitability(self, analysis: Dict) -> float:
        """Calculate overall suitability score"""
        if not analysis:
            return 0.0
        
        suitability_scores = []
        for param, data in analysis.items():
            if isinstance(data, dict) and 'suitability' in data and 'error' not in data:
                score_map = {'excellent': 1.0, 'good': 0.7, 'poor': 0.3, 'unknown': 0.5}
                suitability_scores.append(score_map.get(data['suitability'], 0.5))
        
        return sum(suitability_scores) / len(suitability_scores) if suitability_scores else 0.5
    
    def _generate_location_prompt(self, user_type: str, extracted_location: Optional[Dict]) -> str:
        """Generate location prompt"""
        if extracted_location:
            location_name = extracted_location['name']
            if user_type == 'farmer':
                return f"🌾 I understand you're asking about farming in {location_name}. To give you accurate weather advice, I need the exact coordinates (latitude and longitude) of your farm location. Could you please provide the coordinates or tell me the specific city/area where your farm is located?"
            elif user_type == 'fisher':
                return f"🎣 I understand you're asking about fishing in {location_name}. To give you accurate weather advice, I need the exact coordinates (latitude and longitude) of your fishing location. Could you please provide the coordinates or tell me the specific area where you plan to fish?"
            else:
                return f"📍 I understand you're asking about weather in {location_name}. To give you accurate weather advice, I need the exact coordinates (latitude and longitude) of your location. Could you please provide the coordinates or tell me the specific area you're interested in?"
        else:
            if user_type == 'farmer':
                return "🌾 I'd be happy to help with farming weather advice! To provide accurate recommendations, I need to know your location. Could you please tell me:\n\n• The city or area where your farm is located\n• Or provide the coordinates (latitude, longitude)\n\nFor example: 'I'm farming in Cairo, Egypt' or 'My farm is at 30.0444, 31.2357'"
            elif user_type == 'fisher':
                return "🎣 I'd be happy to help with fishing weather advice! To provide accurate recommendations, I need to know your location. Could you please tell me:\n\n• The city or area where you plan to fish\n• Or provide the coordinates (latitude, longitude)\n\nFor example: 'I'm fishing in Alexandria, Egypt' or 'I'm fishing at 31.2001, 29.9187'"
            else:
                return "📍 I'd be happy to help with weather advice! To provide accurate recommendations, I need to know your location. Could you please tell me:\n\n• The city or area you're interested in\n• Or provide the coordinates (latitude, longitude)\n\nFor example: 'I'm in Cairo, Egypt' or 'My location is 30.0444, 31.2357'"

# Initialize chatbot
chatbot = SimpleWeatherChatbot()

# Create Flask app
app = Flask(__name__)
CORS(app)

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "message": "Simple chatbot server is running"})

@app.route('/api/chatbot', methods=['POST'])
def chatbot_endpoint():
    try:
        data = request.json
        query = data.get('query', '')
        location = data.get('location')
        target_date = data.get('target_date')
        
        if not query:
            return jsonify({"error": "Query is required"}), 400
        
        # Analyze the query
        analysis = chatbot.analyze_query(query, location)
        
        # If location is needed, return a prompt for location
        if analysis['needs_location']:
            response = chatbot._generate_location_prompt(
                analysis['user_type'] or 'user', 
                analysis['extracted_location']
            )
            return jsonify({
                "response": response,
                "user_type": analysis['user_type'],
                "needs_location": True,
                "extracted_location": analysis['extracted_location']
            })
        
        # If we have location information, provide weather analysis
        if location:
            weather_analysis = chatbot.get_weather_analysis(
                analysis['user_type'] or 'general',
                location,
                target_date
            )
            
            response = chatbot.generate_response(
                weather_analysis,
                analysis['query_intent'],
                analysis['user_type'] or 'general',
                query
            )
            
            return jsonify({
                "response": response,
                "user_type": analysis['user_type'],
                "needs_location": False,
                "extracted_location": analysis['extracted_location']
            })
        
        # If no location provided, ask for it
        response = chatbot._generate_location_prompt(
            analysis['user_type'] or 'user', 
            analysis['extracted_location']
        )
        return jsonify({
            "response": response,
            "user_type": analysis['user_type'],
            "needs_location": True,
            "extracted_location": analysis['extracted_location']
        })
        
    except Exception as e:
        logger.error(f"Chatbot endpoint error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/chatbot/suggestions', methods=['GET'])
def get_suggestions():
    return jsonify({
        "farmer_examples": [
            "I'm a farmer and want to know if it's good to plant crops today",
            "Is it safe to harvest in my field right now?",
            "Should I delay irrigation due to weather conditions?",
            "I'm farming in Cairo, Egypt - is the weather suitable for outdoor work?"
        ],
        "fisher_examples": [
            "I'm a fisherman and want to know if it's safe to go fishing today",
            "Is it good to cruise in the Red Sea, Egypt right now?",
            "Should I delay my fishing trip due to weather?",
            "I'm fishing in Alexandria, Egypt - are conditions safe?"
        ],
        "general_examples": [
            "Tell me about the weather conditions for outdoor activities",
            "Is it safe to be outside today?",
            "What's the weather like for my planned activity?"
        ]
    })

if __name__ == '__main__':
    print("🤖 Starting Simple Chatbot Server...")
    print("📍 Server will be available at: http://localhost:5000")
    print("🧪 Test the chatbot at: http://localhost:5000/api/health")
    app.run(host='0.0.0.0', port=5000, debug=True)
