#!/usr/bin/env bash
echo "Text Editor on dataset v17"
echo "Starting seq2seq model..."

# Select GPU-CPU devices. gpu0 <6, gpu1 6-8, cpu >8
export TF_MIN_GPU_MULTIPROCESSOR_COUNT=5

# Start with logging and data path
data_dir=/home/user/Documents/editor_data/text_editor_v17
mkdir -p $data_dir/log
python /home/user/Documents/editor/app2web.py --data_dir $data_dir/ --port=5002 2>&1 | tee -a $data_dir/log/weblog.txt