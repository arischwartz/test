#!/usr/bin/env python
# import
from __future__ import print_function
## batteries
import os
import sys
import pytest
## 3rd party
import numpy as np
import pandas as pd
## package
from SIPSim import Utils
from SIPSim.Commands import Gradient_fractions as Gradient_fractions_CMD

# data dir
test_dir = os.path.join(os.path.dirname(__file__))
data_dir = os.path.join(test_dir, 'data')


# tests
def test_cmd():
    comm_file = os.path.join(data_dir, 'comm-n2-unif.txt')
    args = [comm_file]
    Gradient_fractions_CMD.opt_parse(args)