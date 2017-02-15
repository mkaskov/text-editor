#! /usr/bin/env python

# by Max8mk

"""Утилиты для создания токенов (tokenizing) и подготовки словарей (vocabularies)."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import gzip
import os
import re
import tarfile

from six.moves import urllib

from tensorflow.python.platform import gfile

# Специальные символы словаря - мы всегда ставим их в самом начале.
_PAD = "_PAD"
_GO = "_GO"
_EOS = "_EOS"
_UNK = "_UNK"
_START_VOCAB = [_PAD, _GO, _EOS, _UNK]

# Коды (токены) специальных символов
PAD_ID = 0
GO_ID = 1
EOS_ID = 2
UNK_ID = 3

# Регулярные выражения, используемые для создания токенов (tokenize).
_WORD_SPLIT = re.compile("([,.][ ]+|[!?\"':;)(])") # v2 (not tested)
_DIGIT_RE = re.compile(r"\d")

_TTP_WORD_SPLIT = None

def basic_tokenizer(sentence): #"""Very basic tokenizer: split the sentence into a list of tokens."""
  words = []
  for space_separated_fragment in sentence.strip().split():
    words.extend(re.split(_WORD_SPLIT, space_separated_fragment))
  return [w for w in words if w]

def tokenizer_tpp(t, _tokens):
  words = re.findall(_tokens, t)
  return [w for w in words if w]

def create_vocabulary(vocabulary_path, data_path, max_vocabulary_size,
                      tokenizer=None, normalize_digits=True,ext_TTP_WORD_SPLIT=_TTP_WORD_SPLIT):
  """Create vocabulary file (if it does not exist yet) from data file.

  Data file is assumed to contain one sentence per line. Each sentence is
  tokenized and digits are normalized (if normalize_digits is set).
  Vocabulary contains the most-frequent tokens up to max_vocabulary_size.
  We write it to vocabulary_path in a one-token-per-line format, so that later
  token in the first line gets id=0, second line gets id=1, and so on.

  Args:
    vocabulary_path: path where the vocabulary will be created.
    data_path: data file that will be used to create vocabulary.
    max_vocabulary_size: limit on the size of the created vocabulary.
    tokenizer: a function to use to tokenize each data sentence;
      if None, tokenizer_tpp will be used.
    normalize_digits: Boolean; если true, то все цифры заменяются на нуль.
  """
  if not gfile.Exists(vocabulary_path):
    print("Creating vocabulary %s from data %s" % (vocabulary_path, data_path))
    # print(ext_TTP_WORD_SPLIT.pattern)
    vocab = {}
    with gfile.GFile(data_path, mode="r") as f:
      counter = 0
      for line in f:
        counter += 1
        if counter % 100000 == 0:
          print("  processing line %d" % counter)
        tokens = tokenizer(line) if tokenizer else tokenizer_tpp(line,ext_TTP_WORD_SPLIT)
        for w in tokens:
          word = re.sub(_DIGIT_RE, "0", w) if normalize_digits else w
          if word in vocab:
            vocab[word] += 1
          else:
            vocab[word] = 1
      vocab_list = _START_VOCAB + sorted(vocab, key=vocab.get, reverse=True)
      if len(vocab_list) > max_vocabulary_size:
        vocab_list = vocab_list[:max_vocabulary_size]
      with gfile.GFile(vocabulary_path, mode="w") as vocab_file:
        for w in vocab_list:
          vocab_file.write(w + "\n")
          


def initialize_vocabulary(vocabulary_path):
  """Initialize vocabulary from file.

  We assume the vocabulary is stored one-item-per-line, so a file:
    dog
    cat
  will result in a vocabulary {"dog": 0, "cat": 1}, and this function will
  also return the reversed-vocabulary ["dog", "cat"].

  Args:
    vocabulary_path: path to the file containing the vocabulary.

  Returns:
    a pair: the vocabulary (a dictionary mapping string to integers), and
    the reversed vocabulary (a list, which reverses the vocabulary mapping).

  Raises:
    ValueError: if the provided vocabulary_path does not exist.
  """
  if gfile.Exists(vocabulary_path):
    rev_vocab = []
    with gfile.GFile(vocabulary_path, mode="r") as f:
      rev_vocab.extend(f.readlines())
    rev_vocab = [line.strip() for line in rev_vocab]
    vocab = dict([(x, y) for (y, x) in enumerate(rev_vocab)])
    return vocab, rev_vocab
  else:
    raise ValueError("Vocabulary file %s not found.", vocabulary_path)


def sentence_to_token_ids(sentence, vocabulary,
                          tokenizer=None, normalize_digits=True,ext_TTP_WORD_SPLIT=_TTP_WORD_SPLIT):
  """Convert a string to list of integers representing token-ids.

  For example, a sentence "I have a dog" may become tokenized into
  ["I", "have", "a", "dog"] and with vocabulary {"I": 1, "have": 2,
  "a": 4, "dog": 7"} this function will return [1, 2, 4, 7].

  Args:
    sentence: a string, the sentence to convert to token-ids.
    vocabulary: a dictionary mapping tokens to integers.
    tokenizer: a function to use to tokenize each sentence;
      if None, tokenizer_tpp will be used.
	normalize_digits: Boolean; если true, то все цифры заменяются на нуль.

  Returns:
    a list of integers, the token-ids for the sentence.
  """
  # если мы передали какую то свою функцию
  if tokenizer:
    words = basic_tokenizer(sentence)
  else:
    words = tokenizer_tpp(sentence,ext_TTP_WORD_SPLIT)
  if not normalize_digits:
    return [vocabulary.get(w, UNK_ID) for w in words]
  # Normalize digits by 0 before looking words up in the vocabulary.
  return [vocabulary.get(re.sub(_DIGIT_RE, "0", w), UNK_ID) for w in words]


def data_to_token_ids(data_path, target_path, vocabulary_path,
                      tokenizer=None, normalize_digits=True,ext_TTP_WORD_SPLIT=_TTP_WORD_SPLIT):
  """Tokenize data file and turn into token-ids using given vocabulary file.

  This function loads data line-by-line from data_path, calls the above
  sentence_to_token_ids, and saves the result to target_path. See comment
  for sentence_to_token_ids on the details of token-ids format.

  Args:
    data_path: path to the data file in one-sentence-per-line format.
    target_path: path where the file with token-ids will be created.
    vocabulary_path: path to the vocabulary file.
    tokenizer: a function to use to tokenize each sentence;
      if None, tokenizer_tpp will be used.
    normalize_digits: Boolean; если true, то все цифры заменяются на нуль.
  """
  if not gfile.Exists(target_path):
    print("Tokenizing data in %s" % data_path)
    # print(ext_TTP_WORD_SPLIT.pattern)
    vocab, _ = initialize_vocabulary(vocabulary_path)
    with gfile.GFile(data_path, mode="r") as data_file:
      with gfile.GFile(target_path, mode="w") as tokens_file:
        counter = 0
        for line in data_file:
          counter += 1
          if counter % 100000 == 0:
            print("  tokenizing line %d" % counter)
          token_ids = sentence_to_token_ids(line, vocab, tokenizer,
                                            normalize_digits,ext_TTP_WORD_SPLIT)
          tokens_file.write(" ".join([str(tok) for tok in token_ids]) + "\n")


def prepare_data(data_dir, in_vocabulary_size, out_vocabulary_size,ext_TTP_WORD_SPLIT=_TTP_WORD_SPLIT):
  """Сreate vocabularies and tokenize train and dev data.

  Args:
    data_dir: directory in which the data sets will be stored.
    in_vocabulary_size: size of the INPUT vocabulary to create and use.
    out_vocabulary_size: size of the OUTPUT vocabulary to create and use.

  Returns:
    A tuple of 6 elements:
      (1) path to the token-ids for INPUT training data-set,
      (2) path to the token-ids for OUTPUT training data-set,
      (3) path to the token-ids for INPUT development data-set,
      (4) path to the token-ids for OUTPUT development data-set,
      (5) path to the INPUT vocabulary file,
      (6) path to the OUTPUT vocabulary file.
  """
  
  # Get data to the specified directory.
  train_path = os.path.join(data_dir, "train-data")
  dev_path = os.path.join(data_dir, "dev-data")
  # train-data - большой набор данных, а dev-data - маленький

  # Create vocabularies of the appropriate sizes.
  in_vocab_path = os.path.join(data_dir, "vocab%d.input" % in_vocabulary_size)
  out_vocab_path = os.path.join(data_dir, "vocab%d.output" % out_vocabulary_size)
  create_vocabulary(in_vocab_path, train_path + ".input", in_vocabulary_size, normalize_digits=False,ext_TTP_WORD_SPLIT=ext_TTP_WORD_SPLIT)
  create_vocabulary(out_vocab_path, train_path + ".output", out_vocabulary_size, normalize_digits=False,ext_TTP_WORD_SPLIT=ext_TTP_WORD_SPLIT)

  # Create token ids for the training data.
  in_train_ids_path = train_path + (".ids%d.input" % in_vocabulary_size)
  out_train_ids_path = train_path + (".ids%d.output" % out_vocabulary_size)
  data_to_token_ids(train_path + ".input", in_train_ids_path, in_vocab_path, normalize_digits=False,ext_TTP_WORD_SPLIT=ext_TTP_WORD_SPLIT)
  data_to_token_ids(train_path + ".output", out_train_ids_path, out_vocab_path, normalize_digits=False,ext_TTP_WORD_SPLIT=ext_TTP_WORD_SPLIT)

  # Create token ids for the development data.
  in_dev_ids_path = dev_path + (".ids%d.input" % in_vocabulary_size)
  out_dev_ids_path = dev_path + (".ids%d.output" % out_vocabulary_size)
  data_to_token_ids(dev_path + ".input", in_dev_ids_path, in_vocab_path, normalize_digits=False,ext_TTP_WORD_SPLIT=ext_TTP_WORD_SPLIT)
  data_to_token_ids(dev_path + ".output", out_dev_ids_path, out_vocab_path, normalize_digits=False,ext_TTP_WORD_SPLIT=ext_TTP_WORD_SPLIT)

  return (in_train_ids_path, out_train_ids_path,
          in_dev_ids_path, out_dev_ids_path,
          in_vocab_path, out_vocab_path)
