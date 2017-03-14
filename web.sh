#!/usr/bin/env bash
# Start with logging and data path
data_dir=/home/user/Documents/editor_data/text_editor_v22
echo "Text Editor on dataset "$data_dir
echo "Starting seq2seq model..."

# Select GPU-CPU devices. gpu0 <6, gpu1 6-8, cpu >8
#export TF_MIN_GPU_MULTIPROCESSOR_COUNT=5
export CUDA_VISIBLE_DEVICES=0
export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/usr/local/cuda/lib64:/usr/local/cuda/extras/CUPTI/lib64"
export CUDA_HOME=/usr/local/cuda
source ~/.profile

mkdir -p $data_dir/log
python3 app2web.py --data_dir $data_dir/ --port=5002 --usegpu=true --reduce_gpu=true --web=true --forward_only=true 2>&1 | tee -a $data_dir/log/weblog.txt