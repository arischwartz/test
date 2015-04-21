#!/usr/bin/env python

#--- Option parsing ---#
"""
fragments: simulate genome fragments that would be found in a isopycnic gradient

Usage:
  fragments [options] <genomeList>
  fragments -h | --help
  fragments --version

Options:
  <genomeList>  A file listing: taxonName<tab>genomeSeqFileName
  --fp=<fp>     Full path to genomeSeqFiles (if not in genomeList file).
  --rtr=<rtr>   Read template length range (min,max).
                How big can the read template be (part of the DNA fragment 
                that is actually sequenced) 
                [Default: 400,1200]
  --rtl=<rtl>   Read template length distribution (see Description).
                [Default: uniform,250,250]
  --nf=<nf>     Number of fragments to simulate per genome.
                If value ends in 'X', then the number of reads needed
                to obtain that coverage for each genome will be used
                [Default: 10000]
  --fld=<ld>    Fragment length distribution (see Description).
                [Default: skewed-normal,9000,2500,-5]
  --flr=<m>     Fragment length range (min,max). ('None' = no bounds)
                [Default: 4000,None]
  --fr=<fr>     Fasta of forward & reverse primers (if simulating amplicons).
  --np=<np>     Number of genomes to process in parallel.
                [Default: 1]
  --tbl         Write out fragments as a table instead of a pickled python object.
  -h --help     Show this screen.
  --version     Show version.
  --debug       Debug mode

Description:
  Simulate the genomic fragments that would be found in an isopycnic gradient.
  The location and G+C of each simulated fragment is written to a table.

  Genome sequence file names in the <genomeList> file should either include 
  the full path to the file or the path needs to be provided by the '--fp' flag.

  '--rtr' and '--rtl':
    'read template' refers to the template nucleotide molecule from
    which the read originated. Template size is needed to constrain the location and lengths
    of the simulated genome fragments that contain these templates (G+C calculated
    from these fragments).
    Templates could either be an amplicon (e.g. 16S rRNA sequencing)
    or a genomic fragment (e.g. shotgun metagenomics). '--rtl' constrains
    the size of this template. If primers are provided, the in-silico generated amplicons
    are filtered to those that fit in the specified read template range.
    '--rtl' is used to determine the template lengths of shotgun metagenomic reads
    (not contrained by provided primers).

    ** Example for 16S rRNA amplicons **
    Assumning amplicon lengths of 500-650 bp, use: '--rtr 500,650'.
    This will filter out all in-silico amplicons outside of this range.

  ** Selection of scaffold/chromosome **
  For genoems with multiple scaffolds/chromosomes, the scaffold is chosen randomly
  if simulating shotgun fragments and selected randomly from the list of amplicons
  if simulating amplicon fragments.


  ** Distributions ** 
  normal:
    Parameters: location (mean), scale (standard deviation)

  uniform:
    Parameters: low, high
    
  skewed-normal:
    Parameters: location (mean), scale (stardard deviation), shape (skew)
    Example: --fld  skewed-normal,11000,1000,-1000

  truncated-normal:
    Parameters: location, scale, low, high

  ** Output **
    A tab-delim file written to STDOUT.

"""

# import
## batteries
from docopt import docopt
import sys,os
import re
import functools
import itertools
import cPickle as pickle 

## 3rd party
import parmap
import numpy as np

## application libraries
scriptDir = os.path.dirname(__file__)
libDir = os.path.join(scriptDir, '../lib/')
sys.path.append(libDir)

from Genome import Genome
from SimFrags import SimFrags
import Utils



