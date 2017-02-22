from sqlalchemy.exc import ProgrammingError
from sqlalchemy import create_engine
from util import textUtil as tu
import pandas as pd
import numpy as np
import os, re,errno
import shutil
import datetime
import argparse
import configparser

dbUrl = "postgresql://ttpuser:ttppassword@localhost:5432/ttp"

_category = "category"
_input = "input"
_output = "output"

save_path = '/home/andrew/kts-work/editor_data/Ner'+datetime.datetime.now().strftime("%Y_%m_%d_%H_%M")+'/'
model_ini = 'model_ini/ner5-model.ini'
train_size = 0.9

pd.set_option('chained_assignment', None)

parser = argparse.ArgumentParser(description='Prepare Ner base for parser')
parser.add_argument('--ini', help='model ini path')
parser.add_argument('--outdir', help='full save path')
parser.add_argument('--dburl', help='full db url')

class Core(object):
    global _TTP_WORD_SPLIT
    global _TTP_SENTENCE_SPLIT
    
    def __init__(self,_TTP_WORD_SPLIT_STRING):
        self._TTP_WORD_SPLIT = re.compile(_TTP_WORD_SPLIT_STRING)
        self._TTP_SENTENCE_SPLIT = re.compile("[^;:,.!?\s][^;:,.!?\n\t]*(?:[;:,.!?](?!['\"]?\s|$)[^;:,.!?\n]*)*[;:,.!?\n]?['\"]?(?=\s|$)") #v2

    # подсчет количества слов в предложении
    def tokenizer_tpp(self,sentence):
        words = []
        try:
            words = re.findall(self._TTP_WORD_SPLIT, sentence)
        except TypeError:
            print ('TypeError: ',sentence)
        return len(words)

    # нарезка предложения на слова
    def tokenizer_words(self,sentence):
        words = []
        try:
            words = re.findall(self._TTP_WORD_SPLIT, sentence)
        except TypeError:
            print ('TypeError: ',sentence)
        return [w for w in words if w]

    # нарезка предложений на куски(короткие предложения)
    def sentence_split(self,sentence):
        #sentence = sentence.decode('utf-8')
        seq = []
        try:
            seq = re.findall(self._TTP_SENTENCE_SPLIT, sentence)
        except TypeError:
            print ('TypeError: ',sentence)
        #return seq
        #return [w.encode('utf-8') for w in seq if w]
        return [w for w in seq if w]

    # обработка коротких предложений
    def short_update(self,seq_in_m, seq_out_m):
        #выравнивание размера in и out
        while len(seq_out_m) != len(seq_in_m):
            if len(seq_out_m) > len(seq_in_m):
                seq_in_m.append('')
            else:
                seq_out_m.append('')

        lenseq = len(seq_in_m)
        i = 1 #начинаем обработку с первого (а не с нулевого!) 
        while i < lenseq:
            wcount_in = self.tokenizer_tpp(seq_in_m[i])
            #wcount_out = tokenizer_tpp(seq_out_m[i])

            # если предложение меньше 6 слов или меньше 30 символов то прилепить его к предыдущему
            if (wcount_in < 6) | (len(seq_in_m[i]) < 30):
                seq_in_m[i-1] = seq_in_m[i-1] + ' ' + seq_in_m[i]
                seq_out_m[i-1] = seq_out_m[i-1] + ' ' + seq_out_m[i]
                del seq_in_m[i]
                del seq_out_m[i]
                lenseq -= 1
            else:
                i += 1
            #print wcount,'||',len(seq_in_m[i]),'||', seq_in_m[i]

        return seq_in_m, seq_out_m

    # отрезает запятую если она последний символ предложения, а также удаляет двойные, начальные и конечные пробелы
    def comma_end(self,sentence):
        sentence = re.sub(r'\s+', ' ', sentence).strip() #удаляет двойные, начальные и конечные пробелы
        if sentence[-1:]==',':
            sentence = sentence[:-1]
        return sentence

    # отрезает знак пунктуации, если он последний символ предложения, а также удаляет двойные, начальные и конечные пробелы
    def punctuation_end(self,sentence):
        sentence = re.sub(r'\s+', ' ', sentence).strip() #удаляет двойные, начальные и конечные пробелы
        if sentence[-1:]==',': sentence = sentence[:-1]
        elif sentence[-1:]=='.': sentence = sentence[:-1]
        elif sentence[-1:]==':': sentence = sentence[:-1]
        elif sentence[-1:]==';': sentence = sentence[:-1]
        return sentence

    # очистка предложения
    def str_clearing(self,sentence):
        sentence = re.sub(r'\s+', ' ', sentence).strip() #удаляет двойные, начальные и конечные пробелы
        sentence = sentence.replace(' .', '.')
        sentence = sentence.replace(' ,', ',')
        sentence = sentence.replace(' ;', ';')
        sentence = sentence.replace(' :', ':')
        sentence = sentence.replace(',,', ',')
        sentence = sentence.replace('..', '.')
        sentence = sentence.replace(';;', ';')
        sentence = sentence.replace(',.', ',')
        sentence = sentence.replace(';.', ';')
        sentence = sentence.replace(':.', ':')
        sentence = sentence.replace(':,', ':')
        sentence = sentence.replace('.,', '.')
        sentence = sentence.replace(';,', ';')
        sentence = sentence.replace(':;', ':')
        sentence = sentence.replace('.;', '.')
        sentence = sentence.replace('.;', '.')
        return sentence

