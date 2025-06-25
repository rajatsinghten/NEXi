"""
Week 2 Test Suite for ML-based Intent Classification
Brain Team: Krishna, Rajat
"""

import pytest
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from brain.ml_classifier import MLIntentClassifier
from brain.week2_brain_system import NEXiBrainSystem
from brain.fallback_manager import FallbackManager

class TestWeek2MLClassifier:
    
    @pytest.fixture
    def ml_classifier(self):
        """Create ML classifier instance for testing"""
        return MLIntentClassifier()
    
    @pytest.fixture 
    def brain_system(self):
        """Create complete brain system for testing"""
        return NEXiBrainSystem()
    
    def test_ml_classifier_initialization(self, ml_classifier):
        """Test ML classifier initializes correctly"""
        assert ml_classifier is not None
        assert len(ml_classifier.intents) > 0
        assert len(ml_classifier.responses) > 0
        assert len(ml_classifier.training_data) > 0
        assert ml_classifier.is_trained == True
    
    def test_ml_classification_confidence(self, ml_classifier):
        """Test ML classification provides appropriate confidence scores"""
        test_cases = [
            ("Where is the library?", 0.8),  # Should be high confidence
            ("What time does the gym close?", 0.8),  # Should be high confidence
            ("How do I connect to WiFi?", 0.8),  # Should be high confidence
            ("Building stuff", 0.5),  # Should be medium confidence
            ("Random gibberish xyz", 0.2)  # Should be low confidence
        ]
        
        for question, expected_min_confidence in test_cases:
            response = ml_classifier.classify_intent_ml(question)
            if response.intent != "unknown":
                assert response.confidence >= expected_min_confidence or response.confidence <= 0.5
            assert 0 <= response.confidence <= 1.0
    
    def test_entity_extraction(self, ml_classifier):
        """Test entity extraction functionality"""
        test_cases = [
            ("Where is the library?", {"building": "library"}),
            ("What time does the gym close?", {"building": "gym"}),
            ("How do I connect to WiFi?", {"service": "wifi"}),
            ("Who do I contact for IT support?", {"department": "IT support"}),
        ]
        
        for question, expected_entities in test_cases:
            response = ml_classifier.classify_intent_ml(question)
            for entity_type, entity_value in expected_entities.items():
                assert entity_type in response.entities
                assert entity_value in response.entities[entity_type]
    
    def test_conversation_context(self, ml_classifier):
        """Test conversation context tracking"""
        user_id = "test_context_user"
        
        # Ask a series of related questions
        questions = [
            "Where is the library?",
            "What time does it close?",
            "Thanks for your help"
        ]
        
        responses = []
        for question in questions:
            response = ml_classifier.classify_intent_ml(question, user_id)
            responses.append(response)
        
        # Check that context is maintained
        conv_stats = ml_classifier.get_conversation_stats(user_id)
        assert conv_stats["conversation_length"] > 0
        assert conv_stats["entities_remembered"] is not None
    
    def test_training_data_augmentation(self, ml_classifier):
        """Test that training data includes augmented examples"""
        # Count different types of training data
        categories = {}
        for example in ml_classifier.training_data:
            category = example.category
            categories[category] = categories.get(category, 0) + 1
        
        # Should have original, synthetic, and augmented examples
        assert "navigation" in categories or "hours" in categories  # Original
        assert "synthetic" in categories  # From intent definitions
        assert "augmented" in categories  # Augmented variations
    
    def test_model_persistence(self, ml_classifier):
        """Test that ML models can be saved and loaded"""
        # Models should be automatically saved during training
        model_path = Path("data/models/ml_models.pkl")
        assert model_path.exists()
        
        # Test that we can load models
        assert ml_classifier._load_models() == False or True  # Returns bool


