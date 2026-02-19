# datetime libraries
from datetime import datetime
from geopy import Nominatim
import timezonefinder
from pytz import timezone, utc
# matplotlib to help display our star map
import matplotlib.pyplot as plt
# skyfield for star data 
from skyfield.api import Star, load, wgs84
from skyfield.data import hipparcos
from skyfield.projections import build_stereographic_projection
import timezonefinder.timezonefinder

es = load('de421.bsp') # loads respective postion of earth and sun

#loads up stars dataset from the hipparcos catalog
with load.open(hipparcos.URL) as f:
        stars = hipparcos.load_dataframe(f)

#Loading location and makingg instance for geopy and geoname
locator = Nominatim(user_agent='IcyLocator')
tf = timezonefinder.TimezoneFinder()

location = 'Delhi'
time = "2025-09-05 00:00"

location = locator.geocode(location)
lat, lon = location.latitude, location.longitude

localzone = tf.certain_timezone_at(lat=lat, lng=lon)
local = timezone(localzone)

time = datetime.strptime(time, '%Y-%m-%d %H:%M')
localtime = local.localize(time, is_dst=None)
utc_time = localtime.astimezone(utc)
print(utc_time)

#loading up the locations of sun, earth and observer and time of the observation
earth = es['earth']
sun = es['sun']

ts = load.timescale()
to = ts.from_datetime(utc_time)

observer = wgs84.latlon(latitude_degrees=lat, longitude_degrees=lon).at(to)
position = observer.from_altaz(alt_degrees=90, az_degrees=0)

#loading star data

#generating placeholder star
ra, dec, distance = observer.radec()
placeholder_object = Star(ra=ra, dec=dec)

center = earth.at(to).observe(placeholder_object)
projection = build_stereographic_projection(center)

star_positions = earth.at(to).observe(Star.from_dataframe(stars))
stars['x'], stars['y'] = projection(star_positions)


#plotting time
plot_size = 10
max_size_star = 100
min_magnitude = 20 #star brightness magnitude

br_stars = (stars.magnitude <= min_magnitude)
magnitude = stars['magnitude'][br_stars]

fig, ax = plt.subplots(figsize=(11, 7))
border = plt.Circle((0, 0), 1, color='black', fill=True)

ax.add_patch(border)

star_size = max_size_star * 10 ** (magnitude / -2.5) #formula to calculate star brightness 
ax.scatter(stars['x'][br_stars], stars['y'][br_stars], s=star_size, marker='.', color='white', linewidths=0, zorder=2)

horizon = plt.Circle((0, 0), radius=1, transform=ax.transData)
for col in ax.collections:
        col.set_clip_path(horizon)

ax.set_xlim(-1, 1)
ax.set_ylim(-1, 1)
plt.axis('off')

plt.show()

