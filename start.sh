#!/bin/bash
set -e

#kill $(lsof -ti:8081) 2>/dev/null
#kill $(lsof -ti:8000) 2>/dev/null

#uv run python -m voice.main start &
#uv run python main.py &

python -m voice.main start &
python main.py &

wait -n

kill $(jobs -p) 2>/dev/null
exit 1