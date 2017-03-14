#!/usr/bin/env bash
# Start with logging and data path
data_dir=/home/andrew/kts-work/editor_data/NERparser5_50_210217
url_database=ttpuser:ttppassword@localhost:5432/ttp
echo "Text Editor on dataset "$data_dir
echo "Database: "$url_database
echo "Starting seq2seq model..."

export CUDA_VISIBLE_DEVICES=0

mkdir -p $data_dir/log
python3 app2web_ner.py --data_dir $data_dir/ --url_database $url_database --connect_to_db=true --port=5003 --usegpu=true --reduce_gpu=true --web=true --forward_only=true 2>&1 | tee -a $data_dir/log/weblog.txt