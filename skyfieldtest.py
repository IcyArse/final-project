from skyfield.api import load
import re
from skyfield.api import Star, load
from skyfield.data import hipparcos
from skyfield.api import N, W, E, S, wgs84
import tkinter as tk

root = tk.Tk()
root.title("Coordinates Input")

def submit_coordinates():
    try:
        longitude_cord = 77.062294 
        lateral_cord = 28.982015
        starc = 87937
        x = float(entry_x.get())
        y = float(entry_y.get())
        starcode = int(entry_z.get())
        loc_data(x, y, starcode)
    except ValueError:
        tk.messagebox.showerror("Error", "Please enter valid numerical coordinates.")

def loc_data(x, y, starcode):

      longitude_cord = x
      lateral_cord = y

      if longitude_cord >= 0:
            longitude_cord = longitude_cord * E
      else:
            longitude_cord = longitude_cord * W

      if lateral_cord >= 0:
            lateral_cord = lateral_cord * N
      else:
            lateral_cord = lateral_cord * S

      with load.open(hipparcos.URL) as f:
            df = hipparcos.load_dataframe(f)
      
      try:
            barnards_star = Star.from_dataframe(df.loc[starcode])
      except:
            tk.messagebox.showerror("Error", "Please enter valid star code.")

      # Create a timescale and ask the current time.
      ts = load.timescale()
      t = ts.now()

      # Load the JPL ephemeris DE421 (covers 1900-2050).
      planets = load('de421.bsp')
      earth = planets['earth']

      location = earth + wgs84.latlon(lateral_cord, longitude_cord)

      astrometric = location.at(t).observe(barnards_star)
      ra, dec, distance = astrometric.radec()

      #print(ra)
      #print(dec)
      #print(distance)

      ra = str(ra).split(' ')
      #print(ra)
      for i in range (len(ra)):
            ra[i] = re.findall(r'[-+]?[0-9]*\.?[0-9]+', ra[i])
            ra[i] = float(ra[i].pop())
            
      degRa = (ra[0] + (ra[1] / 60) + (ra[2] / 3600)) * 15
      print(degRa)

      if degRa > 180:
            degRa = -(180 - (degRa - 180)) 

      if 90 > degRa or degRa < -90:
            visiblity = "star slightly/not visible over the horizon"

      else: 
            visiblity = "Star is visible over the horizon"


      new_window = tk.Toplevel(root)
      new_window.title("Star Location Display")

      text = f"""Star Location(Considering sky middle point to be 0deg): \n
Declination(right angle): {dec}        RA(across): {degRa}
Star Visiblity: {visiblity}
      """
    
      label = tk.Label(new_window, text=text, justify='left')
      label.pack(padx=20, pady=20, anchor="w")

frame = tk.Frame(root)
frame.pack(padx=20, pady=20)

label_x = tk.Label(frame, text="Enter X Coordinate:")
label_x.grid(row=0, column=0, padx=5, pady=5, sticky="e")
entry_x = tk.Entry(frame)
entry_x.grid(row=0, column=1, padx=5, pady=5)

label_y = tk.Label(frame, text="Enter Y Coordinate:")
label_y.grid(row=1, column=0, padx=5, pady=5, sticky="e")
entry_y = tk.Entry(frame)
entry_y.grid(row=1, column=1, padx=5, pady=5)

label_z = tk.Label(frame, text="Enter Star HIP Code:")
label_z.grid(row=2, column=0, padx=5, pady=5, sticky="e")
entry_z = tk.Entry(frame)
entry_z.grid(row=2, column=1, padx=5, pady=5)

submit_button = tk.Button(frame, text="Submit", command=submit_coordinates)
submit_button.grid(row=3, columnspan=2, pady=10)

root.mainloop()