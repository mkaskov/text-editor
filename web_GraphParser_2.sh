#!/usr/bin/env bash
sleep 20
url_database=localhost:5432/ttp
echo "Database: "$url_database
echo "Starting seq2seq model..."

while ! curl http://$url_database/ 2>&1 | grep '52'
do
  echo "checking db..."
  sleep 50
done
echo "Starting parser..."
python3 app2web_graph_2.py --url_database ttpuser:ttppassword@$url_database --port 5003