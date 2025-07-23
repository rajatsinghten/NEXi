"""
NEXi Brain MVP System
Brain Team: Krishna, Rajat

This is the production-ready MVP brain system that combines:
- Campus-specific question handling with AI-powered routing
- Gemini AI integration for intelligent question analysis
- Enhanced answer selection and framing
- Optimized for live demonstration
- Fallback systems for offline operation
"""

import sys
from pathlib import Path
import json
import time
from typing import Dict, List, Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from brain.ml_classifier import MLIntentClassifier
from brain.mvp_gemini_handler import MVPGeneralHandler
from brain.intelligent_router import IntelligentRouter

class NEXiBrainMVP:
    """
    MVP Brain System for Live Demonstration
    
    Features:
    - Intelligent AI-powered question routing
    - Campus Q&A with 120+ entries
    - Gemini AI for enhanced analysis and general questions
    - Fast response times (<100ms)
    - Graceful fallbacks
    - Live demo optimized
    """
    
    def __init__(self, data_path: str = "data/campus_qa"):
        print("🧠 Initializing NEXi Brain MVP System...")
        
        # Core components
        self.ml_classifier = MLIntentClassifier(data_path)
        self.general_handler = MVPGeneralHandler()
        self.intelligent_router = IntelligentRouter()
        self.qa_database = self._load_mvp_database(data_path)
        
        # MVP metrics (simplified for demo)
        self.metrics = {
            "total_queries": 0,
            "campus_questions": 0,
            "general_questions": 0,
            "avg_response_time": 0.0,
            "ai_routing_success": 0
        }
        
        print("✅ NEXi Brain MVP System ready for demonstration!")
    
    def _load_mvp_database(self, data_path: str) -> Dict:
        """Load campus Q&A database"""
        try:
            db_path = Path(data_path) / "expanded_database.json"
            with open(db_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print("Warning: Campus database not found, using basic responses")
            return {}
    
    def process_query(self, user_input: str, user_id: str = "demo_user") -> Dict:
        """
        Enhanced MVP Query Processing Pipeline with AI Routing
        
        Returns:
        - Campus questions: AI-enhanced database answers
        - General questions: Gemini AI responses
        - Fast response optimized for live demo
        """
        start_time = time.time()
        self.metrics["total_queries"] += 1
        
        # Step 1: Use intelligent AI routing to analyze the question
        routing_result = self.intelligent_router.analyze_question(user_input)
        
        if routing_result.is_campus_question:
            # Handle as campus question with AI enhancement
            self.metrics["campus_questions"] += 1
            
            # Try AI-powered answer selection first
            ai_answer = self.intelligent_router.find_best_answer(
                user_input, routing_result, self.qa_database
            )
            
            if ai_answer:
                self.metrics["ai_routing_success"] += 1
                response_time = (time.time() - start_time) * 1000
                self._update_response_time(response_time)
                
                return {
                    "status": "campus",
                    "intent": "ai_routed",
                    "confidence": routing_result.confidence,
                    "context": "ai_enhanced",
                    "entities": routing_result.key_entities,
                    "response": ai_answer,
                    "response_type": "ai_campus_database",
                    "response_time_ms": round(response_time, 1),
                    "routing_reasoning": routing_result.reasoning,
                    "suggested_follow_ups": self._get_smart_follow_ups(routing_result.categories)
                }
            
            # Fallback to ML classifier if AI routing doesn't find answer
            ml_response = self.ml_classifier.classify_intent_ml(user_input, user_id)
            specific_answer = self._get_campus_answer_fallback(ml_response, user_input)
            
            response_time = (time.time() - start_time) * 1000
            self._update_response_time(response_time)
            
            return {
                "status": "campus",
                "intent": ml_response.intent,
                "confidence": ml_response.confidence,
                "context": ml_response.context,
                "entities": ml_response.entities,
                "response": specific_answer or "I can help with campus information. Could you be more specific about what you're looking for?",
                "response_type": "campus_database_fallback",
                "response_time_ms": round(response_time, 1),
                "suggested_follow_ups": self._get_campus_follow_ups(ml_response.intent)
            }
        
        else:
            # Handle as general question
            self.metrics["general_questions"] += 1
            general_response = self.general_handler.handle_general_question(user_input)
            
            if general_response:
                response_time = (time.time() - start_time) * 1000
                self._update_response_time(response_time)
                general_response["response_time_ms"] = round(response_time, 1)
                general_response["routing_reasoning"] = routing_result.reasoning
                return general_response
            
            # Final fallback
            response_time = (time.time() - start_time) * 1000
            self._update_response_time(response_time)
            
            return {
                "status": "general",
                "intent": "unknown",
                "confidence": 0.3,
                "context": "fallback",
                "entities": {},
                "response": "I'm here to help with campus information. What would you like to know about campus facilities, hours, or services?",
                "response_type": "fallback",
                "response_time_ms": round(response_time, 1),
                "suggested_follow_ups": [
                    "Where is the library?",
                    "What are the dining hall hours?",
                    "How do I contact IT support?"
                ]
            }
    
    def _get_campus_answer_fallback(self, ml_response, user_input: str) -> Optional[str]:
        """Fallback campus answer method (original logic)"""
        if not self.qa_database:
            return None
        
        categories = self.qa_database.get("campus_database", {}).get("categories", {})
        intent = ml_response.intent
        
        # Enhanced category selection based on content
        target_categories = self._determine_categories(user_input, intent)
        
        # Search through relevant categories
        for category in target_categories:
            if category in categories:
                questions = categories[category].get("questions", [])
                answer = self._find_best_match(user_input, questions)
                if answer:
                    return answer
        
        return None
    
    def _get_smart_follow_ups(self, categories: List[str]) -> List[str]:
        """Generate smart follow-ups based on AI-detected categories"""
        follow_ups = []
        
        category_suggestions = {
            "navigation": [
                "What are the hours for this location?",
                "How do I contact this department?",
                "What services are available here?"
            ],
            "hours": [
                "Where is this building located?",
                "What's the contact information?",
                "Are there special holiday hours?"
            ],
            "contact": [
                "What are their office hours?",
                "Where is their office located?",
                "What services do they provide?"
            ],
            "dining": [
                "What are the dining hall hours?",
                "What meal plans are available?",
                "Are there vegetarian options?"
            ],
            "events": [
                "When is this event?",
                "Where is this event located?",
                "How do I register for events?"
            ]
        }
        
        for category in categories:
            if category in category_suggestions:
                follow_ups.extend(category_suggestions[category])
        
        if not follow_ups:
            follow_ups = [
                "Where is the library?",
                "What time does the gym close?",
                "How do I contact IT support?"
            ]
        
        return follow_ups[:3]  # Return max 3 suggestions
    
    def _determine_categories(self, user_input: str, intent: str) -> List[str]:
        """Determine which categories to search based on user input and intent"""
        user_lower = user_input.lower()
        
        # Content-based category detection
        categories_to_search = []
        
        # Check for specific keywords that indicate category
        if any(word in user_lower for word in ['contact', 'support', 'help', 'phone', 'email', 'it', 'desk']):
            categories_to_search.append("contact")
        
        if any(word in user_lower for word in ['hours', 'time', 'open', 'close', 'schedule']):
            categories_to_search.append("hours")
        
        if any(word in user_lower for word in ['eat', 'food', 'dining', 'mess', 'cafeteria', 'meal', 'menu']):
            categories_to_search.append("dining")
        
        if any(word in user_lower for word in ['event', 'activities', 'club', 'meeting']):
            categories_to_search.append("events")
        
        if any(word in user_lower for word in ['how', 'procedure', 'process', 'apply', 'register']):
            categories_to_search.append("procedures")
        
        # Default intent-based mapping
        intent_mapping = {
            "find_location": "navigation",
            "get_hours": "hours", 
            "get_contact": "contact",
            "how_to": "procedures",
            "get_events": "events"
        }
        
        default_category = intent_mapping.get(intent, "navigation")
        if default_category not in categories_to_search:
            categories_to_search.append(default_category)
        
        return categories_to_search
    
    def _find_best_match(self, user_input: str, questions: List[Dict]) -> Optional[str]:
        """Find the best matching question using content word scoring"""
        user_lower = user_input.lower()
        
        # Remove common words that don't help with matching
        stop_words = {'where', 'is', 'the', 'a', 'an', 'how', 'do', 'i', 'can', 'what', 'when', 'to', 'for', 'on', 'in', 'at', 'of'}
        user_words = [word.strip('?,!.') for word in user_lower.split() if word.strip('?,!.') not in stop_words]
        
        best_score = 0
        best_answer = None
        
        for question_entry in questions:
            question = question_entry.get("question", "").lower()
            question_words = [word.strip('?,!.') for word in question.split() if word.strip('?,!.') not in stop_words]
            
            # Calculate overlap score
            common_words = set(user_words) & set(question_words)
            if common_words:
                # Score based on number of matching content words
                score = len(common_words)
                
                # Bonus for exact phrase matches
                if any(word in question for word in user_words if len(word) > 3):
                    score += 0.5
                
                if score > best_score:
                    best_score = score
                    best_answer = question_entry.get("answer", "")
        
        # Only return answer if we have a reasonable match
        return best_answer if best_score > 0 else None
    
    def _get_campus_follow_ups(self, intent: str) -> List[str]:
        """Get relevant follow-up suggestions for campus questions"""
        follow_ups = {
            "find_location": [
                "What are the hours for this location?",
                "How do I contact this department?",
                "What services are available here?"
            ],
            "get_hours": [
                "Where is this building located?",
                "What's the contact information?",
                "Are there special holiday hours?"
            ],
            "get_contact": [
                "What are their office hours?",
                "Where is their office located?",
                "What services do they provide?"
            ],
            "how_to": [
                "Who can I contact for help?",
                "Are there any requirements?",
                "What documents do I need?"
            ],
            "greeting": [
                "Where is the library?",
                "What time does the gym close?",
                "How do I connect to WiFi?"
            ]
        }
        
        return follow_ups.get(intent, [
            "Where is the library?",
            "What are the dining hall hours?",
            "How do I contact IT support?"
        ])
    
    def _update_response_time(self, response_time: float):
        """Update average response time metric"""
        current_avg = self.metrics["avg_response_time"]
        total_queries = self.metrics["total_queries"]
        
        if total_queries == 1:
            self.metrics["avg_response_time"] = response_time
        else:
            self.metrics["avg_response_time"] = (
                (current_avg * (total_queries - 1) + response_time) / total_queries
            )
    
    def get_mvp_stats(self) -> Dict:
        """Get simplified stats for MVP demo"""
        total = max(self.metrics["total_queries"], 1)
        
        return {
            "total_queries": self.metrics["total_queries"],
            "campus_questions": self.metrics["campus_questions"],
            "general_questions": self.metrics["general_questions"],
            "campus_percentage": round((self.metrics["campus_questions"] / total) * 100, 1),
            "general_percentage": round((self.metrics["general_questions"] / total) * 100, 1),
            "avg_response_time_ms": round(self.metrics["avg_response_time"], 1),
            "ai_routing_success": self.metrics["ai_routing_success"],
            "ai_success_rate": round((self.metrics["ai_routing_success"] / max(self.metrics["campus_questions"], 1)) * 100, 1),
            "gemini_available": self.general_handler.gemini.is_available()
        }
    
    def demo_conversation(self):
        """Run a demonstration conversation for Enhanced MVP"""
        print("\n🎯 NEXi Brain Enhanced MVP - Live Demonstration")
        print("=" * 60)
        print("🚀 Features: AI-powered routing, enhanced accuracy, intelligent analysis")
        
        demo_questions = [
            "Hello NEXi!",
            "Where is the library?",
            "Where is mess?",
            "Where can I find IT support?",
            "What time does the dining hall close?",
            "Can I meet Vice Chancellor?",
            "What's 2 + 2?",
            "Thanks for your help!"
        ]
        
        for i, question in enumerate(demo_questions, 1):
            print(f"\n{i}. Student: {question}")
            response = self.process_query(question, f"demo_student_{i}")
            
            print(f"   NEXi: {response['response']}")
            routing_info = f"{response['response_type']} | {response['response_time_ms']}ms"
            if 'routing_reasoning' in response:
                routing_info += f" | AI: {response['routing_reasoning']}"
            print(f"   [{routing_info}]")
        
        # Show enhanced final stats
        stats = self.get_mvp_stats()
        print(f"\n📊 Enhanced Demo Statistics:")
        print(f"   Campus Questions: {stats['campus_questions']} ({stats['campus_percentage']}%)")
        print(f"   General Questions: {stats['general_questions']} ({stats['general_percentage']}%)")
        print(f"   AI Routing Success: {stats['ai_routing_success']} ({stats['ai_success_rate']}%)")
        print(f"   Average Response Time: {stats['avg_response_time_ms']}ms")
        print(f"   Gemini AI: {'✅ Enabled' if stats['gemini_available'] else '❌ Offline (keyword fallback)'}")
        print(f"\n🎉 Enhanced MVP Demonstration Complete!")
        print("   Ready for team integration and live presentation!")

# MVP Integration function for other teams
def get_nexi_response(question: str) -> str:
    """
    Simple function for other teams to integrate with Brain system
    
    Usage:
        from brain.nexi_brain_mvp import get_nexi_response
        answer = get_nexi_response("Where is the library?")
    """
    # Global brain instance for performance
    if not hasattr(get_nexi_response, 'brain'):
        get_nexi_response.brain = NEXiBrainMVP()
    
    response = get_nexi_response.brain.process_query(question)
    return response['response']

# Test function
def test_mvp_system():
    """Test the MVP system"""
    brain = NEXiBrainMVP()
    brain.demo_conversation()

if __name__ == "__main__":
    test_mvp_system()
