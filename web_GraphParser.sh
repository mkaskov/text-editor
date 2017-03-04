#!/usr/bin/env bash
sleep 100
while ! curl http://db:5432/ 2>&1 | grep '52'
do
  echo "checking db..."
  sleep 50
done
echo "Starting parser..."
python3 app2web_graph.py