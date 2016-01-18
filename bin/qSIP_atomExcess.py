#!/usr/bin/env python

#--- Option parsing ---#
"""
qSIP_atomExcess: calculate isotope enrichment from qSIP data

Usage:
  qSIP_atomExcess [options] <OTU_table> <exp_design>
  qSIP_atomExcess -h | --help
  qSIP_atomExcess --version

Options:
  <OTU_table>     OTU table file 
                  (must contain an 'abs_abund' column).
  <exp_design>    Experimental design table. (See Description)
  -i=<i>          Isotope (13C or 18O).
                  [Default: 13C]
  --version       Show version.
  --debug         Debug mode.
  -h --help       Show this screen.


Description:

  'exp_design' input file
  -----------------------
  2-column table: <library><tab><control|treatment>

References:
  Hungate BA, Mau RL, Schwartz E, Caporaso JG, Dijkstra P, Gestel N van, et
  al. (2015). Quantitative Microbial Ecology Through Stable Isotope Probing.
  Appl Environ Microbiol AEM.02280-15.
"""

# import
## batteries
from docopt import docopt
import sys
import os
from functools import partial
## 3rd party
import numpy as np
import pandas as pd
## application libraries
scriptDir = os.path.dirname(__file__)
libDir = os.path.join(scriptDir, '../lib/')
sys.path.append(libDir)

from OTU_Table import OTU_table
import QSIP_atomExcess

    


# main
if __name__ == '__main__':
    Uargs = docopt(__doc__, version='0.1')
    otu = QSIP_atomExcess.qSIP_atomExcess(Uargs)
    otu.to_csv(sys.stdout, sep='\t', index=False)
    

        
