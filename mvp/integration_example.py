
# NEXi Brain Integration Examples
# Enhanced with AI-Powered Routing
# Brain Team: Krishna & Rajat

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.brain.nexi_brain_mvp import get_nexi_response, NEXiBrainMVP

def voice_team_example():
    """Example for Voice Team integration"""
    print("🎤 Voice Team Integration Example")
    print("-" * 40)
    
    # Simulate voice input
    voice_questions = [
        "Where is the library?",
        "Where is mess?",
        "Where can I find IT support?"
    ]
    
    for question in voice_questions:
        print(f"Voice Input: \"{question}\"")
        
        # Get brain response (simple method)
        response = get_nexi_response(question)
        
        # Send to text-to-speech
        print(f"TTS Output: {response}")
        print()

def interface_team_example():
    """Example for Interface Team integration"""
    print("💻 Interface Team Integration Example")
    print("-" * 40)
    
    # Advanced integration with detailed response info
    brain = NEXiBrainMVP()
    
    ui_questions = [
        "What time does the dining hall close?",
        "What's 2 + 2?"
    ]
    
    for question in ui_questions:
        print(f"UI Input: \"{question}\"")
        
        # Get detailed response
        result = brain.process_query(question)
        
        # Display on interface with metadata
        print(f"Display: {result['response']}")
        print(f"Type: {result['response_type']}")
        print(f"Confidence: {result['confidence']:.2f}")
        print(f"Response Time: {result['response_time_ms']}ms")
        if 'suggested_follow_ups' in result:
            print(f"Suggestions: {result['suggested_follow_ups'][:2]}")
        print()

def hardware_team_example():
    """Example for Hardware Team integration"""
    print("🔧 Hardware Team Integration Example")
    print("-" * 40)
    
    # Simple integration for embedded systems
    print("Hardware Input: Button press + 'Where is the gym?'")
    
    response = get_nexi_response("Where is the gym?")
    
    # Simple LED/Display output
    print(f"LED Display: {response[:50]}...")
    print(f"Status: ✅ Response ready")
    print()

def performance_demo():
    """Demonstrate enhanced performance metrics"""
    print("📊 Performance Enhancement Demo")
    print("-" * 40)
    
    brain = NEXiBrainMVP()
    
    # Test previously failing questions
    test_cases = [
        "Where is mess?",
        "Where can I find IT support?",
        "What time does the dining hall close?"
    ]
    
    print("Testing enhanced AI routing...")
    for question in test_cases:
        result = brain.process_query(question)
        status = "✅ AI Success" if result['response_type'] == 'ai_campus_database' else "⚠️  Fallback"
        print(f"{status}: {question} ({result['response_time_ms']}ms)")
    
    # Show final stats
    stats = brain.get_mvp_stats()
    print(f"\n📈 AI Routing Success: {stats['ai_success_rate']}%")
    print(f"⚡ Avg Response Time: {stats['avg_response_time_ms']}ms")

if __name__ == "__main__":
    print("🤝 NEXi Brain Enhanced Integration Examples")
    print("=" * 50)
    print("✨ Features: AI-powered routing, enhanced accuracy")
    print()
    
    voice_team_example()
    interface_team_example() 
    hardware_team_example()
    performance_demo()
    
    print("🎉 Integration examples complete!")
    print("Ready for team integration and live demo!")
