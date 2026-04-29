#!/bin/bash
# Print the current public ngrok URL
curl -s http://localhost:4040/api/tunnels | python3 -c "
import json, sys
tunnels = json.load(sys.stdin).get('tunnels', [])
if not tunnels:
    print('ngrok not running yet — try again in a few seconds')
else:
    for t in tunnels:
        print(t['public_url'])
"
