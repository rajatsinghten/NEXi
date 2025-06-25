"""
Week 2: ML-Based Intent Classification System
Brain Team: Krishna, Rajat

This implements a production-ready intent classifier using:
- TF-IDF vectorization for better text understanding
- Multiple ML algorithms (Naive Bayes, SVM, Random Forest)
- Confidence thresholding for unknown detection
- Advanced fallback system
- Enhanced context awareness
"""

import json
import re
import pickle
from typing import Dict, List, Tuple, Optional, Union
from dataclasses import dataclass, field
from pathlib import Path
import random
import numpy as np
import pandas as pd
from datetime import datetime

# ML imports
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix
import nltk
from nltk.corpus import stopwords

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

@dataclass
class Intent:
    name: str
    keywords: List[str]
    priority: int = 1
    contexts: List[str] = field(default_factory=list)
    ml_examples: List[str] = field(default_factory=list)

@dataclass
class Response:
    intent: str
    text: str
    confidence: float
    context: str = None
    fallback_reason: str = None
    entities: Dict[str, str] = field(default_factory=dict)

@dataclass
class TrainingExample:
    question: str
    intent: str
    category: str
    entities: Dict[str, str] = field(default_factory=dict)

@dataclass
class ConversationState:
    user_id: str = "default"
    context_history: List[str] = field(default_factory=list)
    last_intent: str = None
    entity_memory: Dict[str, str] = field(default_factory=dict)
    conversation_start: datetime = field(default_factory=datetime.now)

