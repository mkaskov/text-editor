#! /usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import re

def split_string(text,maxWords):
  pat = ur"\[\/K\]|\[K\]|\[At\]|\[\/At\]|гост\s[\d.]+—?\-?[\d]+|ГОСТ\s[\d.]+—?\-?[\d]+|[а-яА-Я]+\/[а-яА-Я\d]+\.{1}[а-яА-Я\d]+\.{1}|[а-яА-Я]+\/\([^()]+\)|[^\s\d.,!?():;/\\|<>\"\'=–—\-+_*\xA0IV\[\]≥≤~”“_ₒ∙°··\x23«»]+\d?\/[^\s.,!?():;/\\|<>\"\'=–—\-+_*\xA0IV\[\]≥≤~”“_ₒ∙°··\x23«»]+|м{1,2}[\d⁰¹²³⁴⁵⁶⁷⁸⁹]|см[\d⁰¹²³⁴⁵⁶⁷⁸⁹]|дм[\d⁰¹²³⁴⁵⁶⁷⁸⁹]|[a-zA-Zа-яА-ЯёЁ]*[^\s\d.\\!?,:;()\"\'<>%«»±^…–—\-*=/+\xA0@·∙\[\]°ₒ”“·≥≤~_\x23]|[\d()\\!?\'\"<>%,:;±«»^…–—\-*=/+@·∙\[\]°ₒ”“·≥≤~_\x23]|\.{3}|\.{1}"
  _splt = re.compile(pat)

  def tokenizer_tpp(t):
    words = re.findall(_splt, t)
    return [w for w in words if w]

  new_tokens =  tokenizer_tpp(text)

  specTags = ['[K]','[/K]','[At]','[/At]']

  totalWordsCount = []

  for i,token in enumerate(new_tokens):
    if token not in specTags: totalWordsCount.append(i)

  def construct_string(tokens, startIndex, maxTokens, wordsCount):
    currStr = ''
    currStrTag = ''
    currentStrArr = []
    currentStrArrTag = []

    zzz_start = wordsCount[startIndex]
    if startIndex+maxTokens-1 < len(wordsCount):
      end_index = startIndex+maxTokens-1
    else: return '',''
    zzz_end = wordsCount[end_index]

    currIndex = zzz_start

    if zzz_start>0 and tokens[zzz_start-1] in specTags:
      currentStrArrTag.append(tokens[zzz_start-1])
    while currIndex <=zzz_end:
      token = tokens[currIndex]
      currentStrArrTag.append(token)
      if token not in specTags:
        currentStrArr.append(token)
      currIndex+=1
    if zzz_end+1<len(tokens) and tokens[zzz_end+1] in specTags:
      currentStrArrTag.append(tokens[zzz_end + 1])

    currStr += " ".join(currentStrArr);
    #currStr += "\n"
    currStrTag += " ".join(currentStrArrTag);
    #currStrTag += "\n"

    return currStr,currStrTag

  totalIn = []
  totalOut = []

  for i in range(len(totalWordsCount)):
    inputStr, outStr = construct_string(new_tokens, i, maxWords, totalWordsCount)
    if(len(inputStr)>0 and len(outStr)>0):
      totalIn.append(inputStr)
      totalOut.append(outStr)

  return totalIn,totalOut



# my_text = ur"[K] Труба тип 1. [/K] [At] Труба должна быть стальная покрыта пенополиуретановой изоляцией при условном давлении не менее 1,5 МПа не более 1,6 МПа   в полиэтиленовой оболочке. [/At] [At] Температурный режим: [/At] [At] подающий не менее 140 °С не более 150 °С. [/At] [At] обратный не менее 65 °С не более 700. [/At] [At] Материал трубы: сталь. [/At] [At] Наружный диаметр трубы: не менее 57 мм. [/At] [At] Толщина стенки трубы: не менее 3,5 мм не более 3,7мм. [/At]"
# totalIn,totalOut = split_string(my_text,30)
#
# print (totalIn)
# print (totalOut)