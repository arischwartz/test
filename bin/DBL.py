#!/usr/bin/env python

#--- Option parsing ---#
"""
DBL: include diffusion boundary layer contamination into G+C variance

Usage:
  fragments [options] <fragment_kde>
  fragments -h | --help
  fragments --version

Options:
  <fragment_kde>    Output from the fragment_kde subcommand.
                    ('-' if input from STDIN) 
  -T=<T>            Ultracentrifugation run temperature (kelvin).
                    [default: 293.15]
  --tube-diam=<td>  
  --tube-height=<th>
  --r_min=<rm>
  --r_max=<rx>
  --r_angle=<ra>
  --frac-abs=<fa>  
  -n=<n>            Number of Monte Carlo replicates to estimate
                    G+C error due to DBL. 
                    [default: 100000]
  --bw=<bw>         The bandwidth scalar or function passed to
                    scipy.stats.gaussian_kde().
  --np=<np>         Number of parallel processes.
                    [default: 1]
  -h --help         Show this screen.
  --version         Show version.
  --debug           Debug mode (no parallel processes)

Description:
  In isopycnic centrifugation, the gradient forms perpendicular to the
  axis of rotation. Thus, in a fixed angle or vertical rotor, the gradient 
  is oriented no down the length of the cfg tube, but at an angle. 
  The gradient formed during ultracentrifugation will rotate once the tube
  is placed in a vertical orientation for fractionation.
  For more info, see: 
      Fisher WD, Cline GB, Anderson NG. (1964). 
      Density gradient centrifugation in angle-head rotors. 
      Analytical Biochemistry 9: 477–482.

  This difference in gradient orientation between centrifugation and 
  fractionation may result in gradient 'smearing' if DNA binds to the tube
  wall during centrifugation and then diffuses back into solution during the 
  period between centrigution and fractionation. This diffusive boundary
  layer (DBL) can introduce 'light' DNA into 'heavy' fractions and vice versa.
  For instance:
    In a fixed angle rotor, particles with a buoyant density of 1.7 (at
    equilibrium) will be collected in a band spanning a couple of centimeters
    of the tube height.
           /  /
    top-->/  /
         /| /     <-- cfg tube during ultracentrifugation 
        / |/
       (  /<--radient band bottom (BD of 1.7)
        ^^

      |  |
      |  |
      |--| <--gradient band (BD of 1.7) during fractionation
      \__/

  Based on information on the rotor and cfg run conditions, this script
  models the gradient 'smearing' that would result from a diffusive boundary
  layer (contaminating DNA diffusing back into the gradient from the tube wall).  

  The error in 'true' G+C values caused by the DBL is estimated
  by Monte Carlo simulation. 

  Output
  ------
  A pickled python object {taxon_name:buoyant_density_kde} is
  written to STDOUT.
"""

# import
## batteries
from docopt import docopt
import sys,os
## application libraries
scriptDir = os.path.dirname(__file__)
libDir = os.path.join(scriptDir, '../lib/')
sys.path.append(libDir)

import DBL

        
# main
if __name__ == '__main__':
    args = docopt(__doc__, version='0.1')            
    args['-n'] = float(args['-n'])
    DBL.main(args)
    

        