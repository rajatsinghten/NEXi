#!/usr/bin/env python3
"""
NEXi Brain System - Interactive Demonstration
This script demonstrates the key capabilities of the NEXi Brain System
"""

import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def demo_both_systems():
    """Demonstrate both Week 1 and Week 2 systems"""
    
    print("🧠 NEXi Brain System Demonstration")
    print("=" * 50)
    
    test_queries = [
        "Where is the library?",
        "What time does the gym close?", 
        "How do I connect to WiFi?",
        "Who do I contact for IT support?",
        "Hello NEXi",
        "Thanks for your help"
    ]
    
    print("\n📍 Week 1 System (Keyword-based)")
    print("-" * 40)
    
    # Test Week 1 system
    try:
        from main import SimpleIntentClassifier
        week1_classifier = SimpleIntentClassifier()
        
        for query in test_queries:
            response = week1_classifier.classify_intent(query)
            print(f"Q: {query}")
            print(f"   Intent: {response.intent} ({response.confidence:.2f})")
            print(f"   Response: {response.text}")
            print()
    except Exception as e:
        print(f"Error with Week 1 system: {e}")
    
    print("\n🚀 Week 2 System (ML-powered)")
    print("-" * 40)
    
    # Test Week 2 system
    try:
        from src.brain.week2_brain_system import NEXiBrainSystem
        week2_system = NEXiBrainSystem()
        
        for i, query in enumerate(test_queries):
            response = week2_system.process_query(query, f"demo_user_{i}")
            print(f"Q: {query}")
            print(f"   Intent: {response['intent']} ({response['confidence']:.2f})")
            print(f"   Response: {response['response']}")  # Fixed: use 'response' not 'text'
            if response.get('entities'):
                print(f"   Entities: {response['entities']}")
            print()
            
        # Show performance metrics
        print("📊 Performance Metrics:")
        metrics = week2_system.metrics
        print(f"   Total queries: {metrics['total_queries']}")
        print(f"   Success rate: {(metrics['successful_classifications']/metrics['total_queries']*100):.1f}%")
        print(f"   Avg confidence: {metrics['avg_confidence']:.2f}")
        
    except Exception as e:
        print(f"Error with Week 2 system: {e}")

if __name__ == "__main__":
    demo_both_systems()
