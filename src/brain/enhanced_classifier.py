"""
Enhanced Intent Classifier for Week 2
Brain Team: Krishna, Rajat
"""

import json
import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path
import random

@dataclass
class Intent:
    name: str
    keywords: List[str]
    priority: int = 1
    contexts: List[str] = None  # New: Context categories

@dataclass
class Response:
    intent: str
    text: str
    confidence: float
    context: str = None  # New: Response context

@dataclass
class TrainingExample:
    question: str
    intent: str
    category: str

class EnhancedIntentClassifier:
    """
    Week 2: Enhanced intent classifier with ML preparation
    Features: Context awareness, expanded training data, fallback system
    """
    
    def __init__(self, data_path: str = "data/campus_qa"):
        self.data_path = Path(data_path)
        self.intents = self._load_enhanced_intents()
        self.responses = self._load_enhanced_responses()
        self.training_data = self._load_training_data()
        self.conversation_context = []  # Track conversation history
    
    def _load_enhanced_intents(self) -> List[Intent]:
        """Enhanced intents with context categories"""
        return [
            Intent("find_location", 
                   ["where", "location", "find", "directions", "building", "room", "parking", "eat", "dining"], 
                   3, ["navigation", "dining", "general"]),
            Intent("get_hours", 
                   ["hours", "open", "close", "time", "when", "schedule"], 
                   3, ["hours", "general"]),
            Intent("get_contact", 
                   ["contact", "phone", "email", "call", "reach", "number", "who"], 
                   2, ["support", "emergency"]),
            Intent("how_to", 
                   ["how", "register", "access", "get", "obtain", "connect", "drop", "schedule"], 
                   2, ["academic", "technology", "services"]),
            Intent("get_events", 
                   ["events", "activities", "happening", "clubs", "sports", "groups", "fair"], 
                   2, ["events", "academic"]),
            Intent("greeting", 
                   ["hello", "hi", "hey", "good morning", "good afternoon", "help me"], 
                   2, ["social"]),
            Intent("goodbye", 
                   ["bye", "goodbye", "see you", "thanks", "thank you"], 
                   1, ["social"]),
            Intent("unknown", [], 0, ["general"])
        ]
    
    def _load_enhanced_responses(self) -> Dict[str, Dict[str, List[str]]]:
        """Context-aware responses organized by category"""
        return {
            "find_location": {
                "navigation": [
                    "I can help you navigate campus. Which building or location are you looking for?",
                    "Let me help you find your way. What specific place do you need directions to?"
                ],
                "dining": [
                    "I can help you find places to eat on campus. Are you looking for the dining hall, cafeteria, or other food options?",
                    "Let me help you find dining options. What type of food or dining location are you interested in?"
                ],
                "general": [
                    "I can help you find locations on campus. Which building or room are you looking for?",
                    "Let me help you with directions. What location do you need?"
                ]
            },
            "get_hours": {
                "hours": [
                    "I can tell you about operating hours. Which facility are you asking about?",
                    "What location's hours would you like to know?"
                ],
                "general": [
                    "I can help with hours information. What facility or service are you asking about?"
                ]
            },
            "get_contact": {
                "support": [
                    "I can help you find contact information. Which department or service do you need?",
                    "Who are you trying to reach? I can provide contact details for campus services."
                ],
                "emergency": [
                    "For emergencies, call campus security at [EMERGENCY NUMBER]. For other contacts, which department do you need?"
                ]
            },
            "how_to": {
                "academic": [
                    "I can help with academic procedures. What do you need assistance with?",
                    "Let me help you with academic processes. What specifically do you need to do?"
                ],
                "technology": [
                    "I can help with campus technology. What system or service do you need help accessing?",
                    "Let me assist you with tech support. What technology issue can I help with?"
                ],
                "services": [
                    "I can help with campus services. What process do you need guidance on?",
                    "Let me help you with campus procedures. What service do you need help with?"
                ]
            },
            "get_events": {
                "events": [
                    "I can tell you about campus events. What type of activities interest you?",
                    "What kind of events are you looking for? Academic, social, or sports?"
                ],
                "academic": [
                    "I can help you find academic activities. Are you looking for study groups, workshops, or other academic events?"
                ]
            },
            "greeting": {
                "social": [
                    "Hello! I'm NEXi, your campus assistant. How can I help you today?",
                    "Hi there! What can I help you with on campus?",
                    "Good day! I'm here to help with any campus questions you have."
                ]
            },
            "goodbye": {
                "social": [
                    "Goodbye! Feel free to ask me anything about campus anytime.",
                    "See you later! I'm here whenever you need campus information.",
                    "Take care! Don't hesitate to reach out if you need more help."
                ]
            },
            "unknown": {
                "general": [
                    "I'm not sure I understand. Could you rephrase your question about campus?",
                    "I'm still learning! Can you ask me about campus locations, hours, contacts, or services?",
                    "I didn't quite catch that. Try asking about campus facilities, events, or how to do something on campus."
                ]
            }
        }
    
    def _load_training_data(self) -> List[TrainingExample]:
        """Load training data from JSON file"""
        try:
            json_path = self.data_path / "essential_questions.json"
            with open(json_path, 'r') as f:
                data = json.load(f)
            
            return [
                TrainingExample(q["question"], q["intent"], q["category"])
                for q in data["campus_questions"]
            ]
        except FileNotFoundError:
            print(f"Warning: Training data file not found at {json_path}")
            return []
    
    def preprocess_text(self, text: str) -> str:
        """Enhanced text preprocessing"""
        # Convert to lowercase
        text = text.lower().strip()
        
        # Handle common contractions
        contractions = {
            "what's": "what is",
            "where's": "where is",
            "how's": "how is",
            "when's": "when is",
            "can't": "cannot",
            "won't": "will not"
        }
        
        for contraction, expansion in contractions.items():
            text = text.replace(contraction, expansion)
        
        # Remove punctuation
        text = re.sub(r'[^\w\s]', '', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text
    
    def classify_intent(self, user_input: str) -> Response:
        """Enhanced intent classification with context awareness"""
        processed_input = self.preprocess_text(user_input)
        words = processed_input.split()
        
        # Score each intent
        intent_scores = {}
        context_scores = {}
        
        for intent in self.intents:
            score = 0
            best_context = "general"
            
            for keyword in intent.keywords:
                if keyword in processed_input:
                    # Exact word match gets higher score
                    if keyword in words:
                        score += 2 * intent.priority
                    else:
                        score += 1 * intent.priority
            
            # Context bonus: check if recent conversation suggests a context
            if self.conversation_context and intent.contexts:
                recent_context = self.conversation_context[-1] if self.conversation_context else None
                if recent_context in intent.contexts:
                    score += 1  # Small bonus for context continuity
                    best_context = recent_context
            
            intent_scores[intent.name] = score
            context_scores[intent.name] = best_context
        
        # Find best matching intent
        best_intent = max(intent_scores.items(), key=lambda x: x[1])
        intent_name, score = best_intent
        context = context_scores[intent_name]
        
        # Enhanced fallback system
        if score == 0:
            intent_name = "unknown"
            confidence = 0.1
            context = "general"
        else:
            # Improved confidence calculation
            max_possible_score = max(len(intent.keywords) * 2 * intent.priority 
                                   for intent in self.intents if intent.name != "unknown")
            confidence = min(score / max_possible_score, 1.0)
        
        # Update conversation context
        if intent_name != "unknown":
            self.conversation_context.append(context)
            # Keep only last 3 contexts
            self.conversation_context = self.conversation_context[-3:]
        
        return Response(
            intent=intent_name,
            text=self.get_response(intent_name, context),
            confidence=confidence,
            context=context
        )
    
    def get_response(self, intent: str, context: str = "general") -> str:
        """Get context-aware response"""
        if intent in self.responses:
            if context in self.responses[intent]:
                responses = self.responses[intent][context]
            else:
                # Fallback to general context
                responses = self.responses[intent].get("general", 
                                                     list(self.responses[intent].values())[0])
            
            # Randomize response selection for variety
            return random.choice(responses)
        
        return random.choice(self.responses["unknown"]["general"])
    
    def add_training_data(self, user_input: str, correct_intent: str, category: str = "general"):
        """Enhanced training data collection"""
        example = TrainingExample(user_input, correct_intent, category)
        self.training_data.append(example)
        
        # Log for debugging
        print(f"Training data added: '{user_input}' -> {correct_intent} ({category})")
        
        # TODO Week 2: Store in database for ML training
    
    def get_training_stats(self) -> Dict:
        """Get statistics about training data"""
        intent_counts = {}
        category_counts = {}
        
        for example in self.training_data:
            intent_counts[example.intent] = intent_counts.get(example.intent, 0) + 1
            category_counts[example.category] = category_counts.get(example.category, 0) + 1
        
        return {
            "total_examples": len(self.training_data),
            "intent_distribution": intent_counts,
            "category_distribution": category_counts
        }


# Enhanced Testing Functions
def test_enhanced_classifier():
    """Test the enhanced classifier"""
    classifier = EnhancedIntentClassifier()
    
    # Show training data stats
    stats = classifier.get_training_stats()
    print("📊 Training Data Statistics:")
    print(f"Total examples: {stats['total_examples']}")
    print(f"Intent distribution: {stats['intent_distribution']}")
    print(f"Category distribution: {stats['category_distribution']}")
    print("\n" + "="*60 + "\n")
    
    test_questions = [
        "Where is the library?",
        "What time does the cafeteria close?",
        "How do I connect to WiFi?",
        "Hello NEXi",
        "Who do I contact for IT support?",
        "When is the career fair?",
        "Where can I eat on campus?",
        "What are the gym hours?",
        "How do I register for classes?",
        "Thanks for your help"
    ]
    
    print("🧠 Testing Enhanced Brain Team Intent Classifier\n")
    print("-" * 60)
    
    for question in test_questions:
        response = classifier.classify_intent(question)
        print(f"Q: {question}")
        print(f"Intent: {response.intent} | Context: {response.context} | Confidence: {response.confidence:.2f}")
        print(f"Response: {response.text}")
        print("-" * 60)

if __name__ == "__main__":
    test_enhanced_classifier()
