#!/usr/bin/env python3
"""
NEXi Brain System - Unified Entry Point
Brain Team: Krishna, Rajat

This is an improved main entry point that provides:
1. Easy switching between Week 1 and Week 2 systems
2. Interactive chat mode
3. Comprehensive testing
4. Performance monitoring
5. Better error handling and user experience
"""

import sys
import os
import argparse
import time
from pathlib import Path
from typing import Optional

# Ensure we can import from src
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Color codes for better terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_banner():
    """Print the NEXi welcome banner"""
    banner = f"""
{Colors.HEADER}{Colors.BOLD}
╔═══════════════════════════════════════════════════════════════════════╗
║                    🧠 NEXi Brain System v2.0                         ║
║                   Campus AI Assistant - Brain Team                   ║
║                     Krishna & Rajat - Week 2 Complete                ║
╚═══════════════════════════════════════════════════════════════════════╝
{Colors.ENDC}"""
    print(banner)

def check_dependencies():
    """Check if all required dependencies are available"""
    missing_deps = []
    
    try:
        import sklearn
    except ImportError:
        missing_deps.append("scikit-learn")
    
    try:
        import nltk
    except ImportError:
        missing_deps.append("nltk")
    
    try:
        import pandas
    except ImportError:
        missing_deps.append("pandas")
    
    if missing_deps:
        print(f"{Colors.FAIL}❌ Missing dependencies: {', '.join(missing_deps)}{Colors.ENDC}")
        print(f"{Colors.WARNING}Please run: pip install -r requirements.txt{Colors.ENDC}")
        return False
    
    # Check NLTK data
    try:
        import nltk
        nltk.data.find('tokenizers/punkt')
        nltk.data.find('corpora/stopwords')
    except LookupError:
        print(f"{Colors.WARNING}⚠️  NLTK data missing. Downloading...{Colors.ENDC}")
        try:
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            print(f"{Colors.OKGREEN}✅ NLTK data downloaded successfully{Colors.ENDC}")
        except Exception as e:
            print(f"{Colors.FAIL}❌ Failed to download NLTK data: {e}{Colors.ENDC}")
            return False
    
    return True

def run_week1_system():
    """Run the original Week 1 keyword-based system"""
    from main import SimpleIntentClassifier
    
    print(f"{Colors.OKBLUE}🔧 Running Week 1 System (Keyword-based Classification){Colors.ENDC}")
    print("-" * 70)
    
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
    
    for i, question in enumerate(test_questions, 1):
        print(f"{Colors.OKCYAN}Test {i}: {question}{Colors.ENDC}")
        start_time = time.time()
        response = classifier.classify_intent(question)
        end_time = time.time()
        
        print(f"  Intent: {Colors.OKGREEN}{response.intent}{Colors.ENDC} "
              f"(confidence: {response.confidence:.2f}) "
              f"[{(end_time-start_time)*1000:.1f}ms]")
        print(f"  Response: {response.text}")
        print()

def run_week2_system():
    """Run the advanced Week 2 ML-based system"""
    try:
        from src.brain.week2_brain_system import NEXiBrainSystem, comprehensive_week2_test
        
        print(f"{Colors.OKBLUE}🚀 Running Week 2 System (ML-based Classification){Colors.ENDC}")
        print("-" * 70)
        
        # Run comprehensive test
        comprehensive_week2_test()
        
    except ImportError as e:
        print(f"{Colors.FAIL}❌ Failed to import Week 2 system: {e}{Colors.ENDC}")
        print(f"{Colors.WARNING}Make sure all dependencies are installed{Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.FAIL}❌ Error running Week 2 system: {e}{Colors.ENDC}")

def interactive_chat(use_week2=True):
    """Run interactive chat mode"""
    if use_week2:
        try:
            from src.brain.week2_brain_system import NEXiBrainSystem
            brain = NEXiBrainSystem()
            system_name = "Week 2 (ML-powered)"
        except ImportError:
            print(f"{Colors.WARNING}Week 2 system not available, falling back to Week 1{Colors.ENDC}")
            from main import SimpleIntentClassifier
            brain = SimpleIntentClassifier()
            system_name = "Week 1 (Keyword-based)"
            use_week2 = False
    else:
        from main import SimpleIntentClassifier
        brain = SimpleIntentClassifier()
        system_name = "Week 1 (Keyword-based)"
    
    print(f"{Colors.HEADER}💬 Interactive Chat Mode - {system_name}{Colors.ENDC}")
    print(f"{Colors.OKCYAN}Ask me anything about campus! Type 'quit', 'exit', or 'help' for options.{Colors.ENDC}")
    print("-" * 70)
    
    conversation_count = 0
    
    while True:
        try:
            user_input = input(f"{Colors.BOLD}You: {Colors.ENDC}")
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print(f"{Colors.OKGREEN}👋 Thanks for chatting with NEXi! Goodbye!{Colors.ENDC}")
                break
            
            if user_input.lower() == 'help':
                show_help()
                continue
            
            if user_input.lower() == 'stats' and use_week2:
                show_stats(brain)
                continue
            
            if not user_input.strip():
                continue
            
            conversation_count += 1
            start_time = time.time()
            
            if use_week2:
                response = brain.process_query(user_input, f"interactive_user_{conversation_count}")
                text = response['response']  # Fixed: use 'response' not 'text'
                intent = response['intent']
                confidence = response['confidence']
            else:
                response = brain.classify_intent(user_input)
                text = response.text
                intent = response.intent
                confidence = response.confidence
            
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            
            print(f"{Colors.OKGREEN}NEXi: {text}{Colors.ENDC}")
            print(f"{Colors.WARNING}[Intent: {intent} | Confidence: {confidence:.2f} | Time: {response_time:.1f}ms]{Colors.ENDC}")
            print()
            
        except KeyboardInterrupt:
            print(f"\n{Colors.OKGREEN}👋 Goodbye!{Colors.ENDC}")
            break
        except Exception as e:
            print(f"{Colors.FAIL}❌ Error: {e}{Colors.ENDC}")
            print("Please try again or type 'help' for assistance.")

