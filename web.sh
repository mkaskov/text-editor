#!/usr/bin/env bash
# starting script

echo "Text Editor on dataset v8 by 01.08.2016"
echo "Starting seq2seq model..."
#sleep 2

# Select GPU-CPU devices. gpu0 <6, gpu1 6-8, cpu >8
export TF_MIN_GPU_MULTIPROCESSOR_COUNT=5

python /home/user/Documents/editor/app2web.py --data_dir /home/user/Documents/editor_data/text_editor_v8/ --train_dir /home/user/Documents/editor_data/text_editor_v8/checkpoints/ --size=512
