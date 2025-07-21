# 🧠 NEXi - Next Tech Intelligence
## Campus AI Assistant - Brain Team Implementation

[![Tests](https://img.shields.io/badge/tests-94%25%20passing-brightgreen)]()
[![Python](https://img.shields.io/badge/python-3.13.5-blue)]()
[![ML Accuracy](https://img.shields.io/badge/ML%20accuracy-83.5%25-brightgreen)]()

**Brain Team Members**: Krishna, Rajat  
**Status**: Week 2 Complete ✅  
**Version**: 2.0

---

## 🚀 Quick Start

### Option 1: Interactive Chat (Recommended)
```bash
python nexi.py
```

### Option 2: System Demos
```bash
python nexi.py --week1    # Run Week 1 keyword system
python nexi.py --week2    # Run Week 2 ML system
```

### Option 3: Run Tests
```bash
python nexi.py --tests
```

---

## 📋 Features

### Week 1 (Complete ✅)
- ✅ Keyword-based intent classification
- ✅ 8 core intent categories
- ✅ 30+ campus questions covered
- ✅ Basic testing framework

### Week 2 (Complete ✅)
- ✅ **ML-based classification** (83.5% accuracy)
- ✅ **120+ structured Q&A database**
- ✅ **Advanced fallback system**
- ✅ **Context-aware conversations**
- ✅ **Performance monitoring** (<100ms response time)
- ✅ **Comprehensive testing** (94% pass rate)

---

## 🎯 Supported Questions

| Category | Examples |
|----------|----------|
| 📍 **Location** | "Where is the library?", "How do I get to the gym?" |
| 🕐 **Hours** | "What time does the cafeteria close?", "Library hours?" |
| 📞 **Contact** | "IT support contact?", "Admissions phone number?" |
| ❓ **How-to** | "How do I connect to WiFi?", "How to register?" |
| 🎉 **Events** | "What events are happening?", "Sports games today?" |
| 👋 **Social** | "Hello NEXi", "Thanks for your help" |

---

## 🛠️ Installation

### 1. Clone & Setup
```bash
cd /Users/rajat/Developer/Projects/NEXi
source .venv/bin/activate  # or create new venv
pip install -r requirements.txt
```

### 2. Verify Installation
```bash
python nexi.py --tests
```

---

## 📊 Performance Metrics

| Metric | Week 1 | Week 2 |
|--------|--------|--------|
| Classification Method | Keywords | ML Ensemble |
| Accuracy | ~60% | **83.5%** |
| Response Time | ~50ms | **<100ms** |
| Database Size | Basic | **120+ entries** |
| Context Awareness | ❌ | ✅ |
| Fallback System | Basic | **Advanced** |

---

## 🧪 Testing

```bash
# Run all tests
python nexi.py --tests

# Run specific test suites
pytest tests/test_week2_brain.py -v  # Week 2 tests
pytest tests/test_brain.py -v        # Week 1 tests

# With coverage
pytest tests/ --cov=src/brain --cov-report=html
```

**Current Test Status**: 33/35 tests passing (94% pass rate)

---

## 📁 Architecture

```
src/brain/
├── week2_brain_system.py    # 🧠 Main integrated system
├── ml_classifier.py         # 🤖 ML-based classification
├── fallback_manager.py      # 🛡️ Fallback handling
└── enhanced_classifier.py   # 📈 Week 1 enhanced

data/campus_qa/
├── expanded_database.json   # 💾 120+ Q&A entries
└── essential_questions.json # 📋 Core questions
```

---

## 🔧 Advanced Usage

### Custom Training
```python
from src.brain.week2_brain_system import NEXiBrainSystem

brain = NEXiBrainSystem()
brain.ml_classifier.add_training_example("Where's the pool?", "find_location")
brain.ml_classifier.retrain_model()
```

### Performance Monitoring
```python
metrics = brain.get_performance_metrics()
print(f"Success rate: {metrics['success_rate']:.1f}%")
```

### Context-Aware Chat
```python
user_id = "student123"
response1 = brain.process_query("Where is the library?", user_id)
response2 = brain.process_query("What are their hours?", user_id)  # Uses context
```

---

## 🤝 Integration Ready

The Brain system provides clean APIs for other teams:

```python
# Simple query processing
response = brain.process_query("Where is the cafeteria?")
print(response['text'])       # Natural language response
print(response['intent'])     # Classified intent
print(response['confidence']) # Confidence score
```

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| NLTK data missing | `python -c "import nltk; nltk.download('punkt')"` |
| Import errors | Run from project root: `/Users/rajat/Developer/Projects/NEXi` |
| Dependencies missing | `pip install -r requirements.txt` |
| Tests failing | Check `python nexi.py --tests` for details |

---

## 📈 Future Roadmap

- [ ] Deep learning models (BERT integration)
- [ ] Voice integration with other teams
- [ ] Multi-language support
- [ ] Real-time campus API integration
- [ ] Persistent conversation memory

---

## 📞 Brain Team Contact

**Team Members**: Krishna, Rajat  
**Completion Status**: Week 2 ✅  
**System Status**: Production Ready 🚀

For questions or integration support, see `TUTORIAL.md` for comprehensive documentation.

---

*Built with ❤️ by the NEXi Brain Team*