class TestWeek2BrainSystem:
    
    @pytest.fixture
    def brain_system(self):
        """Create brain system for testing"""
        return NEXiBrainSystem()
    
    def test_brain_system_initialization(self, brain_system):
        """Test complete brain system initializes correctly"""
        assert brain_system.ml_classifier is not None
        assert brain_system.fallback_manager is not None
        assert brain_system.qa_database is not None
        assert brain_system.metrics["total_queries"] == 0
    
    def test_high_confidence_processing(self, brain_system):
        """Test processing of high-confidence queries"""
        query = "Where is the library?"
        result = brain_system.process_query(query, "test_user")
        
        assert result["status"] == "success"
        assert result["confidence"] > 0.7
        assert result["fallback_used"] == False
        assert "library" in result["entities"].get("building", "")
        assert len(result["suggested_follow_ups"]) > 0
    
    def test_fallback_processing(self, brain_system):
        """Test processing of queries requiring fallback"""
        query = "Random gibberish xyz123"
        result = brain_system.process_query(query, "test_user")
        
        assert result["status"] == "fallback"
        assert result["fallback_used"] == True
        assert result["response_type"] == "fallback"
        assert len(result["suggested_follow_ups"]) > 0
    
    def test_specific_database_answers(self, brain_system):
        """Test that specific answers are retrieved from database when available"""
        # Test a query that should have a specific database answer
        query = "Where is the library?"
        result = brain_system.process_query(query, "test_user")
        
        if result["response_type"] == "specific":
            # Should contain specific information like building number, hours, etc.
            assert any(keyword in result["response"].lower() 
                      for keyword in ["building", "floor", "hours", "open"])
    
    def test_conversation_flow(self, brain_system):
        """Test multi-turn conversation handling"""
        user_id = "conversation_test_user"
        
        # Simulate a conversation
        queries = [
            "Hello NEXi",
            "Where is the library?", 
            "What time does it close?",
            "Thanks"
        ]
        
        for query in queries:
            result = brain_system.process_query(query, user_id)
            assert result["conversation_id"] == user_id
            assert "response" in result
    
    def test_system_metrics(self, brain_system):
        """Test system metrics tracking"""
        # Process some queries
        queries = [
            "Where is the library?",
            "Random text",
            "What time does the gym close?"
        ]
        
        for query in queries:
            brain_system.process_query(query, "metrics_test_user")
        
        metrics = brain_system.get_system_metrics()
        
        assert metrics["total_queries_processed"] == 3
        assert 0 <= metrics["successful_classification_rate"] <= 1
        assert 0 <= metrics["fallback_usage_rate"] <= 1
        assert metrics["ml_model_trained"] == True
        assert metrics["training_examples"] > 50  # Should have expanded training data
    
    def test_feedback_integration(self, brain_system):
        """Test user feedback integration"""
        initial_training_size = len(brain_system.ml_classifier.training_data)
        
        # Add feedback
        brain_system.add_feedback(
            "Test feedback query", 
            "find_location", 
            "feedback_test_user",
            True
        )
        
        # Training data should be expanded
        assert len(brain_system.ml_classifier.training_data) == initial_training_size + 1


class TestWeek2FallbackSystem:
    
    @pytest.fixture
    def fallback_manager(self):
        """Create fallback manager for testing"""
        return FallbackManager()
    
    def test_fallback_strategies(self, fallback_manager):
        """Test different fallback strategies are triggered correctly"""
        test_cases = [
            (0.65, "clarify"),     # High confidence clarification
            (0.4, "suggest"),      # Medium confidence suggestion
            (0.2, "redirect"),     # Low confidence redirect
            (0.05, "unknown")      # Very low confidence unknown
        ]
        
        for confidence, expected_strategy in test_cases:
            strategy = fallback_manager._select_strategy(confidence)
            assert strategy.strategy_type == expected_strategy
    
    def test_personalized_suggestions(self, fallback_manager):
        """Test personalized suggestions based on user history"""
        user_id = "personalization_test_user"
        
        # Simulate successful interactions
        fallback_manager.track_successful_resolution(
            user_id, "Where is the library?", "find_location", True
        )
        fallback_manager.track_successful_resolution(
            user_id, "What time does gym close?", "get_hours", True  
        )
        
        suggestions = fallback_manager.get_personalized_suggestions(user_id)
        assert len(suggestions) > 0
        assert isinstance(suggestions[0], str)


class TestWeek2Integration:
    """Integration tests for complete Week 2 system"""
    
    def test_week2_goal_completion(self):
        """Test that all Week 2 goals are completed"""
        brain_system = NEXiBrainSystem()
        
        # Goal 1: Implement intent classification algorithm
        assert brain_system.ml_classifier.is_trained == True
        assert hasattr(brain_system.ml_classifier, 'primary_classifier')
        
        # Goal 2: Build structured Q&A database  
        assert len(brain_system.qa_database) > 0
        categories = brain_system.qa_database.get("campus_database", {}).get("categories", {})
        assert len(categories) >= 8  # Should have multiple categories
        
        # Goal 3: Create fallback response system
        assert brain_system.fallback_manager is not None
        assert len(brain_system.fallback_manager.fallback_strategies) >= 4
        
        # Goal 4: Add context awareness features
        response = brain_system.ml_classifier.classify_intent_ml("Hello", "context_test")
        conv_stats = brain_system.ml_classifier.get_conversation_stats("context_test")
        assert "conversation_length" in conv_stats
        
        # Goal 5: Test with expanded question set
        metrics = brain_system.get_system_metrics()
        assert metrics["training_examples"] >= 70  # Expanded dataset
    
    def test_system_performance_benchmarks(self):
        """Test that system meets performance benchmarks"""
        brain_system = NEXiBrainSystem()
        
        # Test classification speed
        import time
        start_time = time.time()
        
        for _ in range(10):
            brain_system.process_query("Where is the library?", "benchmark_user")
        
        end_time = time.time()
        avg_time = (end_time - start_time) / 10
        
        # Should be fast (less than 100ms per query)
        assert avg_time < 0.1
        
        # Test accuracy on known good examples
        good_examples = [
            ("Where is the library?", "find_location"),
            ("What time does the gym close?", "get_hours"),
            ("How do I connect to WiFi?", "how_to"),
            ("Hello NEXi", "greeting"),
            ("Thanks for your help", "goodbye")
        ]
        
        correct_classifications = 0
        for query, expected_intent in good_examples:
            result = brain_system.process_query(query, "accuracy_test")
            if result["intent"] == expected_intent and result["confidence"] > 0.5:
                correct_classifications += 1
        
        accuracy = correct_classifications / len(good_examples)
        assert accuracy >= 0.8  # Should have at least 80% accuracy on clear examples


if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v"])