def get_ini_parameters(config_file):
    if not os.path.isfile(config_file):
        print ('[WARNING] File ', config_file, ' not found')
        exit(errno.EFAULT)

    parser = configparser.ConfigParser()
    parser.read(config_file)
    _conf_ints = [(key, int(value)) for key, value in parser.items('ints')]
    _conf_strings = [(key, str(value)) for key, value in parser.items('strings')]

    with open(config_file) as f:
        [_conf_strings.append(('regex',r[r.find('=')+1:].strip())) for r in f.readlines() if 'regex_string' in r]

    outDict = dict(_conf_ints + _conf_strings)
    return outDict['window_size'],outDict['regex']

def connectToDB(url_database):
    try:
        engine = create_engine(url_database)
        base = pd.read_sql_query('select * from "learnpair"', con=engine)
        base.drop('createddate', axis=1, inplace=True)
        base.drop('userid', axis=1, inplace=True)
        return base
    except ProgrammingError:
        print("error")
        exit(errno.EFAULT)

def prepareBase(base,core):
    base['orig'] = base[_input]
    base['orig'] = base['orig'].apply(lambda x: re.sub("[\s]+", " ", x))
    base = base.fillna(value='')
    base[_input] = base[_input].apply(lambda x: tu.getRaw(x, core))
    base[_category] = base[_category].apply(lambda x: tu.getRaw( tu.removeSamples(x,  core).strip(), core))
    base[_output] = base[_output].apply(lambda x: tu.prepareSuperscript(x))
    return base

def get_real_id_list():
    prepared_base = connectToDB(dbUrl)
    prepared_base = prepareBase(prepared_base, core)
    # print("loading base done")

    # print ("base", len(prepared_base))
    prepared_base = prepared_base.drop_duplicates(subset=[_category, _input])
    # print("temp base", len(prepared_base))

    idarray = prepared_base.as_matrix(columns=['id'])
    idarray = sorted([x[0] for x in idarray])
    return idarray

def get_ner_base(core):
    base = connectToDB(dbUrl)

    real_id_list = get_real_id_list()

    ner_base = base.loc[base['id'].isin(real_id_list)]

    ner_base[_category] = ner_base[_category].apply(lambda x: tu.removeSamples(x,  core).strip())
    ner_base[_output] = ner_base[_output].apply(lambda x: tu.prepareSuperscript(x))
    ner_base[_output] = ner_base[_output].apply(lambda x: tu.prepareCelsius(x))
    ner_base[_input] = ner_base[_input].apply(lambda x: tu.prepareSuperscript(x))
    ner_base[_input] = ner_base[_input].apply(lambda x: tu.prepareCelsius(x))
    print("ner base prepared")
    return ner_base

def get_InOutData(base):
    cat_word_first = '[K] '
    cat_word = '[_K_] '
    cat_word_last = '[/K] '
    attrib_word_first = '[At] '
    attrib_word = '[_At_] '
    attrib_word_last = '[/At] '
    delim_arr = ['. ', ' ', ', ', '; ']

    # формирует строку описания из столбцов category, in, a также вторую строку с соответсвующими тегами. (см пример ниже)
    category = ' '
    string_in = ''
    string_out = ''
    str_array_in = []
    str_array_out = []

    for delim in delim_arr:
        for index, row in base.iterrows():
            if row['category'] == ' ' or row['category'] == '': #если категория пустая, то не использовать эти строки
                continue
            elif row['category'].strip() != category: #если новая категория
                category = row['category'].strip()
                str_array_in.append(string_in)
                str_array_out.append(string_out)
                string_in = core.str_clearing(row['category'] + delim)

                string_out = cat_word_first
                for index in range(1, core.tokenizer_tpp(string_in) - 1):
                    string_out = string_out + cat_word
                if core.tokenizer_tpp(string_in)>1:
                    string_out = string_out + cat_word_last

            temp_string_in = core.str_clearing(row['input'] + delim)
            string_out = string_out + attrib_word_first
            for index in range(1, core.tokenizer_tpp(temp_string_in) - 1):
                string_out = string_out + attrib_word
            if core.tokenizer_tpp(temp_string_in)>1:
                string_out = string_out + attrib_word_last

            string_in = string_in + ' ' + temp_string_in

    print ('Создан массив %d строк.' % len(str_array_out))
    
    return str_array_in,str_array_out

