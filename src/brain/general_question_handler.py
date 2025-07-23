"""
Enhanced General Question Handler
This module distinguishes between campus-specific and general questions
and provides appropriate responses for each type.
"""

import re
import math
import random
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass

@dataclass
class GeneralResponse:
    """Response for general (non-campus) questions"""
    response_type: str  # "math", "general_knowledge", "weather", "time", "conversational"
    text: str
    confidence: float

class GeneralQuestionHandler:
    """
    Handles general questions that are not campus-specific.
    Acts like a general LLM for non-campus queries.
    """
    
    def __init__(self):
        self.math_patterns = [
            r'(\d+(?:\.\d+)?)\s*[\+\-\*\/x×÷]\s*(\d+(?:\.\d+)?)',
            r'what\s+is\s+(\d+(?:\.\d+)?)\s*[\+\-\*\/x×÷]\s*(\d+(?:\.\d+)?)',
            r'calculate\s+(\d+(?:\.\d+)?)\s*[\+\-\*\/x×÷]\s*(\d+(?:\.\d+)?)',
            r'solve\s+(\d+(?:\.\d+)?)\s*[\+\-\*\/x×÷]\s*(\d+(?:\.\d+)?)'
        ]
        
        self.campus_keywords = {
            'location': ['library', 'gym', 'cafeteria', 'building', 'room', 'parking', 'campus', 'dining', 'hall'],
            'academic': ['register', 'class', 'course', 'professor', 'grade', 'exam', 'homework', 'assignment', 'tuition'],
            'services': ['wifi', 'student', 'id', 'card', 'portal', 'email', 'account', 'password'],
            'facilities': ['hours', 'open', 'close', 'schedule', 'time'],
            'contact': ['contact', 'phone', 'email', 'office', 'department', 'staff', 'faculty'],
            'events': ['event', 'activity', 'club', 'sport', 'game', 'meeting', 'fair']
        }
        
        # Load general knowledge responses
        self.general_responses = self._load_general_responses()
    
    def _load_general_responses(self) -> Dict[str, List[str]]:
        """Load templates for general responses"""
        return {
            'weather': [
                "I don't have access to current weather data, but you can check weather apps or websites like weather.com for accurate forecasts.",
                "For current weather conditions, I'd recommend checking your local weather app or asking a voice assistant with internet access.",
                "I can't provide real-time weather information, but weather apps on your phone will give you the most up-to-date conditions."
            ],
            'time': [
                "I don't have access to real-time information, but you can check the current time on your device or ask 'What time is it?' to your voice assistant.",
                "For the current time, check your phone, computer, or any clock nearby."
            ],
            'general_knowledge': [
                "That's an interesting question! While I'm specialized in campus information, for general knowledge questions like this, I'd recommend checking reliable sources like Wikipedia, encyclopedias, or search engines.",
                "I focus on campus-related questions, but for general information, you might want to try a web search or ask a general-purpose AI assistant.",
                "That's outside my campus expertise area. For general questions like this, web search engines or general AI assistants would be more helpful."
            ],
            'conversational': [
                "Thanks for the friendly question! I'm here and ready to help with campus information. What can I assist you with today?",
                "Hello! I'm doing well and ready to help. What campus-related question can I answer for you?",
                "I'm here and functioning well! How can I help you navigate campus life today?"
            ],
            'compliment': [
                "Thank you for the kind words! I'm here to help with any campus questions you have.",
                "I appreciate that! Let me know what campus information you need.",
                "Thanks! I'm always happy to help with campus-related questions."
            ]
        }
    
    def is_campus_related(self, text: str) -> bool:
        """
        Determine if a question is campus-related or general
        Returns True for campus questions, False for general questions
        """
        text_lower = text.lower()
        
        # Special handling for greetings - these should be general
        greeting_patterns = [
            r'\bhello\b', r'\bhi\b', r'\bhey\b', r'\bgreetings\b',
            r'good morning', r'good afternoon', r'good evening'
        ]
        
        for pattern in greeting_patterns:
            if re.search(pattern, text_lower):
                # Check if it's specifically mentioning campus assistant
                if any(word in text_lower for word in ['nexi', 'campus', 'assistant']):
                    return False  # General greeting to the assistant
                return False  # General greeting
        
        # Check for explicit campus keywords
        for category, keywords in self.campus_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return True
        
        # Check for campus-specific phrases
        campus_phrases = [
            'on campus', 'at campus', 'school', 'university', 'college',
            'student', 'academic', 'enrollment', 'registration'
        ]
        
        for phrase in campus_phrases:
            if phrase in text_lower:
                return True
        
        return False
    
    def handle_math_question(self, text: str) -> Optional[GeneralResponse]:
        """Handle simple math calculations"""
        text_clean = text.lower().strip()
        
        # Try to find and evaluate math expressions
        for pattern in self.math_patterns:
            match = re.search(pattern, text_clean)
            if match:
                try:
                    # Extract numbers and operator
                    if '+' in text_clean:
                        nums = re.findall(r'(\d+(?:\.\d+)?)', text_clean)
                        if len(nums) >= 2:
                            result = float(nums[0]) + float(nums[1])
                            return GeneralResponse(
                                response_type="math",
                                text=f"{nums[0]} + {nums[1]} = {result}",
                                confidence=0.95
                            )
                    elif '-' in text_clean:
                        nums = re.findall(r'(\d+(?:\.\d+)?)', text_clean)
                        if len(nums) >= 2:
                            result = float(nums[0]) - float(nums[1])
                            return GeneralResponse(
                                response_type="math",
                                text=f"{nums[0]} - {nums[1]} = {result}",
                                confidence=0.95
                            )
                    elif '*' in text_clean or 'x' in text_clean or '×' in text_clean:
                        nums = re.findall(r'(\d+(?:\.\d+)?)', text_clean)
                        if len(nums) >= 2:
                            result = float(nums[0]) * float(nums[1])
                            return GeneralResponse(
                                response_type="math",
                                text=f"{nums[0]} × {nums[1]} = {result}",
                                confidence=0.95
                            )
                    elif '/' in text_clean or '÷' in text_clean:
                        nums = re.findall(r'(\d+(?:\.\d+)?)', text_clean)
                        if len(nums) >= 2 and float(nums[1]) != 0:
                            result = float(nums[0]) / float(nums[1])
                            return GeneralResponse(
                                response_type="math",
                                text=f"{nums[0]} ÷ {nums[1]} = {result}",
                                confidence=0.95
                            )
                except (ValueError, ZeroDivisionError):
                    continue
        
        return None
    
    def handle_weather_question(self, text: str) -> Optional[GeneralResponse]:
        """Handle weather-related questions"""
        weather_keywords = ['weather', 'temperature', 'rain', 'sunny', 'cloudy', 'forecast', 'hot', 'cold']
        text_lower = text.lower()
        
        if any(keyword in text_lower for keyword in weather_keywords):
            response_text = random.choice(self.general_responses['weather'])
            return GeneralResponse(
                response_type="weather",
                text=response_text,
                confidence=0.9
            )
        
        return None
    
    def handle_time_question(self, text: str) -> Optional[GeneralResponse]:
        """Handle time-related questions"""
        time_keywords = ['time', 'clock', 'hour', 'minute', 'now']
        text_lower = text.lower()
        
        if any(keyword in text_lower for keyword in time_keywords) and not self.is_campus_related(text):
            response_text = random.choice(self.general_responses['time'])
            return GeneralResponse(
                response_type="time",
                text=response_text,
                confidence=0.9
            )
        
        return None
    
    def handle_conversational_question(self, text: str) -> Optional[GeneralResponse]:
        """Handle friendly/conversational questions"""
        conversational_patterns = [
            r'how are you',
            r'how is your day',
            r'what\'?s up',
            r'how\'?s it going',
            r'are you okay',
            r'how do you feel'
        ]
        
        # Enhanced greeting patterns
        greeting_patterns = [
            r'\bhello\b',
            r'\bhi\b', 
            r'\bhey\b',
            r'\bgreetings\b',
            r'good morning',
            r'good afternoon',
            r'good evening',
            r'hello nexi',
            r'hi nexi',
            r'hey nexi'
        ]
        
        compliment_patterns = [
            r'you\'?re (good|great|awesome|amazing|helpful|smart)',
            r'nice (work|job)',
            r'thank you',
            r'thanks',
            r'good (bot|ai|assistant)'
        ]
        
        text_lower = text.lower()
        
        # Check for greetings first
        for pattern in greeting_patterns:
            if re.search(pattern, text_lower):
                response_text = random.choice(self.general_responses['conversational'])
                return GeneralResponse(
                    response_type="conversational",
                    text=response_text,
                    confidence=0.95  # High confidence for greetings
                )
        
        # Check for conversational questions
        for pattern in conversational_patterns:
            if re.search(pattern, text_lower):
                response_text = random.choice(self.general_responses['conversational'])
                return GeneralResponse(
                    response_type="conversational",
                    text=response_text,
                    confidence=0.85
                )
        
        # Check for compliments
        for pattern in compliment_patterns:
            if re.search(pattern, text_lower):
                response_text = random.choice(self.general_responses['compliment'])
                return GeneralResponse(
                    response_type="conversational",
                    text=response_text,
                    confidence=0.85
                )
        
        return None
    
    def handle_general_knowledge(self, text: str) -> Optional[GeneralResponse]:
        """Handle general knowledge questions"""
        # If it's not campus-related and we haven't handled it yet, treat as general knowledge
        if not self.is_campus_related(text):
            response_text = random.choice(self.general_responses['general_knowledge'])
            return GeneralResponse(
                response_type="general_knowledge",
                text=response_text,
                confidence=0.7
            )
        
        return None
    
    def process_general_question(self, text: str) -> Optional[GeneralResponse]:
        """
        Main method to process general (non-campus) questions
        Returns None if the question should be handled by campus system
        """
        # First check if it's campus-related
        if self.is_campus_related(text):
            return None  # Let campus system handle it
        
        # Try different general question handlers in order of specificity
        handlers = [
            self.handle_math_question,
            self.handle_conversational_question,
            self.handle_weather_question,
            self.handle_time_question,
            self.handle_general_knowledge
        ]
        
        for handler in handlers:
            result = handler(text)
            if result:
                return result
        
        return None


# Test the general question handler
def test_general_handler():
    """Test the general question handler"""
    handler = GeneralQuestionHandler()
    
    test_questions = [
        # Math questions
        "What is 2 + 2?",
        "Calculate 15 * 3",
        "10 - 4 = ?",
        "What's 100 / 5?",
        
        # Weather questions
        "How is the weather today?",
        "Will it rain tomorrow?",
        "What's the temperature?",
        
        # Conversational
        "How are you?",
        "Thanks for your help",
        "You're awesome!",
        
        # General knowledge
        "Who is the president?",
        "What is the capital of France?",
        
        # Campus questions (should return None)
        "Where is the library?",
        "What time does the gym close?",
        "How do I connect to campus WiFi?"
    ]
    
    print("🧠 Testing General Question Handler")
    print("=" * 50)
    
    for question in test_questions:
        result = handler.process_general_question(question)
        if result:
            print(f"Q: {question}")
            print(f"Type: {result.response_type}")
            print(f"Response: {result.text}")
            print(f"Confidence: {result.confidence}")
        else:
            print(f"Q: {question}")
            print("→ Should be handled by campus system")
        print("-" * 40)

if __name__ == "__main__":
    test_general_handler()
