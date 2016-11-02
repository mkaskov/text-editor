#!/usr/bin/env bash
# Start with logging and data path
data_dir=/home/user/Documents/editor_data/NERparser4_071016
url_database=/home/user/datasets/construction_text_base/DB_3col281016.xlsx
#data_dir=/home/user/Documents/editor_data/NERparser3_051016
#data_dir=/home/user/Documents/editor_data/NERparser3_300916
echo "Text Editor on dataset "$data_dir
echo "Starting seq2seq model..."

# Select GPU-CPU devices. gpu0 <6, gpu1 6-8, cpu >8
#export TF_MIN_GPU_MULTIPROCESSOR_COUNT=5
export CUDA_VISIBLE_DEVICES=0

mkdir -p $data_dir/log
python /home/user/Documents/editor/app2web_ner.py --data_dir $data_dir/ --url_database $url_database --port=5003 --usegpu=true --reduce_gpu=true --web=true --forward_only=true 2>&1 | tee -a $data_dir/log/weblog.txt
