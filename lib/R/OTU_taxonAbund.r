#!/usr/bin/Rscript

# init
rm(list=ls())

# opt parsing
suppressPackageStartupMessages(library(docopt))

'usage: OTU_taxonAbund.r [options] <OTU> 

options:
  <OTU>          OTU table file.
  -o=<o>         Base name of output file.
                 [Default: taxonAbund]
  -r=<r>         Max abundance rank to plot (0 = all).
                 [Default: 0]
  --width=<w>    Plot width.
                 [Default: 8]
  --height=<h>   Plot height.
                 [Default: 6]
  -h             Help

Description:
  Plot the abundances of taxa in the OTU table. 
' -> doc

opts = docopt(doc)


# packages
pkgs <- c('dplyr', 'tidyr', 'ggplot2')
for(x in pkgs){
  suppressPackageStartupMessages(library(x, character.only=TRUE))
}

# main
## import
tbl = read.delim(opts[['<OTU>']], sep='\t')

## BD min/max/mid
tbl = tbl %>%
  mutate(fraction = gsub('^-inf','negInf',fraction)) %>%
    separate(fraction, into = c('BD_min','BD_max'), sep='-', convert=TRUE, remove=FALSE) %>%
      mutate(BD_min = as.numeric(gsub('negInf','-inf',BD_min)),
             BD_max = as.numeric(gsub('negInf','-inf',BD_max)))

calc_BD_mid = function(BD_min, BD_max){
  if(is.infinite(BD_min)){
    return(BD_max)
  } else
    if(is.infinite(BD_max)){
      return(BD_min)
    } else {
      return((BD_max - BD_min) / 2 + BD_min)
    }
  stop('LOGIC error')
}

tbl$BD_mid = mapply(calc_BD_mid,tbl$BD_min, tbl$BD_max) 


## getting relative abundances (counts)
tbl.s = tbl %>%
  group_by(library, BD_mid) %>%
    summarize(total_sample_count = sum(count))

tbl = inner_join(tbl, tbl.s, c('library'='library','BD_mid'='BD_mid'))
tbl = tbl %>%
  mutate(rel_count = count / total_sample_count)


## filtering / selecting
### selecting abundance ranks of interest
rank.sel = as.numeric(opts[['-r']])
if(rank.sel > 0){
  tbl.s = tbl %>%
    group_by(library, taxon) %>%
      summarize( total_abund = sum(count) ) %>%
        mutate(rank = min_rank(desc(total_abund))) %>%
          filter(rank <= rank.sel)
  tbl = tbl %>%
    filter(taxon %in% tbl.s$taxon)
}



## plotting
BD.GCp0 = 0 * 0.098 + 1.66
BD.GCp100 = 1 * 0.098 + 1.66

## making plots
make_frac_plot = function(tbl, BD.GCp0, BD.GCp100, alpha=1, rel=FALSE){
  p = ggplot(tbl, aes(x=BD_mid, fill=taxon))
  if(rel==TRUE){
    p = p + geom_area(aes(y=rel_count), stat='identity', alpha=0.5, position='stack') +
      labs(y='Relative abundance')
  } else {
    p = p + geom_area(aes(y=count), stat='identity', alpha=0.5, position='dodge') +
      labs(y='Absolute abundance')    
  }  
  p = p + geom_vline(xintercept=c(BD.GCp0, BD.GCp100), linetype='dashed', alpha=alpha) +
      labs(x='Buoyant density') +
        scale_x_continuous(expand=c(0.01,0)) +
          scale_y_continuous(expand=c(0,0.01)) +
            facet_grid(library ~ .) +
              theme_bw() +
                theme(
                  text = element_text(size=16),
                  legend.position = 'none'
                )
  return(p)
}


p.dodge = make_frac_plot(tbl, BD.GCp0, BD.GCp100)
p.fill = make_frac_plot(tbl, BD.GCp0, BD.GCp100, rel=TRUE)


### writing plots
plot.width = as.numeric(opts[['--width']])
plot.height = as.numeric(opts[['--height']])

outFile = paste(c(opts[['-o']], 'abs-abund.pdf'), collapse='_')
ggsave(outFile, plot=p.dodge, width=plot.width, height=plot.height)
message('File written: ', outFile)

outFile = paste(c(opts[['-o']], 'rel-abund.pdf'), collapse='_')
ggsave(outFile, plot=p.fill, width=plot.width, height=plot.height)
message('File written: ', outFile)
