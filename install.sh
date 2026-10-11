#!/bin/bash
set -e
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install
playwright install-deps
mkdir -p data/backups projects logs
echo "Installed. Run ./start.sh"
