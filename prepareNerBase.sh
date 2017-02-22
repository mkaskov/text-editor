#!/usr/bin/env bash
data_dir=/home/andrew/kts-work/editor_data/Ner_7/
dburl=ttpuser:ttppassword@localhost:5432/ttp
ini=model_ini/ner5-model.ini

python3 prepareNerBase.py --ini $ini --outdir $data_dir --dburl $dburl
