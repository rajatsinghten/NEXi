#!/usr/bin/env python3
"""
Test the enhanced NEXi system with general question handling
"""

import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_enhanced_system():
    """Test the enhanced system with both campus and general questions"""
    
    from src.brain.week2_brain_system import NEXiBrainSystem
    
    print("🧠 Testing Enhanced NEXi Brain System with General Question Handling")
    print("=" * 70)
    
    brain = NEXiBrainSystem()
    
    # Mixed test questions
    test_questions = [
        # General questions (should be handled by general handler)
        "What is 2 + 2?",
        "How is the weather today?",
        "Calculate 15 * 3",
        "How are you?",
        "Thanks for your help",
        "What's the capital of France?",
        
        # Campus questions (should be handled by campus system)
        "Where is the library?",
        "What time does the gym close?",
        "How do I connect to WiFi?",
        "Who do I contact for IT support?",
        "Hello NEXi"
    ]
    
    print("🔍 Testing Mixed Questions (General + Campus)")
    print("-" * 50)
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n{i}. Q: {question}")
        response = brain.process_query(question, f"test_user_{i}")
        
        print(f"   Status: {response['status']}")
        print(f"   Intent: {response['intent']} (confidence: {response['confidence']:.2f})")
        print(f"   Response: {response['response']}")
        
        if response.get('entities'):
            print(f"   Entities: {response['entities']}")
        
        if response.get('suggested_follow_ups'):
            print(f"   Follow-ups: {response['suggested_follow_ups']}")
    
    # Show performance metrics
    print("\n" + "="*70)
    print("📊 Enhanced System Performance Metrics:")
    metrics = brain.metrics
    total = max(metrics['total_queries'], 1)
    
    print(f"  Total Queries: {metrics['total_queries']}")
    print(f"  Campus Questions: {metrics['successful_classifications']} ({metrics['successful_classifications']/total*100:.1f}%)")
    print(f"  General Questions: {metrics.get('general_questions', 0)} ({metrics.get('general_questions', 0)/total*100:.1f}%)")
    print(f"  Fallback Used: {metrics['fallback_used']} ({metrics['fallback_used']/total*100:.1f}%)")
    print(f"  Average Confidence: {metrics['avg_confidence']:.2f}")

if __name__ == "__main__":
    test_enhanced_system()
