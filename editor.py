#! /usr/bin/env python
# -*- coding: utf-8 -*-



from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from nnet import initialization, core

if __name__ == "__main__":
  FLAGS,_TTP_WORD_SPLIT,_buckets,useGPU = initialization.getParams()
  core = core.Core(FLAGS, _TTP_WORD_SPLIT, _buckets, web=False, reduce_gpu=False, forward_only = False,useGPU=useGPU)
  if FLAGS.self_test: core.self_test()
  elif FLAGS.decode: core.decode()
  else: core.train()