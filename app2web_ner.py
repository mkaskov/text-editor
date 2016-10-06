#! /usr/bin/env python
# -*- coding: utf-8 -*-
# by PureMind

"""ONLY for start app flask for web decoding data.

Директория с данными --data_dir 
Директория с обученной моделью --train_dir.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from cStringIO import StringIO
from flask import Flask, request, jsonify
from nnet import initialization, core, data_utils
import re

# Obtain the flask app object
app = Flask(__name__)

global core


def getEntitys(sent_tokens, outputs, vocab, startTag, middleTag, endTag, lastCheck=False, prinStats=False,
               ignoreCategory=False):
    orig_val_arr = []
    for x in outputs: orig_val_arr.append(vocab[x])

    dSize = len(sent_tokens) - len(orig_val_arr)
    if dSize > 0: [orig_val_arr.append('[_At_]') for i in xrange(0, dSize)]

    if ignoreCategory:
        for i, item in enumerate(orig_val_arr):
            if item in ['[K]', '[_K_]', '[/K]']: orig_val_arr[i] = '[_At_]'


    startIndex = 0
    endIndex = -1
    entitysID = []

    for i, item in enumerate(orig_val_arr):
        if item == startTag: startIndex = i
        if item == endTag: endIndex = i
        if not item in [startTag,middleTag,endTag]: endIndex = i-1
        if endIndex >= startIndex and startIndex > -1:
            entitysID.append([startIndex, endIndex])
            if not item in [startTag,middleTag,endTag]:
                startIndex = i
            else:
                startIndex = i + 1

            endIndex = -1

    if len(entitysID) > 0:
        if startIndex < len(orig_val_arr):
            if orig_val_arr[startIndex] in [startTag, middleTag, endTag]:
                if entitysID[-1][1] != len(orig_val_arr) - 1 and entitysID[-1][1] != -1:
                    entitysID.append([startIndex, len(orig_val_arr) - 1])

    if lastCheck and len(entitysID) == 0:
        entitysID.append([startIndex, len(sent_tokens) - 1])

    if len(entitysID)>0:
        if not entitysID[0][0]==0: entitysID = [[0,entitysID[0][0]-1]] + entitysID
        if not entitysID[-1][1]+1 == len(orig_val_arr): entitysID.append([entitysID[-1][1]+1,len(orig_val_arr)-1])

    entity = []

    for item in entitysID:
        ent = ''
        tag = []
        for i in range(item[0], item[1] + 1):

            if i > len(sent_tokens) - 1: break

            ent += ' ' + sent_tokens[i]

            tag.append(orig_val_arr[i])

        if len(ent) > 0: entity.append([ent, tag])

    finalEntity = []

    for i,item in enumerate(entity):
        thisType = True
        for tag in item[1]:
            if not tag in [startTag, middleTag, endTag]:
                thisType=False
        if thisType: finalEntity.append(item)

    entity = finalEntity

    # if len(entitysID)>0:
    #     print("------------------------------- Result recogintion %s %s %s -----------------------------------------" % (startTag,middleTag,endTag))
    #     print(" ".join(sent_tokens))
    #     print(" ".join(orig_val_arr))
    #     print(entitysID)
    #
    #     [print(i[0],i[1]) for i in entity]
    #     print ("\n")

    return entity


def concat_entity(entity_arr, startTag, middleTag, endTag):

    def recusive_concat(entity, startTag, middleTag, endTag):

        finalEntity = []
        lastConcatI = -1

        for i, item in enumerate(entity):
            if not lastConcatI == i:
                if i + 1 < len(entity):

                    inE = item[1]
                    outE = entity[i + 1][1]

                    FI_ = inE[0]
                    LI_ = inE[-1]

                    _FI = outE[0]
                    _LI = outE[-1]

                    iReady = False
                    oReadey = False

                    if len(inE) == 1:
                        if FI_ in [startTag, middleTag]: iReady = True
                    else:
                        if FI_ in [startTag, middleTag] and LI_ == middleTag: iReady = True

                    if len(outE) == 1:
                        if _LI in [middleTag, endTag]: oReadey = True
                    else:
                        if _FI == middleTag and _LI in [middleTag, endTag]: oReadey = True

                    if iReady and oReadey:
                        str = item[0] + entity[i + 1][0]
                        tag = []
                        tag += item[1] + entity[i + 1][1]
                        finalEntity.append([str, tag])
                        lastConcatI = i + 1

                    else:
                        finalEntity.append(item)

                else:
                    finalEntity.append(item)

        return finalEntity, lastConcatI

    finalEntity, lastConcatI = recusive_concat(entity_arr, startTag, middleTag, endTag)

    while lastConcatI > 0: finalEntity, lastConcatI = recusive_concat(finalEntity, startTag, middleTag, endTag)

    return finalEntity

def end_to_start_concat_entity(entity_arr, startTag, middleTag, endTag):
    retValue = []
    lastIndex = -1
    for i,item in enumerate(entity_arr):
        if i+1<len(entity_arr):
            if not lastIndex==i:
                curr = item[1]
                next = entity_arr[i+1][1]
                last_ = curr[-1]
                _last = next[-1]

                if last_ in [startTag,middleTag] and _last == endTag:
                    text = item[0]+ " " + entity_arr[i+1][0]
                    tag = curr + next
                    retValue.append([text,tag])
                    lastIndex = i+1

                else: retValue.append(item)
        else:
            if not lastIndex == i:
                retValue.append(item)

    return retValue

def clean_tags_entity(entity):
    retValue = []
    for item in entity:
        retValue.append(item[0])
    return retValue


def clean_duplicates_entity(entity):
    retValue = []
    lastI = -10
    for i, sent in enumerate(entity):
        if i > 0 and not lastI + 1 == i:
            prev = data_utils.tokenizer_tpp(entity[i - 1], core._TTP_WORD_SPLIT)
            curr = data_utils.tokenizer_tpp(sent, core._TTP_WORD_SPLIT)
            lastI = i
            if prev[len(prev) - 1] == curr[0]: prev = prev[0:-1]
            retValue.append(" ".join(prev))
            retValue.append(" ".join(curr))

    return retValue


def check_integrity(orig, cat, ent):
    category = ''
    if len(cat)>0: category=cat[0]
    final = category + " ".join(ent)
    final = re.sub("[\s\xA0]+", "", final)
    orig = re.sub("[\s\xA0]+", "", orig)

    print(orig)
    print(final)

    return orig == final


def upgradeSent(sentecesEntity, tokens, window, addWindow=1):
    clusters = int(len(tokens) / window) + 1
    retValue = []

    for iterator in xrange(0, clusters):
        sourceSent = sentecesEntity[iterator]

        startToken = ''
        endToken = ''

        if iterator > addWindow - 1:
            if not tokens[iterator * window - addWindow].isdigit():
                for z in xrange(0, addWindow): startToken += tokens[iterator * window - (addWindow - z)] + ' '

        if (iterator * window + window + addWindow - 1) < len(tokens):
            if not tokens[iterator * window + window + addWindow - 1].isdigit():
                for z in xrange(0, addWindow): endToken += tokens[iterator * window + window + z]

        print('[', iterator, '] [SOURCE  ]', sourceSent.strip())
        tempSent = startToken + ' ' + sourceSent + ' ' + endToken
        print('[', iterator, '] [REFACTOR]', tempSent.strip())

        retValue.append(tempSent)

    return retValue


def recognize_entity(sentecesEntity):
    entity = []
    category = []
    ignoreCategory = True

    for i, sent in enumerate(sentecesEntity):
        # print("\n------------------------------- Start recogintion -----------------------------------------")
        # print(sent)

        outputs, rev_out_vocab = core.recognition(sent)

        sentTokens = data_utils.tokenizer_tpp(sent, core._TTP_WORD_SPLIT)

        if i == 0:
            category = getEntitys(sentTokens, outputs, rev_out_vocab, '[K]', '[_K_]', '[/K]')

            # if len(category) > 0: ignoreCategory = True

            if len(category)>0:
                sentTokens = sentTokens[len(category[0][1]):len(sentTokens)]
                outputs = outputs[len(category[0][1]):len(outputs)]

        currEntity = getEntitys(sentTokens, outputs, rev_out_vocab, '[At]', '[_At_]', '[/At]', lastCheck=True,
                                prinStats=True, ignoreCategory=ignoreCategory)
        ignoreCategory = True

        entity += currEntity

        # print("\n---Parse---\n")
        #
        # print (len(outputs),outputs)
        #
        # [print(x[0], "\n", x[1],"\n",len(x[1])) for x in currEntity]

    return entity, category


def split_text(tokens, clusters, window):
    sentecesEntity = []

    for i in xrange(0, clusters):
        sent = ''
        for y in xrange(i * window, (i + 1) * window): sent += ' ' + tokens[y]
        sentecesEntity.append(sent)
    sent = ''
    for i in xrange(clusters * window, len(tokens)): sent += ' ' + tokens[i]
    sentecesEntity.append(sent)

    return sentecesEntity


@app.route('/decode_sentense', methods=['POST'])
def decode_sentense():
    window = 30

    global printStats
    printStats = False
    integrity = False

    query = request.json['query'].encode("utf-8")
    tokens = data_utils.tokenizer_tpp(query, core._TTP_WORD_SPLIT)

    clusters = int(len(tokens) / window)

    sentecesEntity = split_text(tokens, clusters, window)

    # sentecesEntity = upgradeSent(sentecesEntity, tokens, window, addWindow=1) #эксперементальный способ увеличения данных для выборки

    entity, category = recognize_entity(sentecesEntity)

    entity = concat_entity(entity, '[At]','[_At_]','[/At]')
    category = concat_entity(category, '[K]','[_K_]','[/K]')

    entity = end_to_start_concat_entity(entity, '[At]','[_At_]','[/At]')

    entity = clean_tags_entity(entity)
    category = clean_tags_entity(category)

    # entity = clean_duplicates_entity(entity) #Своевольно режет массив почему то

    integrity = check_integrity(query, category, entity)

    return jsonify(_integrity=integrity, entity=entity, category=category)

if __name__ == "__main__":
    FLAGS, _TTP_WORD_SPLIT, _buckets = initialization.getParams()
    core = core.Core(FLAGS, _TTP_WORD_SPLIT, _buckets, web=True, reduce_gpu=True, forward_only=True)
    app.run(host='0.0.0.0', port=FLAGS.port, debug=True, use_reloader=False, threaded=True)