# functions
def by_genome(taxonName, inFile, args):
    """All processing conducted per genome.
    Args:
    inFile -- genome sequence file name
    taxonName -- taxon name of genome
    args -- user-provided args as dict
    Return:
    2d-list -- for each fragment: [taxonName,scaf,start,end,GC]
    """
    # status
    sys.stderr.write('Processing: "{}"\n'.format(taxonName))
    
    # input check
    assert 'scriptDir' in args, '"scriptDir" not in args'
    
    
    # checking for MFEprimer.py executable
    MFEprimerExe = os.path.join(args['scriptDir'], 'MFEprimer.py')
    if not os.path.isfile(MFEprimerExe):
        raise IOError('Cannot find executable "{}"'.format(MFEprimerExe))


    # making genome object
    assert '--fr' in args, '"--fr" must be provided in args'
    genome = Genome(inFile, taxonName, args['--fr'])
    
    
    # sequenced read template location: amplicons
    if genome.get_primerFile() is not None:
        # in-silico PCR
        assert '--rtr' in args, '"--rtr" must be in args'
        genome.callMFEprimer(rtr=args['--rtr'], MFEprimerExe=MFEprimerExe)
    
        # filtering overlapping in-silico amplicons
        genome.filterOverlaps()
        
        
    # simulating fragments    
    simFO = SimFrags(fld=args['--fld'], flr=args['--flr'], rtl=args['--rtl'])
    nFragsMade = 0
    fragList = dict()
    ## if no amplicons
    if genome.nAmplicons == 0:
        pass
    ## if using coverage
    elif args['--nf'].endswith('X') or args['--nf'].endswith('x'):
        coverage = float(args['--nf'].rstrip('xX'))
        fragLenCov = genome.length * coverage
        fragLenTotal = 0
        while 1:
            (scaf,fragStart,fragLen,fragGC) = simFO.simFrag(genome)
            try:
                type(fragList[scaf])
            except KeyError:
                fragList[scaf] = []
                                
            if fragStart == "NA":
                break
            elif fragLenTotal > fragLenCov:
                break
            fragLenTotal += fragLen 

            nFragsMade += 1
            fragList[scaf].append([fragStart, fragLen, fragGC])            
    ## if using fixed number of fragments
    else:            
        for i in xrange(int(args['--nf'])):
            (scaf,fragStart,fragLen,fragGC) = simFO.simFrag(genome)

            try:
                type(fragList[scaf])
            except KeyError:
                fragList[scaf] = []

            if fragStart == "NA":
                break

            nFragsMade += 1
            fragList[scaf].append([fragStart, fragLen, fragGC])
                
    # status
    sys.stderr.write('  Genome name: {}\n'.format(genome.get_taxonName()))                
    sys.stderr.write('  Genome length (bp): {}\n'.format(genome.length))
    if args['--nf']:
        sys.stderr.write('  Number of amplicons: {}\n'.format(genome.nAmplicons))
    sys.stderr.write('  Number of fragments simulated: {}\n'.format(nFragsMade))
                
    return [genome.get_taxonName(), fragList]


def write_fragList(fragList):
    """Writing out fragList as a tab-delim table.
    """
    print '\t'.join(['taxon_name','scaffoldID','fragStart','fragLength','fragGC'])            

    for x in fragList:
        taxon_name = x[0]
        for scaf,v in x[1].items():
            for y in v:                
                print '\t'.join([taxon_name, scaf] + [str(i) for i in y])


def main(args):
    # adding to args
    args['scriptDir'] = libDir

    # list of genome files
    genomeList =  Utils.parseGenomeList(args['<genomeList>'], filePath=args['--fp'])
        
    # analyzing each genome (in parallel)    
    by_genome_part = functools.partial(by_genome, args=args)

    if args['--debug']:
        fragList = itertools.starmap(by_genome_part,genomeList)

        if args['--tbl']:
            write_fragList(fragList)
        else:
            pickle.dump([x for x in fragList], sys.stdout)
            
    else:
        fragList = parmap.starmap(by_genome_part,
                             genomeList,
                             chunksize=1,
                             processes=int(args['--np']))

        if args['--tbl']:
            write_fragList(fragList)
        else:
            pickle.dump(fragList, sys.stdout)
        

    
# main
if __name__ == '__main__':
    args = docopt(__doc__, version='0.1')
    
    sp = re.compile(' *, *')    
    args = {k:sp.split(str(v)) if sp.search(str(v)) else v for k,v in args.items()}
    
    main(args)

        
        
    

        