def get_out_base(core, input_len_str=30):
    str_array_in, str_array_out = get_InOutData(get_ner_base(core))

    data0 = pd.DataFrame()
    totalInArr = []
    totalOutArr = []

    for i in range(0, len(str_array_out)):
        len_str = input_len_str
        words_in_arr = core.tokenizer_words(str_array_in[i])
        words_out_arr = core.tokenizer_words(str_array_out[i])
        len_seq = len(words_out_arr) - len_str
        if len_seq <= 0: #если длина предложения меньше 30 слов
            len_str = len(words_out_arr)
            len_seq = 1
        for j in range(0, len_seq):
            totalIn = ''
            totalOut = ''
            for z in range(j, j + len_str):
                totalIn += words_in_arr[z] + ' '
                totalOut += words_out_arr[z] + ' '
            totalInArr.append(totalIn)
            totalOutArr.append(totalOut)

    d = {"input":totalInArr , "output": totalOutArr}
    data0 = pd.concat([data0, pd.DataFrame(data=d)], ignore_index=True)
    data0['n_intype'] = data0.index + 1

    data = data0[(data0['input'] != '') | (data0['output'] != '')]
    print ('Создан массив %d строк.' % len(data))
    
    return data

def save_to_disk(inputDF):
    #shuffle
    inputDF = inputDF.reindex(np.random.permutation(inputDF.index))

    # разбиение на обучающую и тестовую выборки
    row = int(round(train_size * (len(inputDF) - 1)))
    train_in = inputDF['input'][:row]
    train_out = inputDF['output'][:row]
    dev_in = inputDF['input'][row:]
    dev_out = inputDF['output'][row:]

    if os.path.exists(save_path): print ('Ошибка! Директория %s уже существует! Сохранение отменено.' % save_path)
    else:
        os.mkdir(save_path , 0o7775)
        train_in.to_csv(save_path + 'train-data.input', sep='|', header=None, encoding='utf-8', index=False)
        train_out.to_csv(save_path  + 'train-data.output', sep='|', header=None, encoding='utf-8', index=False)
        dev_in.to_csv(save_path  + 'dev-data.input', sep='|', header=None, encoding='utf-8', index=False)
        dev_out.to_csv(save_path  + 'dev-data.output', sep='|', header=None, encoding='utf-8', index=False)
        os.mkdir(save_path + 'ini/', 0o7775)
        os.mkdir(save_path + 'log/', 0o7775)
        os.mkdir(save_path + 'checkpoints/', 0o7775)
        shutil.copy2(model_ini, save_path + 'ini/model.ini')
        print ('[Выполнено] данные подготовлены в папке %s' % save_path)

def get_statistics(inputDF):
    inputDF['words_in'] = inputDF['input'].apply(core.tokenizer_tpp)
    inputDF['words_out'] = inputDF['output'].apply(core.tokenizer_tpp)
    print ('Длина входных предложений: средняя %.3f , максимальная %d' % (inputDF['words_in'].mean(), inputDF['words_in'].max()))
    print ('Длина выходных предложений: средняя %.3f , максимальная %d' % (inputDF['words_out'].mean(), inputDF['words_out'].max()))

def check_word_count(str_in,str_out):
    index = 6763
    print (str_in[index])
    print (core.tokenizer_tpp(str_in[index]))
    print (str_out[index])
    print (core.tokenizer_tpp(str_out[index]))

    # проверка количества слов
    c_in = 0
    c_out = 0
    for index in range(0, len(str_array_out)):
        c_in += core.tokenizer_tpp(str_in[index])
        c_out += core.tokenizer_tpp(str_out[index])

    print ("Количество слов во входных и выходных предложениях %d %d" % (c_in, c_out))
    if not c_in == c_out:
        print ('[warning]', "количество слов во входном и выходном наборе не совпадает")
        exit(errno.EFAULT)

args = parser.parse_args()

if(args.ini): model_ini = args.ini
if(args.outdir): save_path = args.outdir
if(args.dburl): dbUrl = 'postgresql://'+args.dburl

windows_size, _TTP_WORD_SPLIT_STRING = get_ini_parameters(model_ini)

core = Core(_TTP_WORD_SPLIT_STRING)
out_base = get_out_base(core,windows_size)
save_to_disk(out_base)