class MLIntentClassifier:
    """
    Week 2: Advanced ML-based intent classifier
    
    Features:
    - Multiple ML algorithms with ensemble voting
    - TF-IDF vectorization with custom preprocessing
    - Confidence-based fallback system
    - Entity extraction
    - Multi-turn conversation awareness
    - Performance monitoring
    """
    
    def __init__(self, data_path: str = "data/campus_qa", model_path: str = "data/models"):
        self.data_path = Path(data_path)
        self.model_path = Path(model_path)
        self.model_path.mkdir(exist_ok=True)
        
        # ML components
        self.vectorizer = None
        self.classifiers = {}
        self.is_trained = False
        
        # Configuration
        self.confidence_threshold = 0.6  # Minimum confidence for valid classification
        self.unknown_threshold = 0.3     # Below this, classify as unknown
        
        # Initialize components
        self.stop_words = set(stopwords.words('english'))
        
        # Load data and train models
        self.intents = self._load_enhanced_intents()
        self.responses = self._load_enhanced_responses()
        self.training_data = self._load_training_data()
        self.conversation_states = {}
        
        # Entity patterns for basic NER
        self.entity_patterns = self._load_entity_patterns()
        
        # Train ML models if we have enough data
        if len(self.training_data) >= 10:
            self.train_ml_models()
    
    def _load_enhanced_intents(self) -> List[Intent]:
        """Enhanced intents with ML training examples"""
        return [
            Intent("find_location", 
                   ["where", "location", "find", "directions", "building", "room", "parking", "eat", "dining"],
                   3, ["navigation", "dining", "general"],
                   ["Where is the library?", "How do I get to the cafeteria?", "Find parking"]),
            
            Intent("get_hours", 
                   ["hours", "open", "close", "time", "when", "schedule"],
                   3, ["hours", "general"],
                   ["What time does the gym open?", "When does the library close?", "Operating hours"]),
            
            Intent("get_contact", 
                   ["contact", "phone", "email", "call", "reach", "number", "who"],
                   2, ["support", "emergency"],
                   ["Who do I contact for help?", "What's the phone number?", "How to reach support"]),
            
            Intent("how_to", 
                   ["how", "register", "access", "get", "obtain", "connect", "drop", "schedule"],
                   2, ["academic", "technology", "services"],
                   ["How do I register for classes?", "How to connect to WiFi?", "How to access portal"]),
            
            Intent("get_events", 
                   ["events", "activities", "happening", "clubs", "sports", "groups", "fair"],
                   2, ["events", "academic"],
                   ["What events are happening?", "Any clubs to join?", "Sports activities"]),
            
            Intent("greeting", 
                   ["hello", "hi", "hey", "good morning", "good afternoon", "help me"],
                   2, ["social"],
                   ["Hello there", "Good morning", "Hi NEXi", "Can you help me"]),
            
            Intent("goodbye", 
                   ["bye", "goodbye", "see you", "thanks", "thank you", "that's all"],
                   1, ["social"],
                   ["Goodbye", "Thanks for helping", "See you later", "That's all I needed"]),
            
            Intent("unknown", [], 0, ["general"], [])
        ]
    
    def _load_enhanced_responses(self) -> Dict[str, Dict[str, List[str]]]:
        """Context-aware responses with fallback support"""
        return {
            "find_location": {
                "navigation": [
                    "I can help you navigate campus. Which building or location are you looking for?",
                    "Let me help you find your way. What specific place do you need directions to?",
                    "I know the campus layout well. What location would you like to find?"
                ],
                "dining": [
                    "I can help you find places to eat on campus. Are you looking for the dining hall, cafeteria, or other food options?",
                    "Let me help you find dining options. What type of food or dining location are you interested in?",
                    "There are several dining options on campus. What kind of food are you looking for?"
                ],
                "general": [
                    "I can help you find locations on campus. Which building or room are you looking for?",
                    "Let me help you with directions. What location do you need?",
                    "What campus location can I help you find today?"
                ]
            },
            "get_hours": {
                "hours": [
                    "I can tell you about operating hours. Which facility are you asking about?",
                    "What location's hours would you like to know?",
                    "I have current hours for most campus facilities. Which one interests you?"
                ],
                "general": [
                    "I can help with hours information. What facility or service are you asking about?",
                    "What operating hours do you need to know?"
                ]
            },
            "get_contact": {
                "support": [
                    "I can help you find contact information. Which department or service do you need?",
                    "Who are you trying to reach? I can provide contact details for campus services.",
                    "What department's contact information can I help you find?"
                ],
                "emergency": [
                    "For emergencies, call campus security at 911 or (555) 123-4567. For other contacts, which department do you need?",
                    "Emergency contacts: Campus Security (555) 123-4567. What other contact info do you need?"
                ]
            },
            "how_to": {
                "academic": [
                    "I can help with academic procedures. What do you need assistance with?",
                    "Let me help you with academic processes. What specifically do you need to do?",
                    "What academic procedure can I guide you through?"
                ],
                "technology": [
                    "I can help with campus technology. What system or service do you need help accessing?",
                    "Let me assist you with tech support. What technology issue can I help with?",
                    "What technical process do you need help with?"
                ],
                "services": [
                    "I can help with campus services. What process do you need guidance on?",
                    "Let me help you with campus procedures. What service do you need help with?",
                    "What campus service procedure can I assist with?"
                ]
            },
            "get_events": {
                "events": [
                    "I can tell you about campus events. What type of activities interest you?",
                    "What kind of events are you looking for? Academic, social, or sports?",
                    "There are many campus activities. What type of events interest you most?"
                ],
                "academic": [
                    "I can help you find academic activities. Are you looking for study groups, workshops, or other academic events?",
                    "What academic events or activities are you interested in?"
                ]
            },
            "greeting": {
                "social": [
                    "Hello! I'm NEXi, your campus assistant. How can I help you today?",
                    "Hi there! What can I help you with on campus?",
                    "Good day! I'm here to help with any campus questions you have.",
                    "Welcome! I'm NEXi, and I'm here to assist with campus information."
                ]
            },
            "goodbye": {
                "social": [
                    "Goodbye! Feel free to ask me anything about campus anytime.",
                    "See you later! I'm here whenever you need campus information.",
                    "Take care! Don't hesitate to reach out if you need more help.",
                    "Thanks for using NEXi! Have a great day on campus!"
                ]
            },
            "unknown": {
                "general": [
                    "I'm not sure I understand. Could you rephrase your question about campus?",
                    "I'm still learning! Can you ask me about campus locations, hours, contacts, or services?",
                    "I didn't quite catch that. Try asking about campus facilities, events, or how to do something on campus.",
                    "I'm here to help with campus questions. Could you be more specific about what you need?"
                ],
                "clarification": [
                    "I want to help, but I need more details. Are you asking about campus locations, hours, events, or something else?",
                    "Could you give me more context? I can help with directions, contact info, procedures, and campus services.",
                    "I'm not quite sure what you're looking for. Try asking about specific campus facilities or services."
                ]
            }
        }
    
    def _load_training_data(self) -> List[TrainingExample]:
        """Load and augment training data"""
        training_examples = []
        
        # Load from JSON file
        try:
            json_path = self.data_path / "essential_questions.json"
            with open(json_path, 'r') as f:
                data = json.load(f)
            
            for q in data["campus_questions"]:
                training_examples.append(
                    TrainingExample(q["question"], q["intent"], q["category"])
                )
        except FileNotFoundError:
            print(f"Warning: Training data file not found at {json_path}")
        
        # Add examples from intent definitions
        for intent in self.intents:
            for example in intent.ml_examples:
                training_examples.append(
                    TrainingExample(example, intent.name, "synthetic")
                )
        
        # Add augmented examples for better training
        augmented = self._augment_training_data(training_examples)
        training_examples.extend(augmented)
        
        return training_examples
    
    def _augment_training_data(self, examples: List[TrainingExample]) -> List[TrainingExample]:
        """Create augmented training examples for better ML performance"""
        augmented = []
        
        # Common variations and synonyms
        variations = {
            "where": ["where is", "where can I find", "location of", "how to get to"],
            "what time": ["when does", "what are the hours", "operating hours"],
            "how do I": ["how can I", "what's the process to", "steps to"],
            "who": ["who can I contact", "who should I call", "contact for"],
            "hello": ["hi", "hey", "good morning", "greetings"],
            "thanks": ["thank you", "appreciate it", "that helps"]
        }
        
        for example in examples[:20]:  # Augment first 20 examples
            text = example.question.lower()
            for original, replacements in variations.items():
                if original in text:
                    for replacement in replacements[:2]:  # Limit augmentation
                        new_text = text.replace(original, replacement)
                        augmented.append(
                            TrainingExample(new_text, example.intent, "augmented")
                        )
        
        return augmented
    
    def _load_entity_patterns(self) -> Dict[str, List[str]]:
        """Define entity patterns for basic Named Entity Recognition"""
        return {
            "building": [
                "library", "gym", "cafeteria", "dining hall", "student center",
                "administration", "registrar", "bookstore", "health center",
                "dormitory", "residence hall", "parking garage"
            ],
            "department": [
                "admissions", "registrar", "financial aid", "IT support",
                "campus security", "housing", "student services"
            ],
            "time": [
                "morning", "afternoon", "evening", "today", "tomorrow",
                "monday", "tuesday", "wednesday", "thursday", "friday",
                "weekend", "weekday"
            ],
            "service": [
                "wifi", "internet", "email", "portal", "registration",
                "enrollment", "transcript", "grades"
            ]
        }
    
    def preprocess_text_ml(self, text: str) -> str:
        """Advanced text preprocessing for ML"""
        # Basic preprocessing
        text = text.lower().strip()
        
        # Handle contractions
        contractions = {
            "what's": "what is", "where's": "where is", "how's": "how is",
            "when's": "when is", "can't": "cannot", "won't": "will not",
            "don't": "do not", "i'm": "i am", "you're": "you are"
        }
        
        for contraction, expansion in contractions.items():
            text = text.replace(contraction, expansion)
        
        # Remove punctuation but keep spaces
        text = re.sub(r'[^\w\s]', '', text)
        
        # Simple tokenization and stopword removal
        keep_stopwords = {'where', 'when', 'what', 'how', 'who', 'which'}
        tokens = text.split()  # Simple whitespace tokenization
        filtered_tokens = [
            token for token in tokens 
            if token not in self.stop_words or token in keep_stopwords
        ]
        
        # Simple stemming (remove common suffixes)
        stemmed_tokens = []
        for token in filtered_tokens:
            # Basic stemming rules
            if token.endswith('ing'):
                token = token[:-3]
            elif token.endswith('ed'):
                token = token[:-2]
            elif token.endswith('er'):
                token = token[:-2]
            elif token.endswith('ly'):
                token = token[:-2]
            stemmed_tokens.append(token)
        
        return ' '.join(stemmed_tokens)
    
    def extract_entities(self, text: str) -> Dict[str, str]:
        """Extract entities from text using pattern matching"""
        entities = {}
        text_lower = text.lower()
        
        for entity_type, patterns in self.entity_patterns.items():
            for pattern in patterns:
                if pattern in text_lower:
                    entities[entity_type] = pattern
                    break  # Take first match for each type
        
        return entities
    
    def train_ml_models(self):
        """Train multiple ML models for intent classification"""
        print("🤖 Training ML models...")
        
        # Prepare training data
        texts = [example.question for example in self.training_data]
        labels = [example.intent for example in self.training_data]
        
        # Preprocess texts
        processed_texts = [self.preprocess_text_ml(text) for text in texts]
        
        # Create TF-IDF vectorizer
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            ngram_range=(1, 2),  # Unigrams and bigrams
            min_df=1,
            max_df=0.95,
            stop_words=None  # We handle stopwords in preprocessing
        )
        
        # Fit vectorizer and transform texts
        X = self.vectorizer.fit_transform(processed_texts)
        y = np.array(labels)
        
        # Train multiple classifiers
        self.classifiers = {
            'naive_bayes': MultinomialNB(alpha=0.1),
            'svm': SVC(probability=True, kernel='linear', C=1.0),
            'random_forest': RandomForestClassifier(n_estimators=100, random_state=42)
        }
        
        # Train and evaluate each classifier
        results = {}
        for name, classifier in self.classifiers.items():
            print(f"Training {name}...")
            classifier.fit(X, y)
            
            # Cross-validation score
            scores = cross_val_score(classifier, X, y, cv=min(5, len(set(y))))
            results[name] = scores.mean()
            print(f"{name} CV accuracy: {scores.mean():.3f} (+/- {scores.std() * 2:.3f})")
        
        # Select best classifier as primary
        self.primary_classifier = max(results, key=results.get)
        print(f"Primary classifier: {self.primary_classifier} (accuracy: {results[self.primary_classifier]:.3f})")
        
        self.is_trained = True
        
        # Save models
        self._save_models()
        
        print("✅ ML models trained successfully!")
    
    def _save_models(self):
        """Save trained models to disk"""
        model_data = {
            'vectorizer': self.vectorizer,
            'classifiers': self.classifiers,
            'primary_classifier': self.primary_classifier,
            'confidence_threshold': self.confidence_threshold,
            'unknown_threshold': self.unknown_threshold
        }
        
        with open(self.model_path / 'ml_models.pkl', 'wb') as f:
            pickle.dump(model_data, f)
        
        print(f"Models saved to {self.model_path / 'ml_models.pkl'}")
    
    def _load_models(self):
        """Load trained models from disk"""
        try:
            with open(self.model_path / 'ml_models.pkl', 'rb') as f:
                model_data = pickle.load(f)
            
            self.vectorizer = model_data['vectorizer']
            self.classifiers = model_data['classifiers']
            self.primary_classifier = model_data['primary_classifier']
            self.confidence_threshold = model_data.get('confidence_threshold', 0.6)
            self.unknown_threshold = model_data.get('unknown_threshold', 0.3)
            self.is_trained = True
            
            print("✅ Models loaded successfully!")
            return True
        except FileNotFoundError:
            print("No saved models found. Will train new models.")
            return False
    
    def classify_intent_ml(self, user_input: str, user_id: str = "default") -> Response:
        """ML-based intent classification with ensemble voting"""
        
        # Get or create conversation state
        if user_id not in self.conversation_states:
            self.conversation_states[user_id] = ConversationState(user_id=user_id)
        
        conv_state = self.conversation_states[user_id]
        
        # Extract entities
        entities = self.extract_entities(user_input)
        
        # If ML models aren't trained, fall back to keyword matching
        if not self.is_trained:
            return self._classify_intent_fallback(user_input, conv_state, entities)
        
        # Preprocess input
        processed_input = self.preprocess_text_ml(user_input)
        
        # Vectorize input
        X = self.vectorizer.transform([processed_input])
        
        # Get predictions from all classifiers
        predictions = {}
        confidences = {}
        
        for name, classifier in self.classifiers.items():
            pred = classifier.predict(X)[0]
            
            # Get confidence (probability)
            if hasattr(classifier, 'predict_proba'):
                proba = classifier.predict_proba(X)[0]
                max_proba = np.max(proba)
                confidences[name] = max_proba
            else:
                confidences[name] = 0.5  # Default for classifiers without probability
            
            predictions[name] = pred
        
        # Ensemble voting - use primary classifier but check agreement
        primary_pred = predictions[self.primary_classifier]
        primary_conf = confidences[self.primary_classifier]
        
        # Check if other classifiers agree
        agreement_count = sum(1 for pred in predictions.values() if pred == primary_pred)
        agreement_ratio = agreement_count / len(predictions)
        
        # Adjust confidence based on agreement
        final_confidence = primary_conf * agreement_ratio
        
        # Apply confidence thresholding
        if final_confidence < self.unknown_threshold:
            intent_name = "unknown"
            final_confidence = 0.1
            fallback_reason = f"Low confidence ({final_confidence:.2f})"
        elif final_confidence < self.confidence_threshold:
            # Medium confidence - provide clarification
            intent_name = primary_pred
            fallback_reason = f"Medium confidence ({final_confidence:.2f}) - may need clarification"
        else:
            intent_name = primary_pred
            fallback_reason = None
        
        # Update conversation state
        conv_state.last_intent = intent_name
        if intent_name != "unknown":
            conv_state.context_history.append(intent_name)
            conv_state.context_history = conv_state.context_history[-3:]  # Keep last 3
        
        # Update entity memory
        conv_state.entity_memory.update(entities)
        
        # Determine context
        context = self._determine_context(intent_name, conv_state, entities)
        
        return Response(
            intent=intent_name,
            text=self.get_response(intent_name, context, fallback_reason),
            confidence=final_confidence,
            context=context,
            fallback_reason=fallback_reason,
            entities=entities
        )
    
    def _classify_intent_fallback(self, user_input: str, conv_state: ConversationState, entities: Dict[str, str]) -> Response:
        """Fallback to keyword-based classification when ML isn't available"""
        processed_input = user_input.lower().strip()
        words = processed_input.split()
        
        # Score each intent
        intent_scores = {}
        
        for intent in self.intents:
            score = 0
            for keyword in intent.keywords:
                if keyword in processed_input:
                    if keyword in words:
                        score += 2 * intent.priority
                    else:
                        score += 1 * intent.priority
            intent_scores[intent.name] = score
        
        # Find best matching intent
        best_intent = max(intent_scores.items(), key=lambda x: x[1])
        intent_name, score = best_intent
        
        # Calculate confidence
        if score == 0:
            intent_name = "unknown"
            confidence = 0.1
        else:
            max_possible_score = max(len(intent.keywords) * 2 * intent.priority 
                                   for intent in self.intents if intent.name != "unknown")
            confidence = min(score / max_possible_score, 1.0)
        
        context = self._determine_context(intent_name, conv_state, entities)
        
        return Response(
            intent=intent_name,
            text=self.get_response(intent_name, context),
            confidence=confidence,
            context=context,
            entities=entities
        )
    
    def _determine_context(self, intent: str, conv_state: ConversationState, entities: Dict[str, str]) -> str:
        """Determine response context based on intent, conversation history, and entities"""
        
        # Default contexts for each intent
        default_contexts = {
            "find_location": "general",
            "get_hours": "general", 
            "get_contact": "support",
            "how_to": "general",
            "get_events": "events",
            "greeting": "social",
            "goodbye": "social",
            "unknown": "general"
        }
        
        context = default_contexts.get(intent, "general")
        
        # Refine context based on entities
        if intent == "find_location":
            if any(dining in entities.get("building", "") for dining in ["cafeteria", "dining"]):
                context = "dining"
            elif entities.get("building"):
                context = "navigation"
        
        elif intent == "get_contact":
            if "emergency" in entities.get("department", ""):
                context = "emergency"
        
        elif intent == "how_to":
            if entities.get("service") in ["wifi", "internet", "email", "portal"]:
                context = "technology"
            elif entities.get("service") in ["registration", "enrollment"]:
                context = "academic"
            else:
                context = "services"
        
        elif intent == "unknown":
            if conv_state.last_intent:
                context = "clarification"
        
        return context
    
    def get_response(self, intent: str, context: str = "general", fallback_reason: str = None) -> str:
        """Get context-aware response with fallback handling"""
        
        # Handle fallback cases
        if fallback_reason and "Low confidence" in fallback_reason:
            if intent == "unknown":
                context = "clarification"
            else:
                # For low confidence, ask for clarification
                clarification_responses = [
                    f"I think you're asking about {intent.replace('_', ' ')}, but I'm not completely sure. Could you provide more details?",
                    f"It seems like you might need help with {intent.replace('_', ' ')}. Can you be more specific?",
                    f"I want to make sure I understand correctly. Are you asking about {intent.replace('_', ' ')}?"
                ]
                return random.choice(clarification_responses)
        
        # Get appropriate response
        if intent in self.responses:
            if context in self.responses[intent]:
                responses = self.responses[intent][context]
            else:
                # Fallback to general context
                responses = self.responses[intent].get("general", 
                                                     list(self.responses[intent].values())[0])
            
            # Add fallback context if needed
            response = random.choice(responses)
            if fallback_reason and "Medium confidence" in fallback_reason:
                response += " (Please let me know if this isn't what you were looking for!)"
            
            return response
        
        return random.choice(self.responses["unknown"]["general"])
    
    def get_conversation_stats(self, user_id: str = "default") -> Dict:
        """Get conversation statistics for a user"""
        if user_id not in self.conversation_states:
            return {"error": "No conversation found for user"}
        
        conv_state = self.conversation_states[user_id]
        return {
            "user_id": user_id,
            "conversation_length": len(conv_state.context_history),
            "last_intent": conv_state.last_intent,
            "entities_remembered": dict(conv_state.entity_memory),
            "conversation_duration": str(datetime.now() - conv_state.conversation_start)
        }
    
    def add_training_data(self, user_input: str, correct_intent: str, category: str = "user_feedback"):
        """Add training data and retrain if enough new examples"""
        example = TrainingExample(user_input, correct_intent, category)
        self.training_data.append(example)
        
        print(f"Training data added: '{user_input}' -> {correct_intent} ({category})")
        
        # Retrain if we have enough new examples (every 10 new examples)
        user_feedback_count = sum(1 for ex in self.training_data if ex.category == "user_feedback")
        if user_feedback_count % 10 == 0 and user_feedback_count > 0:
            print("Retraining models with new feedback...")
            self.train_ml_models()
    
    def get_training_stats(self) -> Dict:
        """Get comprehensive training statistics"""
        intent_counts = {}
        category_counts = {}
        
        for example in self.training_data:
            intent_counts[example.intent] = intent_counts.get(example.intent, 0) + 1
            category_counts[example.category] = category_counts.get(example.category, 0) + 1
        
        return {
            "total_examples": len(self.training_data),
            "intent_distribution": intent_counts,
            "category_distribution": category_counts,
            "ml_models_trained": self.is_trained,
            "primary_classifier": getattr(self, 'primary_classifier', None),
            "confidence_threshold": self.confidence_threshold,
            "unknown_threshold": self.unknown_threshold
        }


