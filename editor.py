#! /usr/bin/env python
# -*- coding: utf-8 -*-



from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from nnet import initialization, core
import docker_prepare


if __name__ == "__main__":
  FLAGS, _TTP_WORD_SPLIT, _buckets, app_options = initialization.getParams()
  if app_options["fixdataset"]: docker_prepare.fix_dataset()
  core = core.Core(FLAGS, _TTP_WORD_SPLIT, _buckets, app_options)
  if FLAGS.self_test: core.self_test()
  elif FLAGS.decode: core.decode()
  else: core.train()