# README

### Описание

.......

### Содержание

app2web.py - запуск WEB-сервиса flask

data_utils.py - предобработка данных, создание словарей, токенизация

editor.py - основной скрипт

seq2seq_model.py - описание модели нейросети


### editor.py

cd /home/user/Documents/tensorflow/tensorflow/models/rnn/editor/

Обучение(train)

python editor.py --data_dir /home/user/datasets/text_editor_v3/ --train_dir /home/user/datasets/text_editor_v3/checkpoints/ --size=512

Распознавание/обработка данных(decode)

python editor.py --decode --data_dir /home/user/datasets/text_editor_v3/ --train_dir /home/user/datasets/text_editor_v3/checkpoints/ --size=512


### app2web.py 

cd /home/user/Documents/tensorflow/tensorflow/models/rnn/editor/

python app2web.py --data_dir /home/user/datasets/text_editor_v3/ --train_dir /home/user/datasets/text_editor_v3/checkpoints/ --size=512


