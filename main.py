
import json
import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Intent:
    name: str
    keywords: List[str]
    priority: int = 1  # Higher = more priority

@dataclass
class Response:
    intent: str
    text: str
    confidence: float

class SimpleIntentClassifier:
    """
    Week 1: Simple keyword-based intent classifier
    Week 2: Will upgrade to ML-based classification
    """
    
    def __init__(self):
        self.intents = self._load_default_intents()
        self.responses = self._load_default_responses()
    
    def _load_default_intents(self) -> List[Intent]:
        """Define your intents with keywords"""
        return [
            Intent("find_location", ["where", "location", "find", "directions", "building", "room"], 3),
            Intent("get_hours", ["hours", "open", "close", "time", "when", "schedule"], 3),
            Intent("get_contact", ["contact", "phone", "email", "call", "reach", "number"], 2),
            Intent("how_to", ["how", "register", "access", "get", "obtain", "connect"], 2),
            Intent("get_events", ["events", "activities", "happening", "clubs", "sports"], 1),
            Intent("greeting", ["hello", "hi", "hey", "good morning", "good afternoon"], 2),
            Intent("goodbye", ["bye", "goodbye", "see you", "thanks", "thank you"], 1),
            Intent("unknown", [], 0)  # Fallback
        ]
    
    def _load_default_responses(self) -> Dict[str, List[str]]:
        """Default responses for each intent"""
        return {
            "find_location": [
                "I can help you find locations on campus. Which building or room are you looking for?",
                "Let me help you with directions. What location do you need?"
            ],
            "get_hours": [
                "I can tell you about campus hours. Which facility are you asking about?",
                "What location's hours would you like to know?"
            ],
            "get_contact": [
                "I can help you find contact information. Which department do you need?",
                "Who are you trying to reach? I can provide contact details."
            ],
            "how_to": [
                "I can help you with campus procedures. What do you need help with?",
                "What process do you need assistance with?"
            ],
            "get_events": [
                "I can tell you about campus events. What type of activities interest you?",
                "What kind of events are you looking for?"
            ],
            "greeting": [
                "Hello! I'm NEXi, your campus assistant. How can I help you today?",
                "Hi there! What can I help you with on campus?"
            ],
            "goodbye": [
                "Goodbye! Feel free to ask me anything about campus.",
                "See you later! I'm here whenever you need campus information."
            ],
            "unknown": [
                "I'm not sure I understand. Could you rephrase your question?",
                "I'm still learning! Can you ask me about campus locations, hours, or services?"
            ]
        }
    
    def preprocess_text(self, text: str) -> str:
        """Clean and normalize input text"""
        # Convert to lowercase
        text = text.lower().strip()
        
        # Remove punctuation
        text = re.sub(r'[^\w\s]', '', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text
    
    def classify_intent(self, user_input: str) -> Response:
        """
        Classify user input into an intent
        Returns: Response object with intent, confidence score
        """
        processed_input = self.preprocess_text(user_input)
        words = processed_input.split()
        
        # Score each intent
        intent_scores = {}
        
        for intent in self.intents:
            score = 0
            for keyword in intent.keywords:
                if keyword in processed_input:
                    # Exact word match gets higher score
                    if keyword in words:
                        score += 2 * intent.priority
                    else:
                        score += 1 * intent.priority
            
            intent_scores[intent.name] = score
        
        # Find best matching intent
        best_intent = max(intent_scores.items(), key=lambda x: x[1])
        intent_name, score = best_intent
        
        # If no keywords matched, return unknown
        if score == 0:
            intent_name = "unknown"
            confidence = 0.1
        else:
            # Simple confidence calculation
            max_possible_score = max(len(intent.keywords) * 2 * intent.priority 
                                   for intent in self.intents if intent.name != "unknown")
            confidence = min(score / max_possible_score, 1.0)
        
        return Response(
            intent=intent_name,
            text=self.get_response(intent_name),
            confidence=confidence
        )
    
    def get_response(self, intent: str) -> str:
        """Get a response for the given intent"""
        if intent in self.responses:
            # For now, return first response. Later: randomize or personalize
            return self.responses[intent][0]
        return self.responses["unknown"][0]
    
    def add_training_data(self, user_input: str, correct_intent: str):
        """
        Add training example for later ML model improvement
        For Week 1: Just log it. Week 2: Use for ML training
        """
        # For now, just print for debugging
        print(f"Training data: '{user_input}' -> {correct_intent}")
        
        # Later: Store in database for ML training

# Testing and Demo Functions
def test_classifier():
    """Test the classifier with sample questions"""
    classifier = SimpleIntentClassifier()
    
    test_questions = [
        "Where is the library?",
        "What time does the cafeteria close?",
        "How do I connect to WiFi?",
        "Hello NEXi",
        "Who do I contact for IT support?",
        "Thanks for your help",
        "I want to eat pizza"  # Should be unknown
    ]
    
    print("🧠 Testing Brain Team Intent Classifier\n")
    print("-" * 50)
    
    for question in test_questions:
        response = classifier.classify_intent(question)
        print(f"Q: {question}")
        print(f"Intent: {response.intent} (confidence: {response.confidence:.2f})")
        print(f"Response: {response.text}")
        print("-" * 50)

if __name__ == "__main__":
    test_classifier()