#!/bin/bash
# Quick test script to demonstrate the interactive chat
cd /Users/rajat/Developer/Projects/NEXi

# Test a few queries non-interactively
echo "Testing NEXi Interactive Mode..."

echo -e "Where is the library?\nWhat are their hours?\nThanks\nquit" | /Users/rajat/Developer/Projects/NEXi/.venv/bin/python -c "
import sys
sys.path.insert(0, '.')
from nexi import interactive_chat
import sys

# Mock input for testing
inputs = ['Where is the library?', 'What are their hours?', 'Thanks', 'quit']
input_iter = iter(inputs)

original_input = input
def mock_input(prompt=''):
    try:
        value = next(input_iter)
        print(f'{prompt}{value}')
        return value
    except StopIteration:
        return 'quit'

# Replace input function temporarily
import builtins
builtins.input = mock_input

# Test interactive chat
try:
    interactive_chat(use_week2=True)
except:
    pass
"
