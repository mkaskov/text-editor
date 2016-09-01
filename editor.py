#! /usr/bin/env python
# -*- coding: utf-8 -*-



from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import initialization
import core as Core

if __name__ == "__main__":
  FLAGS,_TTP_WORD_SPLIT,_buckets = initialization.getParams()
  core = Core.Core(FLAGS,_TTP_WORD_SPLIT,_buckets,web=False,reduce_gpu=False,forward_only = False)
  if FLAGS.self_test: core.self_test()
  elif FLAGS.decode: core.decode()
  else: core.train()