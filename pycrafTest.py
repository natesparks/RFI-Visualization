import datetime
import numpy as np
from astropy.coordinates import EarthLocation
from astropy import time
from pycraf import satellite

#Az, el, dist calculation code based on satellite module documentation from https://bwinkel.github.io/pycraf/satellite/index.html, retrieved 06/17/2022 


tle_string = """STARLINK-2336
1 47879U 21021V   22165.46324513  .00000070  00000+0  23615-4 0  9992 
2 47879  53.0563 290.8842 0001751  64.8366 295.2804 15.06404960 70539"""

# gbt location
gbt_location = EarthLocation.of_site('gbt')
print(f"gbt_location: {gbt_location}")

# create a SatelliteObserver instance
sat_obs = satellite.SatelliteObserver(gbt_location)

dt = datetime.datetime(2022, 5, 15, 16, 2, 0) #time of day
obstime = time.Time(dt)

satname, sat = satellite.get_sat(tle_string)

az, el, dist = sat_obs.azel_from_sat(sat, obstime)  
print('az, el, dist: {:.1f}, {:.1f}, {:.0f}'.format(az, el, dist))  
