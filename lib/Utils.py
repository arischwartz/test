"""Utility scripts for application"""

# import
## batteries
import os,sys
from pprint import pprint
import re
from itertools import chain
## 3rd party
import pandas as pd


def checkExists(f):
    """
    Args:
    f -- file name
    """
    if not os.path.isfile(f):
        raise IOError('"{}" not found. Did you provide the full PATH?'.format(f))


def parseGenomeList(inFile, filePath=None):
    """Parsing the genome list file
    Args:
    inFile -- genome list file name
    filePath -- abs path to genome sequence files
    Return:
    dict -- {genomeFile : taxonName}
    """
    # parse file as list
    genomeList = []
    with open(inFile, 'rb') as inF:
        for line in inF:
            row = line.rstrip().split('\t')
            
            if len(row) < 2:
                raise ValueError('Need format: "taxonName<tab>fileName";'
                                 'for row: "{}"'.format(row))
            else:
                (taxonName,fileName) = row[:2]
                
            # path to genome file
            if filePath is not None:
                fileName = os.path.join(filePath, fileName)

            # checking for file existence
            checkExists(fileName)
                
            #genomeList[fileName] = taxonName
            genomeList.append((fileName,taxonName))
                
    return genomeList


def describe_builtin(obj):
    """ Describe a builtin function """

    #wi('+Built-in Function: %s' % obj.__name__)
    # Built-in functions cannot be inspected by
    # inspect.getargspec. We have to try and parse
    # the __doc__ attribute of the function.
    docstr = obj.__doc__
    args = ''
    
    if docstr:
        items = docstr.split('\n')
        if items:
            func_descr = items[0]
            s = func_descr.replace(obj.__name__,'')
            idx1 = s.find('(')
            idx2 = s.find(')',idx1)
            if idx1 != -1 and idx2 != -1 and (idx2>idx1+1):
                args = s[idx1+1:idx2]
                #wi('\t-Method Arguments:', args)
                for arg in args:
                    yield arg
                
    if args=='':
        yield None


def parseKeyValueString(x):
    """Parse a string in format: 'key1:value1,key2:value2,keyN:valueN'.
    Values assumed to be numeric.
    Returns a dict.
    """
    x = x.replace(' ','')
    l = re.split('[:,]', x)
    return {k:float(v) for k,v in zip(l[::2],l[1::2])}
        
        

        
class _table(object):
    """Template class for reading in SIPSim tables"""
    
    def __init__(self, df, filename):
        """
        Args:
        df -- pandas dataframe
        filename -- name of table file
        """
        self.df = df
        self.tableFileName = filename
        
        # library as string
        try:
            self.df['library'] = self.df['library'].astype(str)
        except KeyError:
            self.wide2long()
            try:
                self.df['library'] = self.df['library'].astype(str)
            except KeyError:
                raise KeyError('"library" column not found in table: "{}"!'.format(filename))
            

    # reshaping table
    def wide2long(self, sep='__'):
        """Convert table from wide to long format.
        Args:
        sep -- used to split column names
        """
        self.df = pd.melt(self.df, id_vars=['taxon'])        
        new_cols = self.df['variable'].str.split(sep).apply(pd.Series, 1)
        self.df = self.df.join(new_cols)\
                         .rename(columns={'value':'count',0:'library',1:'fractions'})\
                         .drop('variable',1)

        try:
            self.df = self.df\
                          .reindex_axis(['library','fractions','taxon','count'], axis=1)\
                          .sort(['taxon', 'fractions', 'library'])            
        except KeyError:
            pass
        

    def long2wide(self, values, index, columns):
        """Convert table from long to wide format.
        Args:
        values -- values in pivot table
        index -- index in pivot table
        columns -- columns in pivot table
        """
        self.df = pd.pivot_table(self.df, values=values,
                                 index=index, columns=columns)
        self.df.columns =  ['__'.join(x) for x in self.df.columns.tolist()]

            
    # write table
    def to_csv(self, *args, **kwargs):
        self.df.to_csv(*args, **kwargs)

    def write_table(self, *args, **kwargs):
        self.to_csv(*args, **kwargs)

            
    # load from csv
    @classmethod
    def from_csv(cls, filename, **kwargs):
        """Read in table file to a pandas dataframe.
        Args:
        filename -- Table file name
        kwargs -- passed to pandas.read_csv
        """
        df = pd.read_csv(filename, **kwargs)
        return cls(df, filename)

        
    # get/set/iter
    def iter_uniqueColumnValues(self, columnID):
        """General iteration of unique column values.
        """
        try:
            for l in self.df[columnID].unique():
                yield l
        except KeyError:
            raise KeyError('Column "{}" not found'.format(columnID))
            
    def iter_libraries(self):
        """iterating through all unique library IDs
        """
        for libID in self.iter_uniqueColumnValues('library'):
            yield libID
                
    def iter_taxa(self, libID=None):
        """Iterating through all unique taxon names.
        """
        if libID is None:
            for taxon_name in self.iter_uniqueColumnValues('taxon_name'):
                yield taxon_name
        else:
            df_lib = self.df.loc[self.df['library'] == libID]
            for taxon_name in df_lib['taxon_name'].unique():
                yield taxon_name
                
    def iter_taxonRowsInLib(self, libID):
        """Iterate through all subset dataframes containing just 1 taxon.
        Args:
        libID -- str; library ID        
        """
        df_lib = self.df.loc[self.df['library'] == libID]
        for taxon_name in df_lib['taxon_name'].unique():
            yield (taxon_name, df_lib.loc[df_lib['taxon_name'] == taxon_name])
                
    def __repr__(self):
        return self.df.__repr__()
        