def show_help():
    """Show help information"""
    help_text = f"""
{Colors.HEADER}🆘 NEXi Help Guide{Colors.ENDC}

{Colors.BOLD}Available Commands:{Colors.ENDC}
  • 'help' - Show this help message
  • 'stats' - Show system performance statistics (Week 2 only)
  • 'quit'/'exit'/'bye' - Exit the chat

{Colors.BOLD}Example Questions:{Colors.ENDC}
  📍 Location: "Where is the library?", "How do I get to the gym?"
  🕐 Hours: "What time does the cafeteria close?", "Library hours?"
  📞 Contact: "IT support contact?", "Admissions office phone number?"
  ❓ How-to: "How do I connect to WiFi?", "How to register for classes?"
  🎉 Events: "What events are happening?", "Any sports games today?"

{Colors.BOLD}Tips for Better Results:{Colors.ENDC}
  • Be specific: "library hours" instead of just "hours"
  • Use natural language: "I need help with registration"
  • Ask follow-up questions for more details

{Colors.OKCYAN}NEXi learns from your questions and gets smarter over time!{Colors.ENDC}
    """
    print(help_text)

def show_stats(brain):
    """Show system performance statistics"""
    if hasattr(brain, 'metrics'):
        metrics = brain.metrics
        total = max(metrics['total_queries'], 1)
        success_rate = (metrics['successful_classifications']/total*100)
        fallback_rate = (metrics['fallback_used']/total*100)
        general_rate = (metrics.get('general_questions', 0)/total*100)
        
        print(f"""
{Colors.HEADER}📊 System Performance Statistics{Colors.ENDC}
{Colors.OKGREEN}
  Total Queries Processed: {metrics['total_queries']}
  Campus Questions: {metrics['successful_classifications']} ({success_rate:.1f}%)
  General Questions (Math/Weather/etc): {metrics.get('general_questions', 0)} ({general_rate:.1f}%)
  Fallback System Used: {metrics['fallback_used']} ({fallback_rate:.1f}%)
  Average Confidence Score: {metrics['avg_confidence']:.2f}
{Colors.ENDC}""")
    else:
        print(f"{Colors.WARNING}Statistics not available for Week 1 system{Colors.ENDC}")

def run_tests():
    """Run the test suite"""
    print(f"{Colors.OKBLUE}🧪 Running NEXi Brain System Tests{Colors.ENDC}")
    print("-" * 70)
    
    try:
        import subprocess
        result = subprocess.run(['pytest', 'tests/', '-v'], 
                              capture_output=True, text=True, cwd=project_root)
        print(result.stdout)
        if result.stderr:
            print(f"{Colors.WARNING}{result.stderr}{Colors.ENDC}")
        
        if result.returncode == 0:
            print(f"{Colors.OKGREEN}✅ All tests completed successfully!{Colors.ENDC}")
        else:
            print(f"{Colors.WARNING}⚠️  Some tests failed. Check output above.{Colors.ENDC}")
            
    except FileNotFoundError:
        print(f"{Colors.FAIL}❌ pytest not found. Please install it with: pip install pytest{Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.FAIL}❌ Error running tests: {e}{Colors.ENDC}")

def main():
    """Main entry point with argument parsing"""
    parser = argparse.ArgumentParser(
        description="NEXi Brain System - Campus AI Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python nexi.py                    # Interactive chat (Week 2)
  python nexi.py --week1            # Run Week 1 system demo
  python nexi.py --week2            # Run Week 2 system demo
  python nexi.py --chat --week1     # Interactive chat with Week 1
  python nexi.py --tests            # Run test suite
        """
    )
    
    parser.add_argument('--week1', action='store_true', help='Use Week 1 system')
    parser.add_argument('--week2', action='store_true', help='Use Week 2 system') 
    parser.add_argument('--chat', action='store_true', help='Start interactive chat mode')
    parser.add_argument('--tests', action='store_true', help='Run test suite')
    parser.add_argument('--no-banner', action='store_true', help='Skip welcome banner')
    
    args = parser.parse_args()
    
    # Show banner unless disabled
    if not args.no_banner:
        print_banner()
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Determine what to run
    if args.tests:
        run_tests()
    elif args.week1 and not args.chat:
        run_week1_system()
    elif args.week2 and not args.chat:
        run_week2_system()
    elif args.chat or (not args.week1 and not args.week2 and not args.tests):
        # Default to interactive chat
        use_week2 = not args.week1  # Use Week 2 unless explicitly Week 1
        interactive_chat(use_week2)
    else:
        print(f"{Colors.WARNING}Please specify what you want to run. Use --help for options.{Colors.ENDC}")

if __name__ == "__main__":
    main()
