#!/usr/bin/env python3
"""
Quick interactive test of the enhanced system
"""

import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def quick_test():
    from src.brain.week2_brain_system import NEXiBrainSystem
    
    brain = NEXiBrainSystem()
    
    # Test specific questions
    test_cases = [
        "Hello NEXi",
        "What is 5 + 3?",
        "Where is the library?",
        "How is the weather?",
        "Thanks for your help"
    ]
    
    print("🧠 Quick Test of Enhanced NEXi System")
    print("=" * 50)
    
    for question in test_cases:
        print(f"\nQ: {question}")
        response = brain.process_query(question)
        print(f"Status: {response['status']}")
        print(f"Intent: {response['intent']}")
        print(f"Response: {response['response']}")
        print("-" * 30)

if __name__ == "__main__":
    quick_test()
