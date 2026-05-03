import sys
# datetime libraries
from datetime import datetime
from geopy import Nominatim
import timezonefinder
from pytz import timezone, utc
# matplotlib to help display our star map
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
# skyfield for star data 
from skyfield.api import Star, load, wgs84
from skyfield.data import hipparcos
from skyfield.projections import build_stereographic_projection
import timezonefinder.timezonefinder
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout



class StarrySky(QWidget):
        def __init__(self):
                super().__init__()
                self.setWindowTitle("Star Mapper")

                self.setMinimumSize(400, 300)

                self.location_input = QLineEdit()
                self.location_input.setPlaceholderText("City (example: Delhi,  Melbourne etc.)")


                self.year_input = QLineEdit()
                self.year_input.setPlaceholderText("YYYY(year)")

                self.month_input = QLineEdit()
                self.month_input.setPlaceholderText("MM(Month)")

                self.date_input = QLineEdit()
                self.date_input.setPlaceholderText("DD(Date)")

                self.hour_input = QLineEdit()
                self.hour_input.setPlaceholderText("HH(Hours)")

                self.minute_input = QLineEdit()
                self.minute_input.setPlaceholderText("MM(Minutes)")


                self.status = QLabel("Enter details and click button")
                self.button = QPushButton("Generate Star Map")
                self.button.clicked.connect(self.main_app)

                layout = QVBoxLayout()
                date_layout = QHBoxLayout()
                time_layout = QHBoxLayout()

                date_layout.addWidget(self.year_input)
                date_layout.addWidget(self.month_input)
                date_layout.addWidget(self.date_input)

                time_layout.addWidget(self.hour_input)
                time_layout.addWidget(self.minute_input)

                layout.addWidget(self.location_input)
                layout.addLayout(date_layout)
                layout.addLayout(time_layout)
                layout.addWidget(self.button)
                layout.addWidget(self.status)

                self.setLayout(layout)


        def main_app(self):
                try:
                        es = load('de421.bsp') # loads respective postion of earth and sun

                        #loads up stars dataset from the hipparcos catalog
                        with load.open(hipparcos.URL) as f:
                                stars = hipparcos.load_dataframe(f)

                        #Loading location and makingg instance for geopy and geoname
                        locator = Nominatim(user_agent='IcyLocator')
                        tf = timezonefinder.TimezoneFinder()

                        location = self.location_input.text()
                        time = f"{self.year_input.text()}-{self.month_input.text()}-{self.date_input.text()} {self.hour_input.text()}:{self.minute_input.text()}"
                        
                        #defaults
                        #location = 'Melbourne'
                        #time = "2025-12-31 00:00"

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
                        plot_size = 8
                        max_size_star = 100
                        min_magnitude = 20 #star brightness magnitude

                        br_stars = (stars.magnitude <= min_magnitude)
                        magnitude = stars['magnitude'][br_stars]

                        fig, ax = plt.subplots(figsize=(plot_size*2, plot_size))
                        border = plt.Rectangle((-1, -1), plot_size*2, plot_size, color='black', fill=True)

                        ax.add_patch(border)

                        star_size = max_size_star * 10 ** (magnitude / -2.5) #formula to calculate star brightness 
                        ax.scatter(stars['x'][br_stars], stars['y'][br_stars], s=star_size, marker='.', color='white', linewidths=0, zorder=2)

                        horizon = plt.Rectangle((-1, -1), plot_size*2, plot_size, transform=ax.transData)
                        for col in ax.collections:
                                col.set_clip_path(horizon)

                        ax.set_xlim(-1, 1)
                        ax.set_ylim(-1, 1)
                        plt.axis('off')

                        plt.show()

                        self.status.setText("Star map generated!")
                except Exception as error:
                        self.status.setText(error)

final = QApplication(sys.argv)
Starapp_window = StarrySky()
Starapp_window.show()
sys.exit(final.exec_())



