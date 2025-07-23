"""
Gemini API Integration for General Questions
Brain Team MVP Enhancement

This module integrates with Google Gemini API to provide intelligent responses
for questions outside the campus database scope.
"""

import os
import json
import requests
from typing import Optional, Dict
from dataclasses import dataclass

@dataclass
class GeminiResponse:
    """Response from Gemini API"""
    text: str
    confidence: float
    response_type: str = "gemini"

class GeminiHandler:
    """
    Handles general questions using Google Gemini API
    Falls back gracefully if API is unavailable
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-latest:generateContent"
        self.enabled = bool(self.api_key)
        
        if not self.enabled:
            print("⚠️  Gemini API key not found. Using offline responses for general questions.")
            print("   To enable Gemini: export GEMINI_API_KEY='your-api-key'")
    
    def is_available(self) -> bool:
        """Check if Gemini API is available"""
        return self.enabled
    
    def generate_response(self, question: str, context: str = "general") -> Optional[GeminiResponse]:
        """
        Generate response using Gemini API
        
        Args:
            question: User's question
            context: Context for the response (helps with response quality)
            
        Returns:
            GeminiResponse or None if API call fails
        """
        if not self.enabled:
            return None
        
        try:
            # Craft a campus-assistant appropriate prompt
            prompt = self._create_prompt(question, context)
            
            # Make API request
            headers = {
                'Content-Type': 'application/json',
            }
            
            data = {
                "contents": [{
                    "parts": [{
                        "text": prompt
                    }]
                }],
                "generationConfig": {
                    "temperature": 0.7,
                    "topK": 40,
                    "topP": 0.95,
                    "maxOutputTokens": 200,
                    "stopSequences": []
                }
            }
            
            url = f"{self.base_url}?key={self.api_key}"
            response = requests.post(url, headers=headers, json=data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if 'candidates' in result and len(result['candidates']) > 0:
                    text = result['candidates'][0]['content']['parts'][0]['text']
                    
                    # Clean up response
                    text = self._clean_response(text)
                    
                    return GeminiResponse(
                        text=text,
                        confidence=0.85,  # High confidence for API responses
                        response_type="gemini"
                    )
            elif response.status_code == 429:
                print("⚠️  Gemini API quota exceeded - using intelligent fallback")
                return None
            else:
                print(f"⚠️  Gemini API error {response.status_code} - using fallback")
                return None
            
        except Exception as e:
            print(f"Gemini API error: {e}")
            if hasattr(e, 'response'):
                print(f"Response status: {e.response.status_code}")
                print(f"Response text: {e.response.text}")
            return None
    
    def _create_prompt(self, question: str, context: str) -> str:
        """Create an appropriate prompt for the campus assistant"""
        base_prompt = f"""You are NEXi, a helpful campus AI assistant. A student has asked you a question that's not about campus-specific information.

Please provide a helpful, concise response (under 150 words) that:
1. Directly answers their question if possible
2. Is friendly and encouraging
3. Mentions that you're primarily designed for campus questions
4. Suggests they can ask you about campus facilities, hours, contacts, or procedures

Student question: "{question}"