# Testing and Demo Functions for Week 2
def test_ml_classifier():
    """Comprehensive test of the ML classifier"""
    print("🧠 Testing Week 2 ML-Based Intent Classifier")
    print("=" * 60)
    
    classifier = MLIntentClassifier()
    
    # Show training stats
    stats = classifier.get_training_stats()
    print("📊 Training Statistics:")
    print(f"Total examples: {stats['total_examples']}")
    print(f"ML models trained: {stats['ml_models_trained']}")
    if stats['ml_models_trained']:
        print(f"Primary classifier: {stats['primary_classifier']}")
    print(f"Intent distribution: {stats['intent_distribution']}")
    print("\n" + "="*60 + "\n")
    
    # Test questions with various complexity levels
    test_questions = [
        # Basic questions
        "Where is the library?",
        "What time does the cafeteria close?",
        "How do I connect to WiFi?",
        "Hello NEXi",
        
        # Medium complexity
        "I need help finding the student center building",
        "What are the operating hours for the gym facility?",
        "Who should I contact for IT technical support?",
        "Can you tell me about upcoming campus events?",
        
        # Complex/edge cases
        "I'm looking for somewhere to eat dinner on campus",
        "When does the library close on weekends?",
        "How do I register for spring semester classes?",
        "Thanks for all your help today",
        
        # Challenging cases
        "I want pizza",  # Should be unknown
        "The weather is nice",  # Should be unknown
        "Find food",  # Should be find_location with dining context
        "Hours?",  # Minimal input
    ]
    
    print("🧪 Testing Classification Performance:")
    print("-" * 60)
    
    for i, question in enumerate(test_questions, 1):
        response = classifier.classify_intent_ml(question, user_id="test_user")
        
        print(f"{i:2d}. Q: {question}")
        print(f"    Intent: {response.intent}")
        print(f"    Context: {response.context}")
        print(f"    Confidence: {response.confidence:.3f}")
        if response.entities:
            print(f"    Entities: {response.entities}")
        if response.fallback_reason:
            print(f"    Fallback: {response.fallback_reason}")
        print(f"    Response: {response.text}")
        print("-" * 60)
    
    # Show conversation stats
    conv_stats = classifier.get_conversation_stats("test_user")
    print("💬 Conversation Statistics:")
    for key, value in conv_stats.items():
        print(f"{key}: {value}")
    
    print("\n✅ ML Classifier testing completed!")

if __name__ == "__main__":
    test_ml_classifier()
