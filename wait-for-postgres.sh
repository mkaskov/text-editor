#!/bin/bash
while ! curl http://db:5432/ 2>&1 | grep '52'
do
  echo "checking db..."
  sleep 10
done
echo "Starting parser..."
sh web_GraphParser.sh