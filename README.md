# README

### Описание

Скрипты запуска обучения и обработки строк текста на базе алгоритма seq2seq

### Содержание

1. *app2web.py* - запуск WEB-сервиса flask

2. *data_utils.py* - предобработка данных, создание словарей, токенизация

3. *editor.py* - основной скрипт

4. *seq2seq_model.py* - описание модели нейросети


### editor.py

cd /home/user/Documents/tensorflow/tensorflow/models/rnn/editor/

*Обучение (train)*

python editor.py --data_dir /home/user/datasets/text_editor_v3/ --train_dir /home/user/datasets/text_editor_v3/checkpoints/ --size=512

*Распознавание/обработка данных (decode)*

python editor.py --decode --data_dir /home/user/datasets/text_editor_v3/ --train_dir /home/user/datasets/text_editor_v3/checkpoints/ --size=512


### app2web.py 

cd /home/user/Documents/tensorflow/tensorflow/models/rnn/editor/

python app2web.py --data_dir /home/user/datasets/text_editor_v3/ --train_dir /home/user/datasets/text_editor_v3/checkpoints/ --size=512


