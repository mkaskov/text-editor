#!/usr/bin/env bash
data_dir=/home/user/Documents/editor_data/test
mkdir -p $data_dir/log
python editor.py --data_dir $data_dir/ 2>&1 | tee -a $data_dir/log/log.txt 

