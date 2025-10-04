from __future__ import annotations

from datetime import date, datetime
from typing import Dict, List, Optional, Tuple, Any
import re
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from app.services.power_client import fetch_daily_series
    from app.utils.stats import select_dayofyear_window
except ImportError as e:
    logger.error(f"Import error: {e}")
    # Fallback for testing
    def fetch_daily_series(*args, **kwargs):
        return {}
    def select_dayofyear_window(*args, **kwargs):
        return []


class WeatherChatbotV2:
    """Enhanced weather chatbot for farmers and fishermen with robust error handling"""
    
    def __init__(self):
        self.farmer_keywords = [
            'farmer', 'farming', 'crop', 'plant', 'harvest', 'irrigation', 
            'agriculture', 'field', 'farm', 'grow', 'cultivate', 'seed',
            'planting', 'harvesting', 'fieldwork', 'spraying'
        ]
        self.fisher_keywords = [
            'fisher', 'fishing', 'fish', 'boat', 'sea', 'ocean', 'cruise',
            'maritime', 'sail', 'catch', 'fisherman', 'angler', 'boating',
            'sailing', 'maritime', 'coastal', 'offshore'
        ]
        
        # Weather thresholds for different activities
        self.thresholds = {
            'farmer': {
                'precipitation': {'min': 0, 'max': 15},  # mm/day
                'temperature': {'min': 10, 'max': 35},  # °C
                'wind': {'max': 25},  # km/h
                'humidity': {'min': 30, 'max': 85}  # %
            },
            'fisher': {
                'wind': {'max': 20},  # km/h - safe for fishing
                'precipitation': {'max': 8},  # mm/day - light rain okay
                'temperature': {'min': 0, 'max': 45},  # °C - wide range
                'visibility': {'min': 5}  # km - good visibility
            }
        }
        
        # Common locations for quick lookup
        self.common_locations = {
            'cairo': {'lat': 30.0444, 'lng': 31.2357, 'name': 'Cairo, Egypt'},
            'alexandria': {'lat': 31.2001, 'lng': 29.9187, 'name': 'Alexandria, Egypt'},
            'red sea': {'lat': 27.9158, 'lng': 34.3300, 'name': 'Red Sea, Egypt'},
            'sharm el sheikh': {'lat': 27.9158, 'lng': 34.3300, 'name': 'Sharm El Sheikh, Egypt'},
            'hurghada': {'lat': 27.2574, 'lng': 33.8129, 'name': 'Hurghada, Egypt'},
            'luxor': {'lat': 25.6872, 'lng': 32.6396, 'name': 'Luxor, Egypt'},
            'aswan': {'lat': 24.0889, 'lng': 32.8998, 'name': 'Aswan, Egypt'},
            'giza': {'lat': 30.0131, 'lng': 31.2089, 'name': 'Giza, Egypt'}
        }
    
    def analyze_query(self, query: str, location: Optional[Dict] = None) -> Dict:
        """Analyze user query and determine user type and intent"""
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
        """Detect if user is farmer or fisherman based on keywords"""
        try:
            query_lower = query.lower()
            
            # Check for explicit farmer mentions first
            farmer_indicators = ['farmer', 'farming', 'farm', 'crop', 'plant', 'harvest', 'agriculture']
            fisher_indicators = ['fisher', 'fishing', 'fish', 'boat', 'sea', 'ocean', 'cruise', 'maritime']
            
            farmer_score = sum(1 for keyword in farmer_indicators if keyword in query_lower)
            fisher_score = sum(1 for keyword in fisher_indicators if keyword in query_lower)
            
            # If user explicitly says "I'm a farmer", prioritize that
            if 'i\'m a farmer' in query_lower or 'i am a farmer' in query_lower:
                return 'farmer'
            elif 'i\'m a fisher' in query_lower or 'i am a fisher' in query_lower:
                return 'fisher'
            
            # Otherwise use keyword scoring
            if farmer_score > fisher_score and farmer_score > 0:
                return 'farmer'
            elif fisher_score > farmer_score and fisher_score > 0:
                return 'fisher'
            return None
        except Exception as e:
            logger.error(f"Error detecting user type: {e}")
            return None
    
    def _extract_location(self, query: str) -> Optional[Dict]:
        """Extract location information from query"""
        try:
            # Check for common locations first
            for location_name, location_data in self.common_locations.items():
                if location_name in query:
                    return location_data
            
            # Common location patterns
            location_patterns = [
                r'in\s+([a-zA-Z\s]+)',
                r'at\s+([a-zA-Z\s]+)',
                r'near\s+([a-zA-Z\s]+)',
                r'around\s+([a-zA-Z\s]+)',
                r'([a-zA-Z\s]+)\s+area',
                r'([a-zA-Z\s]+)\s+region'
            ]
            
            for pattern in location_patterns:
                match = re.search(pattern, query)
                if match:
                    location_name = match.group(1).strip()
                    # Filter out common words
                    if location_name.lower() not in ['the', 'my', 'this', 'that', 'our', 'here']:
                        return {'name': location_name}
            
            return None
        except Exception as e:
            logger.error(f"Error extracting location: {e}")
            return None
    
    def _needs_location(self, query: str, provided_location: Optional[Dict], 
                       extracted_location: Optional[Dict]) -> bool:
        """Determine if location information is needed"""
        try:
            # If location is already provided, no need to ask
            if provided_location and 'lat' in provided_location and 'lng' in provided_location:
                return False
            
            # If location was extracted from query, no need to ask
            if extracted_location:
                return False
            
            # Check if query mentions specific activities that require location
            location_required_activities = [
                'farm', 'fish', 'cruise', 'sail', 'plant', 'harvest', 'boat'
            ]
            
            return any(activity in query for activity in location_required_activities)
        except Exception as e:
            logger.error(f"Error checking location needs: {e}")
            return True
    
    def _analyze_intent(self, query: str, user_type: Optional[str]) -> str:
        """Analyze the intent of the user query"""
        try:
            if 'good' in query or 'suitable' in query or 'safe' in query:
                return 'suitability_check'
            elif 'delay' in query or 'postpone' in query or 'wait' in query:
                return 'timing_advice'
            elif 'when' in query or 'best time' in query:
                return 'optimal_timing'
            elif 'risk' in query or 'danger' in query:
                return 'risk_assessment'
            else:
                return 'general_advice'
        except Exception as e:
            logger.error(f"Error analyzing intent: {e}")
            return 'general_advice'
    
    def get_weather_analysis(self, user_type: str, location: Dict, 
                           target_date: Optional[date] = None) -> Dict:
        """Get weather analysis for specific user type and location"""
        try:
            if not target_date:
                target_date = date.today()
            
            lat = float(location.get('lat', 0))
            lon = float(location.get('lng', 0))
            
            # Validate coordinates
            if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
                return {
                    'success': False,
                    'error': 'Invalid coordinates. Latitude must be between -90 and 90, longitude between -180 and 180.',
                    'location': location,
                    'target_date': target_date,
                    'user_type': user_type
                }
            
            # Get weather data for the location
            start_date = date(2020, 1, 1)  # Use more recent data
            end_date = date.today()
            
            # Fetch relevant weather parameters
            if user_type == 'farmer':
                parameters = ['T2M_MAX', 'T2M_MIN', 'PRECTOTCORR', 'WS10M']
            else:  # fisher
                parameters = ['WS10M', 'PRECTOTCORR', 'T2M']
            
            logger.info(f"Fetching weather data for lat={lat}, lon={lon}, params={parameters}")
            
            series = fetch_daily_series(
                lat=lat, lon=lon, 
                start=start_date, end=end_date, 
                parameters=parameters
            )
            
            if not series:
                return {
                    'success': False,
                    'error': 'No weather data available for this location.',
                    'location': location,
                    'target_date': target_date,
                    'user_type': user_type
                }
            
            # Analyze each parameter
            analysis = {}
            for param in parameters:
                try:
                    if param in series and series[param]:
                        samples = select_dayofyear_window(series[param], target_date, 15)
                        if samples:
                            analysis[param] = self._analyze_parameter(
                                param, samples, user_type, target_date
                            )
                        else:
                            analysis[param] = {'error': f'No data available for {param}'}
                    else:
                        analysis[param] = {'error': f'Parameter {param} not available'}
                except Exception as e:
                    logger.error(f"Error analyzing parameter {param}: {e}")
                    analysis[param] = {'error': f'Failed to analyze {param}: {str(e)}'}
            
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
        """Analyze a specific weather parameter"""
        try:
            if not samples:
                return {'error': 'No data available'}
            
            # Filter out None values and invalid numbers
            valid_samples = [
                val for val in samples 
                if val is not None 
                and val == val  # Check for NaN
                and val != float('inf') 
                and val != float('-inf')
                and val >= 0  # Ensure non-negative values for most weather parameters
            ]
            
            # For temperature parameters, allow negative values
            if param in ['T2M_MAX', 'T2M_MIN', 'T2M']:
                valid_samples = [
                    val for val in samples 
                    if val is not None 
                    and val == val  # Check for NaN
                    and val != float('inf') 
                    and val != float('-inf')
                ]
            
            if not valid_samples:
                return {'error': 'No valid data'}
            
            # Calculate statistics
            mean_val = sum(valid_samples) / len(valid_samples)
            min_val = min(valid_samples)
            max_val = max(valid_samples)
            
            # Ensure reasonable values
            if param == 'WS10M':  # Wind speed should be positive
                mean_val = max(0, mean_val)
                min_val = max(0, min_val)
                max_val = max(0, max_val)
            elif param == 'PRECTOTCORR':  # Precipitation should be non-negative
                mean_val = max(0, mean_val)
                min_val = max(0, min_val)
                max_val = max(0, max_val)
            
            # Get thresholds for this parameter and user type
            thresholds = self.thresholds.get(user_type, {})
            
            # Determine suitability
            suitability = self._assess_suitability(param, mean_val, thresholds)
            
            return {
                'mean': round(mean_val, 2),
                'min': round(min_val, 2),
                'max': round(max_val, 2),
                'suitability': suitability,
                'thresholds': thresholds.get(self._get_threshold_key(param), {}),
                'sample_count': len(valid_samples)
            }
        except Exception as e:
            logger.error(f"Error analyzing parameter {param}: {e}")
            return {'error': f'Analysis failed: {str(e)}'}
    
    def _get_threshold_key(self, param: str) -> str:
        """Map parameter names to threshold keys"""
        mapping = {
            'T2M_MAX': 'temperature',
            'T2M_MIN': 'temperature',
            'T2M': 'temperature',
            'PRECTOTCORR': 'precipitation',
            'WS10M': 'wind',
            'WS10M_MAX': 'wind'
        }
        return mapping.get(param, param.lower())
    
    def _assess_suitability(self, param: str, value: float, thresholds: Dict) -> str:
        """Assess weather suitability based on thresholds"""
        try:
            threshold_key = self._get_threshold_key(param)
            param_thresholds = thresholds.get(threshold_key, {})
            
            if not param_thresholds:
                return 'unknown'
            
            # Check if value is within acceptable range
            if 'min' in param_thresholds and value < param_thresholds['min']:
                return 'poor'
            if 'max' in param_thresholds and value > param_thresholds['max']:
                return 'poor'
            
            # Check for optimal range (within 80% of threshold range)
            if 'min' in param_thresholds and 'max' in param_thresholds:
                range_size = param_thresholds['max'] - param_thresholds['min']
                optimal_min = param_thresholds['min'] + 0.1 * range_size
                optimal_max = param_thresholds['max'] - 0.1 * range_size
                
                if optimal_min <= value <= optimal_max:
                    return 'excellent'
                else:
                    return 'good'
            
            return 'good'
        except Exception as e:
            logger.error(f"Error assessing suitability: {e}")
            return 'unknown'
    
    def generate_response(self, analysis_result: Dict, intent: str, 
                         user_type: str, query: str) -> str:
        """Generate human-readable response based on analysis"""
        try:
            if not analysis_result['success']:
                return self._generate_error_response(analysis_result['error'])
            
            analysis = analysis_result['analysis']
            location = analysis_result['location']
            target_date = analysis_result['target_date']
            
            # Generate response based on intent
            if intent == 'suitability_check':
                return self._generate_suitability_response(analysis, user_type, location, target_date)
            elif intent == 'timing_advice':
                return self._generate_timing_response(analysis, user_type, location, target_date)
            elif intent == 'optimal_timing':
                return self._generate_optimal_timing_response(analysis, user_type, location)
            elif intent == 'risk_assessment':
                return self._generate_risk_response(analysis, user_type, location, target_date)
            else:
                return self._generate_general_response(analysis, user_type, location, target_date)
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return self._generate_error_response(f"Response generation failed: {str(e)}")
    
    def _generate_suitability_response(self, analysis: Dict, user_type: str, 
                                     location: Dict, target_date: date) -> str:
        """Generate response for suitability check"""
        try:
            location_name = location.get('name', f"{location.get('lat', 0):.2f}°, {location.get('lng', 0):.2f}°")
            
            if user_type == 'farmer':
                return self._generate_farmer_suitability(analysis, location_name, target_date)
            else:
                return self._generate_fisher_suitability(analysis, location_name, target_date)
        except Exception as e:
            logger.error(f"Error generating suitability response: {e}")
            return self._generate_error_response(f"Suitability analysis failed: {str(e)}")
    
    def _generate_farmer_suitability(self, analysis: Dict, location_name: str, 
                                   target_date: date) -> str:
        """Generate farming suitability response"""
        try:
            responses = []
            
            # Check precipitation
            if 'PRECTOTCORR' in analysis and 'error' not in analysis['PRECTOTCORR']:
                precip = analysis['PRECTOTCORR']
                if precip['suitability'] == 'excellent':
                    responses.append(f"🌧️ **Rain conditions**: Excellent! Expected {precip['mean']:.1f}mm of rain - perfect for irrigation and crop growth.")
                elif precip['suitability'] == 'good':
                    responses.append(f"🌧️ **Rain conditions**: Good with {precip['mean']:.1f}mm expected - suitable for farming activities.")
                else:
                    responses.append(f"🌧️ **Rain conditions**: Challenging with {precip['mean']:.1f}mm expected - consider irrigation needs.")
            
            # Check temperature
            if 'T2M_MAX' in analysis and 'error' not in analysis['T2M_MAX']:
                temp = analysis['T2M_MAX']
                if temp['suitability'] == 'excellent':
                    responses.append(f"🌡️ **Temperature**: Perfect farming weather! Max temperature around {temp['mean']:.1f}°C.")
                elif temp['suitability'] == 'good':
                    responses.append(f"🌡️ **Temperature**: Good conditions with max temperature around {temp['mean']:.1f}°C.")
                else:
                    responses.append(f"🌡️ **Temperature**: Challenging with max temperature around {temp['mean']:.1f}°C - consider heat protection.")
            
            # Check wind
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
        except Exception as e:
            logger.error(f"Error generating farmer suitability: {e}")
            return self._generate_error_response(f"Farming analysis failed: {str(e)}")
    
    def _generate_fisher_suitability(self, analysis: Dict, location_name: str, 
                                    target_date: date) -> str:
        """Generate fishing suitability response"""
        try:
            responses = []
            
            # Check wind (most important for fishing)
            if 'WS10M' in analysis and 'error' not in analysis['WS10M']:
                wind = analysis['WS10M']
                if wind['suitability'] == 'excellent':
                    responses.append(f"💨 **Wind**: Perfect fishing conditions! Light winds at {wind['mean']:.1f} km/h - safe for boating.")
                elif wind['suitability'] == 'good':
                    responses.append(f"💨 **Wind**: Good conditions with {wind['mean']:.1f} km/h winds - suitable for fishing.")
                else:
                    responses.append(f"💨 **Wind**: Strong winds at {wind['mean']:.1f} km/h - consider staying ashore or fishing in protected areas.")
            
            # Check precipitation
            if 'PRECTOTCORR' in analysis and 'error' not in analysis['PRECTOTCORR']:
                precip = analysis['PRECTOTCORR']
                if precip['suitability'] == 'excellent':
                    responses.append(f"🌧️ **Rain**: Clear conditions with {precip['mean']:.1f}mm expected - excellent visibility.")
                elif precip['suitability'] == 'good':
                    responses.append(f"🌧️ **Rain**: Light rain possible ({precip['mean']:.1f}mm) - still good for fishing.")
                else:
                    responses.append(f"🌧️ **Rain**: Heavy rain expected ({precip['mean']:.1f}mm) - consider indoor activities or wait for better weather.")
            
            # Check temperature
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
        except Exception as e:
            logger.error(f"Error generating fisher suitability: {e}")
            return self._generate_error_response(f"Fishing analysis failed: {str(e)}")
    
    def _generate_timing_response(self, analysis: Dict, user_type: str, 
                                location: Dict, target_date: date) -> str:
        """Generate timing advice response"""
        try:
            overall_suitability = self._calculate_overall_suitability(analysis)
            
            if overall_suitability >= 0.7:
                return f"✅ **Timing Advice**: Conditions look excellent for {target_date}! No need to delay - this is a great time for your activities."
            elif overall_suitability >= 0.5:
                return f"⚠️ **Timing Advice**: Conditions are acceptable for {target_date}, but you might want to wait a few days for better weather if possible."
            else:
                return f"❌ **Timing Advice**: I'd recommend delaying your activities. Conditions on {target_date} are challenging - consider waiting for better weather."
        except Exception as e:
            logger.error(f"Error generating timing response: {e}")
            return self._generate_error_response(f"Timing analysis failed: {str(e)}")
    
    def _generate_optimal_timing_response(self, analysis: Dict, user_type: str, 
                                        location: Dict) -> str:
        """Generate optimal timing response"""
        try:
            if user_type == 'farmer':
                return "🌾 **Optimal Timing**: For farming, spring and early fall typically offer the best conditions. Look for periods with moderate temperatures (15-25°C), light winds (<15 km/h), and adequate rainfall (5-15mm)."
            else:
                return "🎣 **Optimal Timing**: For fishing, early morning and late afternoon are usually best. Look for calm winds (<10 km/h), clear skies, and stable weather patterns."
        except Exception as e:
            logger.error(f"Error generating optimal timing response: {e}")
            return self._generate_error_response(f"Optimal timing analysis failed: {str(e)}")
    
    def _generate_risk_response(self, analysis: Dict, user_type: str, 
                              location: Dict, target_date: date) -> str:
        """Generate risk assessment response"""
        try:
            overall_suitability = self._calculate_overall_suitability(analysis)
            
            if overall_suitability >= 0.8:
                return f"✅ **Risk Assessment**: Low risk conditions for {target_date}. Weather looks safe and favorable for your activities."
            elif overall_suitability >= 0.6:
                return f"⚠️ **Risk Assessment**: Moderate risk conditions for {target_date}. Exercise caution and monitor weather closely."
            else:
                return f"❌ **Risk Assessment**: High risk conditions for {target_date}. Consider postponing activities or take extra safety precautions."
        except Exception as e:
            logger.error(f"Error generating risk response: {e}")
            return self._generate_error_response(f"Risk assessment failed: {str(e)}")
    
    def _generate_general_response(self, analysis: Dict, user_type: str, 
                                 location: Dict, target_date: date) -> str:
        """Generate general advice response"""
        try:
            return self._generate_suitability_response(analysis, user_type, location, target_date)
        except Exception as e:
            logger.error(f"Error generating general response: {e}")
            return self._generate_error_response(f"General analysis failed: {str(e)}")
    
    def _generate_error_response(self, error: str) -> str:
        """Generate error response"""
        return f"❌ **Sorry, I encountered an error**: {error}\n\nPlease try again or check if the location coordinates are valid."
    
    def _calculate_overall_suitability(self, analysis: Dict) -> float:
        """Calculate overall suitability score"""
        try:
            if not analysis:
                return 0.0
            
            suitability_scores = []
            for param, data in analysis.items():
                if isinstance(data, dict) and 'suitability' in data and 'error' not in data:
                    score_map = {'excellent': 1.0, 'good': 0.7, 'poor': 0.3, 'unknown': 0.5}
                    suitability_scores.append(score_map.get(data['suitability'], 0.5))
            
            return sum(suitability_scores) / len(suitability_scores) if suitability_scores else 0.5
        except Exception as e:
            logger.error(f"Error calculating overall suitability: {e}")
            return 0.5
    
    def _generate_location_prompt(self, user_type: str, extracted_location: Optional[Dict]) -> str:
        """Generate a prompt asking for location information"""
        try:
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
        except Exception as e:
            logger.error(f"Error generating location prompt: {e}")
            return "📍 I'd be happy to help with weather advice! To provide accurate recommendations, I need to know your location. Could you please provide the coordinates or tell me the specific area you're interested in?"