Response:"""
        
        return base_prompt
    
    def _clean_response(self, text: str) -> str:
        """Clean up the API response"""
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Ensure it ends properly
        if not text.endswith(('.', '!', '?')):
            text += '.'
        
        # Add campus context if not present
        if 'campus' not in text.lower() and len(text) < 100:
            text += " Feel free to ask me about campus facilities, hours, or services!"
        
        return text

class MVPGeneralHandler:
    """
    MVP-ready general question handler with Gemini integration
    Provides intelligent fallbacks for offline operation
    """
    
    def __init__(self):
        self.gemini = GeminiHandler()
        
        # Campus keywords for routing
        self.campus_keywords = [
            'library', 'gym', 'cafeteria', 'dining', 'hall', 'building', 'room', 'parking',
            'campus', 'student', 'class', 'course', 'professor', 'wifi', 'registration',
            'contact', 'hours', 'open', 'close', 'schedule', 'event', 'club', 'sport',
            'department', 'office', 'staff', 'faculty', 'id', 'card', 'portal', 'email',
            'mess', 'canteen', 'food', 'it', 'support', 'tech', 'computer', 'help',
            'desk', 'service', 'services', 'facility', 'facilities', 'location',
            'where', 'find', 'chancellor', 'vice', 'admin', 'administration'
        ]
        
        # Offline responses for common general questions
        self.offline_responses = {
            'math': "I can help with simple calculations! For complex math problems, try a calculator app or ask about our campus math tutoring center.",
            'weather': "I don't have real-time weather data, but check your weather app! I can tell you about covered walkways and indoor spaces on campus.",
            'time': "I don't have the current time, but I can tell you campus facility hours! Try asking 'What time does the library close?'",
            'greeting': "Hello! I'm NEXi, your campus assistant. I'm here to help with campus locations, hours, contacts, and services. What can I help you with?",
            'thanks': "You're welcome! I'm always here to help with campus questions. Feel free to ask about facilities, events, or services anytime!",
            'general': "That's an interesting question! While I specialize in campus information, I'm here to help with locations, hours, contacts, and campus services. What can I help you find?"
        }
    
    def is_campus_related(self, text: str) -> bool:
        """Quick check if question is campus-related"""
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.campus_keywords)
    
    def handle_general_question(self, question: str) -> Optional[Dict]:
        """
        Handle general questions with Gemini API or offline fallback
        
        Returns None if question should be handled by campus system
        """
        # Route campus questions to campus system
        if self.is_campus_related(question):
            return None
        
        question_lower = question.lower()
        
        # Try Gemini API first
        if self.gemini.is_available():
            gemini_response = self.gemini.generate_response(question, "general")
            if gemini_response:
                return {
                    "status": "general",
                    "intent": "general_ai",
                    "confidence": gemini_response.confidence,
                    "context": "general",
                    "entities": {},
                    "response": gemini_response.text,
                    "response_type": "gemini_ai",
                    "fallback_used": False,
                    "suggested_follow_ups": [
                        "Want to know about campus facilities?",
                        "Looking for specific campus services?",
                        "Need help with campus information?"
                    ]
                }
        
        # Fallback to offline responses
        response_type = self._classify_offline(question_lower)
        response_text = self.offline_responses.get(response_type, self.offline_responses['general'])
        
        return {
            "status": "general",
            "intent": f"general_{response_type}",
            "confidence": 0.75,
            "context": "general",
            "entities": {},
            "response": response_text,
            "response_type": "offline_general",
            "fallback_used": True,
            "suggested_follow_ups": [
                "Where is the library?",
                "What time does the gym close?",
                "How do I contact IT support?"
            ]
        }
    
    def _classify_offline(self, question: str) -> str:
        """Classify question type for offline handling"""
        if any(word in question for word in ['hello', 'hi', 'hey', 'greet']):
            return 'greeting'
        elif any(word in question for word in ['thank', 'thanks']):
            return 'thanks'
        elif any(word in question for word in ['+', '-', '*', '/', 'calculate', 'math']):
            return 'math'
        elif any(word in question for word in ['weather', 'rain', 'sunny', 'temperature']):
            return 'weather'
        elif any(word in question for word in ['time', 'clock', 'hour']):
            return 'time'
        else:
            return 'general'

# Test function for MVP demo
def test_mvp_handler():
    """Test the MVP general handler"""
    handler = MVPGeneralHandler()
    
    test_questions = [
        # General questions (should use Gemini/offline)
        "What is the capital of France?",
        "How do you cook pasta?",
        "What's 15 + 27?",
        "Hello there!",
        "Thanks for your help",
        
        # Campus questions (should return None)
        "Where is the library?",
        "What time does the cafeteria close?",
        "How do I connect to campus WiFi?"
    ]
    
    print("🧠 Testing MVP General Handler")
    print("=" * 50)
    
    for question in test_questions:
        result = handler.handle_general_question(question)
        if result:
            print(f"Q: {question}")
            print(f"Type: {result['response_type']}")
            print(f"Response: {result['response']}")
            print(f"Confidence: {result['confidence']}")
        else:
            print(f"Q: {question}")
            print("→ Routed to campus system")
        print("-" * 30)

if __name__ == "__main__":
    test_mvp_handler()
