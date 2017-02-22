#!/usr/bin/env bash
data_dir=/home/user/Documents/editor_data/NERparser5_50_210217
#data_dir=/home/user/Documents/editor_data/NERparser3_051016
#data_dir=/home/user/Documents/editor_data/text_editor_v22

export CUDA_VISIBLE_DEVICES=0
export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/usr/local/cuda/lib64:/usr/local/cuda/extras/CUPTI/lib64"
export CUDA_HOME=/usr/local/cuda
source ~/.profile

mkdir -p $data_dir/log
python3 editor.py --data_dir $data_dir/ --usegpu=true 2>&1 | tee -a $data_dir/log/log.txt 

