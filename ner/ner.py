#! /usr/bin/env python
# -*- coding: utf-8 -*-
# by PureMind

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from nnet import data_utils as du
from util.textUtil import dotsArr
from util import textUtil as tu

def getEntitys(sent_tokens, outputs, vocab, startTag, middleTag, endTag, lastCheck=False, prinStats=False,
               ignoreCategory=False):
    orig_val_arr = [vocab[x] for x in outputs]

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

    for item in entity:
        thisType = True
        for tag in item[1]:
            if not tag in [startTag, middleTag, endTag]:
                thisType=False
        if thisType: finalEntity.append(item)

    return finalEntity

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
    return [x[0].strip() for x in entity]

def check_integrity(orig, cat, ent):
    final = "".join(du.tokenizer_tpp(cat + "".join(ent),core._TTP_WORD_SPLIT))
    orig = "".join(du.tokenizer_tpp(tu.removeSamples(orig, core),core._TTP_WORD_SPLIT))

    if not orig == final:
        print("\n----------------Integrity False----------------------------")
        print(orig)
        print(final)

    return orig == final

def clearSingleDots(entity):
    retValue = []
    lastI = -1
    for i,current in enumerate(entity):
        if not i == lastI:
            if i+1<len(entity):
                next = entity[i+1][0]
                currentE = current[0]
                nextTokens = du.tokenizer_tpp(next, core._TTP_WORD_SPLIT)
                if len(nextTokens)==1:
                    if nextTokens[0] in dotsArr:
                        retValue.append([currentE+" "+next,current[1]+entity[i+1][1]])
                        lastI = i+1
                    else: retValue.append(current)
                else: retValue.append(current)
            else: retValue.append(current)

    return retValue

def cleanBeginigDots(entity):
    for i, current in enumerate(entity):
        if i-1>=0:
           tokens = du.tokenizer_tpp(current[0], core._TTP_WORD_SPLIT)
           tokensNer =  current[1]

           if tokens[0] in dotsArr:
               entity[i-1][0] += " " + tokens[0]
               entity[i-1][1] += tokensNer[0]
               entity[i][0] =  " ".join(tokens[1:len(tokens)])
               entity[i][1] = tokensNer[1:len(tokensNer)]

    return entity

def recognize_entity(sentecesEntity):
    entity = []
    category = []
    ignoreCategory = True

    for i, sent in enumerate(sentecesEntity):
        outputs, rev_out_vocab = core.recognition(sent,printStats=False)

        sentTokens = du.tokenizer_tpp(sent, core._TTP_WORD_SPLIT)

        if i == 0:
            category = getEntitys(sentTokens, outputs, rev_out_vocab, '[K]', '[_K_]', '[/K]')

            if len(category)>0:
                sentTokens = sentTokens[len(category[0][1]):len(sentTokens)]
                outputs = outputs[len(category[0][1]):len(outputs)]

        currEntity = getEntitys(sentTokens, outputs, rev_out_vocab, '[At]', '[_At_]', '[/At]', lastCheck=True,
                                prinStats=True, ignoreCategory=ignoreCategory)
        ignoreCategory = True

        entity += currEntity

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

def clean_tags(category,entity):
    entity = clean_tags_entity(entity)
    category = clean_tags_entity(category)

    return category,entity

def parse_tags(text,core_):
    window = 30
    global core
    core = core_

    tokens = du.tokenizer_tpp(text,core._TTP_WORD_SPLIT)
    clusters = int(len(tokens) / window)
    sentecesEntity = split_text(tokens, clusters, window)
    entity, category = recognize_entity(sentecesEntity)
    entity = concat_entity(entity, '[At]', '[_At_]', '[/At]')
    category = concat_entity(category, '[K]', '[_K_]', '[/K]')
    entity = end_to_start_concat_entity(entity, '[At]', '[_At_]', '[/At]')

    return category,entity

def parse(text,core_,cleanTags=True):
    global core
    core = core_

    category, entity = parse_tags(text, core_)
    entity = clearSingleDots(entity)
    entity = cleanBeginigDots(entity)

    if cleanTags:
        entity = clean_tags_entity(entity)
        category = category[0][0] if len(category) > 0 else ""

    return category,entity