#!/usr/bin/env python

"""
OTU_subsample: simulate sequencing by subsampling from an OTU table

Usage:
  OTU_subsample [options] <OTU_table_file>
  OTU_subsample -h | --help
  OTU_subsample --version

Options:
  <OTU_table_file>    OTU table file.
  --dist=<nd>         Distribution used to select number of samples per community.
                      See numpy.random for possible distributions.
                      For the same number of samples per community, use 'uniform'.
                      [Default: normal]
  --dist_params=<dp>  Parameters for the distribution used to select the number. 
                      of samples per community.
                      Input format: 'key1:value1,key2:value2,keyN:valueN'
                      To sample exactly X from each community, use: 'low:X,high:X'
                      [Default: loc:20000,scale:5000]
  --min_size=<m>      Minimum sample size (truncates distribution).
  --max_size=<n>      Maximum sample size (truncates distribution). 
  --samp_min          Use the minimum number of taxa in any community as the
                      number subsampled for all communities. Overrides '--dist*'
                      options.
  --no-replace        Subsample without replacement.         
  --walk=<w>          Set fraction order a autocorrelating based on a random 
                      walk. This parameter determines the max walk step size.
                      The greater the size, the less autocorrleation.
                      Zero = completely random (no autocorrelation).
                      [Default: 0]
  --base=<b>          Logarithm base for log-transform of taxon counts.
                      Taxon counts used set sampling probabilities;
                      a larger base will even out probabilities.
  -h --help           Show this screen.
  --version           Show version.
  --debug             Debug mode

Description:
  Subsample from an OTU table created by the OTU_table subcommand.

  This is used to simulate the actual sequencing of DNA/RNA from each
  gradient fraction.
  
  The 'dist' and 'dist_params' options are used to simulate uneven numbers
  of sequences (here, signified as OTUs) per sample.

  If a community has a total count of 0, subsampling will produce a community
  with a total count of 0 (can't subsample from nothing). 

  Parameters where a value is required but not set by default are not used.

  Output
  ------
  A tab-delimited OTU table written to STDOUT.
"""

# import
## batteries
from docopt import docopt
import os, sys
## application libraries
scriptDir = os.path.dirname(__file__)
libDir = os.path.join(scriptDir, '../lib/')
sys.path.append(libDir)

from OTU_Table import OTU_table
import Utils


def main(Uargs):
    Uargs['--walk'] = int(Uargs['--walk'])

    # dist params as dict
    Uargs['--dist_params'] = Utils.parseKeyValueString(Uargs['--dist_params'])
    
    otu_tbl = OTU_table.from_csv(Uargs['<OTU_table_file>'], sep='\t')

    # if --samp_min, get min comm size, set dist to uniform w/ same low & high
    if Uargs['--samp_min']:
        min_size = otu_tbl.get_comm_size_stats()[0]
        assert min_size > 0, '--samp min is < 1. Nothing to sample!'
        Uargs['--dist_params'] = {'low':min_size, 'high':min_size}
        
    # setting subsampling size distribution
    otu_tbl.set_samp_dist(samp_dist=Uargs['--dist'],
                          samp_dist_params=Uargs['--dist_params'])
    
    # subsampling
    df = otu_tbl.subsample(no_replace=Uargs['--no-replace'],
                           walk=Uargs['--walk'], 
                           min_size=Uargs['--min_size'], 
                           max_size=Uargs['--max_size'], 
                           base=Uargs['--base'])

    # writing out table
    df.to_csv(sys.stdout, sep='\t', index=False)
    

# main
if __name__ == '__main__':
    Uargs = docopt(__doc__, version='0.1')
    main(Uargs)
    

        
