#!/usr/bin/env bash
data_dir=/home/user/Documents/editor_data/NERparser4_071016
url_database=ttpuser:ttppassword@localhost:5432/ttp
echo "Text Editor on dataset "$data_dir
echo "Database: "$url_database
echo "Starting seq2seq model..."

export CUDA_VISIBLE_DEVICES=0

sleep 50
while ! curl http://db:5432/ 2>&1 | grep '52'
do
  echo "checking db..."
  sleep 50
done
echo "Starting parser..."
python3 app2web_graph_2.py --data_dir $data_dir/ --url_database $url_database --port=5003 --usegpu=true --reduce_gpu=true --web=true --forward_only=true