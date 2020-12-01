#!/bin/bash
cd ..
source venv/bin/activate >/dev/null
cd - >/dev/null
./manager.py "$@"
