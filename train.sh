#!/usr/bin/env bash
data_dir=/home/user/Documents/editor_data/NERparser4_071016
#data_dir=/home/user/Documents/editor_data/NERparser3_051016
#data_dir=/home/user/Documents/editor_data/text_editor_v22

mkdir -p $data_dir/log
python editor.py --data_dir $data_dir/ 2>&1 | tee -a $data_dir/log/log.txt 

