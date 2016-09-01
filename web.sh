#!/usr/bin/env bash
# starting script

echo "Text Editor on dataset v15"
echo "Starting seq2seq model..."
#sleep 2

# Select GPU-CPU devices. gpu0 <6, gpu1 6-8, cpu >8
export TF_MIN_GPU_MULTIPROCESSOR_COUNT=5

python /home/user/Documents/editor/app2web.py --data_dir /home/user/Documents/editor_data/text_editor_v15/ --port=5002 --reduce_gpu=True
