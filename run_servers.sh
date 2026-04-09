#!/bin/bash
set -e

cd /app/backend
pip install -r requirements.txt
python main.py &

cd /app/frontend
npm install
npm run build
npm start &
