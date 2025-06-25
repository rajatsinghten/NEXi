"""
Week 2: Advanced Fallback and Context Management System
Brain Team: Krishna, Rajat

This module provides sophisticated fallback handling, context management,
and clarification question generation for the intent classification system.
"""

import json
import random
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

@dataclass
class FallbackStrategy:
    """Defines different fallback strategies based on confidence levels"""
    name: str
    confidence_range: Tuple[float, float]
    strategy_type: str  # "clarify", "suggest", "redirect", "unknown"
    templates: List[str]
    follow_up_questions: List[str] = field(default_factory=list)

@dataclass
class ContextMemory:
    """Stores conversation context and user preferences"""
    recent_intents: List[str] = field(default_factory=list)
    mentioned_entities: Dict[str, str] = field(default_factory=list)
    user_preferences: Dict[str, str] = field(default_factory=dict)
    failed_queries: List[str] = field(default_factory=list)
    successful_queries: List[str] = field(default_factory=list)

class FallbackManager:
    """
    Advanced fallback system that provides intelligent responses
    when the primary classifier is uncertain or fails
    """
    
    def __init__(self, database_path: str = "data/campus_qa"):
        self.database_path = Path(database_path)
        self.fallback_strategies = self._load_fallback_strategies()
        self.context_memory = {}
        self.suggestion_database = self._load_suggestion_database()
        
    def _load_fallback_strategies(self) -> List[FallbackStrategy]:
        """Define fallback strategies for different confidence levels"""
        return [
            FallbackStrategy(
                name="high_confidence_clarification",
                confidence_range=(0.5, 0.7),
                strategy_type="clarify",
                templates=[
                    "I think you're asking about {intent}, but I want to make sure. {clarification_question}",
                    "It seems like you need help with {intent}. {clarification_question}",
                    "I believe you're looking for information about {intent}. {clarification_question}"
                ],
                follow_up_questions=[
                    "Could you provide more details?",
                    "Can you be more specific?",
                    "What exactly would you like to know?",
                    "Which aspect interests you most?"
                ]
            ),
            
            FallbackStrategy(
                name="medium_confidence_suggestion",
                confidence_range=(0.3, 0.5),
                strategy_type="suggest",
                templates=[
                    "I'm not entirely sure what you're looking for. Are you asking about {suggestions}?",
                    "I can help with several things. Are you interested in {suggestions}?",
                    "Let me suggest some options: {suggestions}. Which one matches what you need?"
                ],
                follow_up_questions=[]
            ),
            
            FallbackStrategy(
                name="low_confidence_redirect",
                confidence_range=(0.1, 0.3),
                strategy_type="redirect",
                templates=[
                    "I'm having trouble understanding. I can help you with {popular_topics}.",
                    "I want to make sure I give you the right information. I'm great at helping with {popular_topics}.",
                    "Let me help you find what you need. I can assist with {popular_topics}."
                ],
                follow_up_questions=[
                    "What campus topic can I help you with?",
                    "Try asking about locations, hours, contacts, or procedures.",
                    "What specific information are you looking for?"
                ]
            ),
            
            FallbackStrategy(
                name="very_low_confidence_unknown",
                confidence_range=(0.0, 0.1),
                strategy_type="unknown",
                templates=[
                    "I didn't understand that question. {help_prompt}",
                    "I'm not sure how to help with that. {help_prompt}",
                    "That's outside my knowledge area. {help_prompt}"
                ],
                follow_up_questions=[
                    "Try asking about campus locations, hours, or services.",
                    "I can help you find buildings, get contact information, or learn about procedures.",
                    "Ask me about specific campus facilities or how to do something on campus."
                ]
            )
        ]
    
    def _load_suggestion_database(self) -> Dict[str, List[str]]:
        """Load common suggestions based on failed queries"""
        return {
            "location_related": [
                "finding campus buildings",
                "getting directions", 
                "locating services",
                "parking information"
            ],
            "time_related": [
                "facility hours",
                "schedule information",
                "deadline dates",
                "event times"
            ],
            "contact_related": [
                "department phone numbers",
                "staff contact information", 
                "emergency contacts",
                "service desk locations"
            ],
            "procedure_related": [
                "registration procedures",
                "how to access services",
                "step-by-step guides",
                "requirements and deadlines"
            ],
            "service_related": [
                "available campus services",
                "student resources",
                "technology support",
                "health and wellness"
            ]
        }
    
    def get_fallback_response(self, user_input: str, confidence: float, 
                            predicted_intent: str, context: ContextMemory, 
                            user_id: str = "default") -> Tuple[str, List[str]]:
        """
        Generate appropriate fallback response based on confidence level
        Returns: (response_text, suggested_follow_ups)
        """
        
        # Update context with failed query
        if user_id not in self.context_memory:
            self.context_memory[user_id] = ContextMemory()
        
        self.context_memory[user_id].failed_queries.append(user_input)
        
        # Find appropriate strategy
        strategy = self._select_strategy(confidence)
        
        # Generate response based on strategy
        if strategy.strategy_type == "clarify":
            return self._generate_clarification_response(
                user_input, predicted_intent, strategy, context
            )
        elif strategy.strategy_type == "suggest":
            return self._generate_suggestion_response(
                user_input, strategy, context
            )
        elif strategy.strategy_type == "redirect":
            return self._generate_redirect_response(
                user_input, strategy, context
            )
        else:  # unknown
            return self._generate_unknown_response(
                user_input, strategy, context
            )
    
    def _select_strategy(self, confidence: float) -> FallbackStrategy:
        """Select appropriate fallback strategy based on confidence"""
        for strategy in self.fallback_strategies:
            min_conf, max_conf = strategy.confidence_range
            if min_conf <= confidence <= max_conf:
                return strategy
        
        # Default to unknown strategy
        return self.fallback_strategies[-1]
    
    def _generate_clarification_response(self, user_input: str, predicted_intent: str,
                                       strategy: FallbackStrategy, 
                                       context: ContextMemory) -> Tuple[str, List[str]]:
        """Generate clarification questions for medium-high confidence predictions"""
        
        intent_readable = predicted_intent.replace('_', ' ')
        clarification_q = random.choice(strategy.follow_up_questions)
        
        template = random.choice(strategy.templates)
        response = template.format(
            intent=intent_readable,
            clarification_question=clarification_q
        )
        
        # Generate specific follow-ups based on intent
        follow_ups = self._get_intent_specific_follow_ups(predicted_intent)
        
        return response, follow_ups
    
    def _generate_suggestion_response(self, user_input: str, strategy: FallbackStrategy,
                                    context: ContextMemory) -> Tuple[str, List[str]]:
        """Generate suggestions based on input patterns"""
        
        # Analyze input to suggest relevant categories
        suggestions = self._analyze_input_for_suggestions(user_input, context)
        suggestions_text = ", ".join(suggestions)
        
        template = random.choice(strategy.templates)
        response = template.format(suggestions=suggestions_text)
        
        # Create actionable follow-ups
        follow_ups = [f"Tell me about {suggestion}" for suggestion in suggestions[:3]]
        
        return response, follow_ups
    
    def _generate_redirect_response(self, user_input: str, strategy: FallbackStrategy,
                                  context: ContextMemory) -> Tuple[str, List[str]]:
        """Redirect to popular/common topics"""
        
        popular_topics = [
            "finding campus locations",
            "getting facility hours", 
            "contacting departments",
            "learning campus procedures"
        ]
        
        topics_text = ", ".join(popular_topics)
        help_prompt = random.choice(strategy.follow_up_questions)
        
        template = random.choice(strategy.templates)
        response = template.format(popular_topics=topics_text)
        
        return response, popular_topics
    
    def _generate_unknown_response(self, user_input: str, strategy: FallbackStrategy,
                                 context: ContextMemory) -> Tuple[str, List[str]]:
        """Handle completely unknown queries"""
        
        help_prompt = random.choice(strategy.follow_up_questions)
        template = random.choice(strategy.templates)
        response = template.format(help_prompt=help_prompt)
        
        # Suggest based on recent context if available
        if context.recent_intents:
            recent_intent = context.recent_intents[-1]
            follow_ups = self._get_intent_specific_follow_ups(recent_intent)
        else:
            follow_ups = [
                "Where is [building name]?",
                "What time does [facility] close?",
                "How do I [do something]?",
                "Who do I contact for [service]?"
            ]
        
        return response, follow_ups
    
    def _analyze_input_for_suggestions(self, user_input: str, 
                                     context: ContextMemory) -> List[str]:
        """Analyze user input to suggest relevant categories"""
        
        input_lower = user_input.lower()
        suggestions = []
        
        # Pattern matching for suggestions
        if any(word in input_lower for word in ["where", "find", "location", "building"]):
            suggestions.extend(self.suggestion_database["location_related"][:2])
        
        if any(word in input_lower for word in ["time", "when", "hours", "open", "close"]):
            suggestions.extend(self.suggestion_database["time_related"][:2])
        
        if any(word in input_lower for word in ["contact", "phone", "email", "call"]):
            suggestions.extend(self.suggestion_database["contact_related"][:2])
        
        if any(word in input_lower for word in ["how", "register", "access", "get"]):
            suggestions.extend(self.suggestion_database["procedure_related"][:2])
        
        # If no patterns match, use popular suggestions
        if not suggestions:
            suggestions = [
                "campus locations",
                "facility hours", 
                "contact information",
                "campus procedures"
            ]
        
        return suggestions[:4]  # Limit to 4 suggestions
    
    def _get_intent_specific_follow_ups(self, intent: str) -> List[str]:
        """Generate follow-up questions specific to an intent"""
        
        follow_up_map = {
            "find_location": [
                "Which building are you looking for?",
                "Do you need directions to a specific facility?",
                "Are you looking for dining, academic, or service buildings?"
            ],
            "get_hours": [
                "Which facility's hours do you need?",
                "Are you asking about today's hours or general schedule?",
                "Do you need hours for academic or service buildings?"
            ],
            "get_contact": [
                "Which department do you need to contact?",
                "Are you looking for a phone number or email?",
                "Do you need emergency or regular contact information?"
            ],
            "how_to": [
                "What process do you need help with?",
                "Are you asking about academic or administrative procedures?",
                "Do you need technology help or general guidance?"
            ],
            "get_events": [
                "What type of events interest you?",
                "Are you looking for academic, social, or sports events?",
                "Do you need information about today or upcoming events?"
            ]
        }
        
        return follow_up_map.get(intent, [
            "Can you be more specific?",
            "What exactly are you looking for?",
            "Which aspect would you like to know more about?"
        ])
    
    def track_successful_resolution(self, user_id: str, original_query: str, 
                                  final_intent: str, user_satisfaction: bool = True):
        """Track when a fallback successfully leads to resolution"""
        
        if user_id not in self.context_memory:
            self.context_memory[user_id] = ContextMemory()
        
        context = self.context_memory[user_id]
        
        if user_satisfaction:
            context.successful_queries.append(original_query)
            
            # Remove from failed queries if it was there
            if original_query in context.failed_queries:
                context.failed_queries.remove(original_query)
        
        # Update user preferences based on successful resolutions
        context.user_preferences[final_intent] = context.user_preferences.get(final_intent, 0) + 1
    
    def get_personalized_suggestions(self, user_id: str) -> List[str]:
        """Get personalized suggestions based on user history"""
        
        if user_id not in self.context_memory:
            return ["campus locations", "facility hours", "contact information"]
        
        context = self.context_memory[user_id]
        
        # Sort preferences by frequency
        sorted_prefs = sorted(
            context.user_preferences.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        # Convert to readable suggestions
        suggestions = []
        for intent, _ in sorted_prefs[:3]:
            suggestions.append(intent.replace('_', ' '))
        
        return suggestions if suggestions else [
            "campus locations", "facility hours", "contact information"
        ]
    
    def get_context_stats(self, user_id: str) -> Dict:
        """Get statistics about user's interaction patterns"""
        
        if user_id not in self.context_memory:
            return {"error": "No context found for user"}
        
        context = self.context_memory[user_id]
        
        return {
            "total_failed_queries": len(context.failed_queries),
            "total_successful_queries": len(context.successful_queries),
            "success_rate": len(context.successful_queries) / 
                          (len(context.successful_queries) + len(context.failed_queries))
                          if (len(context.successful_queries) + len(context.failed_queries)) > 0 else 0,
            "top_preferences": dict(sorted(
                context.user_preferences.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:5]),
            "recent_intents": context.recent_intents[-5:],
            "mentioned_entities": dict(context.mentioned_entities)
        }


def test_fallback_system():
    """Test the fallback management system"""
    print("🔄 Testing Advanced Fallback System")
    print("=" * 50)
    
    fallback_manager = FallbackManager()
    
    # Test different confidence levels
    test_cases = [
        ("Where building?", 0.65, "find_location"),  # High confidence clarification
        ("I need help with something", 0.4, "unknown"),  # Medium confidence suggestion
        ("Campus stuff", 0.2, "unknown"),  # Low confidence redirect
        ("Banana elephant purple", 0.05, "unknown"),  # Very low confidence unknown
    ]
    
    context = ContextMemory()
    
    for i, (query, confidence, predicted_intent) in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: '{query}' (confidence: {confidence})")
        print("-" * 30)
        
        response, follow_ups = fallback_manager.get_fallback_response(
            query, confidence, predicted_intent, context, "test_user"
        )
        
        print(f"Response: {response}")
        print(f"Follow-ups: {follow_ups}")
    
    # Test personalization
    print(f"\n📊 Context Statistics:")
    stats = fallback_manager.get_context_stats("test_user")
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    print("\n✅ Fallback system testing completed!")

if __name__ == "__main__":
    test_fallback_system()
