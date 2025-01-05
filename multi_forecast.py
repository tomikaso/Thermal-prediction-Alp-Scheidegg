import json
import numpy as np
import requests
import math
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime

locations = ['Scheidegg', 'Locarno', 'Pany', 'Solothurn', 'Scuol', 'Fiesch']
coordinates = np.array([[47.289, 8.915], [46.175384, 8.793927], [46.927030, 9.771950], [47.233629, 7.497267],
                        [46.798445, 10.299627], [46.404585, 8.13389]])
start_hight = [1200, 1100, 1650, 1440, 2150, 2200]
max_locations = 6
temp700 = np.array([])
temp1000 = np.array([])
temp1500 = np.array([])
temp1900 = np.array([])
temp3000 = np.array([])
temp4200 = np.array([])
temp5600 = np.array([])
dew700 = np.array([])
dew1000 = np.array([])
dew1500 = np.array([])
dew1900 = np.array([])
dew3000 = np.array([])
dew4200 = np.array([])
dew5600 = np.array([])
wind700 = np.array([])
wind1000 = np.array([])
wind1500 = np.array([])
wind1900 = np.array([])
wind3000 = np.array([])
wind4200 = np.array([])
wind5600 = np.array([])
wind_dir700 = np.array([])
wind_dir1000 = np.array([])
wind_dir1500 = np.array([])
wind_dir1900 = np.array([])
wind_dir3000 = np.array([])
wind_dir4200 = np.array([])
wind_dir5600 = np.array([])
radiation = np.array([])
precipitation = np.array([])
cloud_cover_low = np.array([])
cloud_cover_mid = np.array([])
cloud_cover_high = np.array([])
pressure_msl = np.array([])
freezing_level = np.array([])

def get_meteo(lat: float, lng: float):
    status = 'online'
    url = 'https://api.open-meteo.com/v1/forecast?latitude=' + str(lat) + '&longitude=' + str(lng) + '&'
    url = url + 'hourly=temperature_2m,wind_speed_10m,wind_direction_10m,dew_point_2m,pressure_msl,'
    url = url + 'direct_radiation,precipitation,cloud_cover_low,cloud_cover_mid,cloud_cover_high,'
    url = url + 'temperature_900hPa,dew_point_900hPa,wind_speed_900hPa,wind_direction_900hPa,'
    url = url + 'temperature_850hPa,dew_point_850hPa,wind_speed_850hPa,wind_direction_850hPa,'
    url = url + 'temperature_800hPa,dew_point_800hPa,wind_speed_800hPa,wind_direction_800hPa,'
    url = url + 'temperature_700hPa,dew_point_700hPa,wind_speed_700hPa,wind_direction_700hPa,'
    url = url + 'temperature_600hPa,dew_point_600hPa,wind_speed_600hPa,wind_direction_600hPa,'
    url = url + 'temperature_500hPa,dew_point_500hPa,wind_speed_500hPa,wind_direction_500hPa,'
    url = url + 'freezing_level_height&timezone=Europe%2FBerlin&models=icon_seamless'
    print(url)
    try:
        y = requests.get(url)
        response = json.loads(y.text)
        return response
    except requests.exceptions.ConnectTimeout:
        print("ICON API timed out.")
        status = 'offline'
    except requests.exceptions.ConnectionError as conerr:
        print("error in connection to ICON.")
        status = 'offline'
    except requests.exceptions.RequestException as err:
        print("ICON weather request exception.")
        status = 'offline'


# here we start. The loop queries open Meteo with all specified locations. The result is stored in arrays
i = 0
while i < max_locations:
    latitude = coordinates[i, 0]
    longitude = coordinates[i, 1]
    print(locations[i], 'Coordinates: ', coordinates[i], ' latitude: ', latitude, ' long: ', longitude)
    meteo_forcast = get_meteo(latitude, longitude)
    print(meteo_forcast)
    forcast_dump = json.dumps(meteo_forcast)
    forcast_payload = json.loads(forcast_dump)
    hourly = forcast_payload["hourly"]
    time = hourly["time"]
    # temperatures
    temp700 = np.append(temp700, hourly["temperature_2m"])
    temp1000 = np.append(temp1000,hourly["temperature_900hPa"])
    temp1500 = np.append(temp1500,hourly["temperature_850hPa"])
    temp1900 = np.append(temp1900,hourly["temperature_800hPa"])
    temp3000 = np.append(temp3000,hourly["temperature_700hPa"])
    temp4200 = np.append(temp4200,hourly["temperature_600hPa"])
    temp5600 = np.append(temp5600,hourly["temperature_500hPa"])
    # dew-points
    dew700 = np.append(dew700, hourly["dew_point_2m"])
    dew1000 = np.append(dew1000, hourly["dew_point_900hPa"])
    dew1500 = np.append(dew1000, hourly["dew_point_850hPa"])
    dew1900 = np.append(dew1000, hourly["dew_point_800hPa"])
    dew3000 = np.append(dew1000, hourly["dew_point_700hPa"])
    dew4200 = np.append(dew1000, hourly["dew_point_600hPa"])
    dew5600 = np.append(dew1000, hourly["dew_point_500hPa"])

    # wind-speeds
    wind700 = np.append(wind700, hourly["wind_speed_10m"])
    wind1000 = np.append(wind1000, hourly["wind_speed_900hPa"])
    wind1500 = np.append(wind1500, hourly["wind_speed_850hPa"])
    wind1900 = np.append(wind1900, hourly["wind_speed_800hPa"])
    wind3000 = np.append(wind3000, hourly["wind_speed_700hPa"])
    wind4200 = np.append(wind4200, hourly["wind_speed_600hPa"])
    wind5600 = np.append(wind5600, hourly["wind_speed_500hPa"])
    # wind-direction
    wind_dir700 = np.append(wind_dir700, hourly["wind_direction_10m"])
    wind_dir1000 = np.append(wind_dir1000, hourly["wind_direction_900hPa"])
    wind_dir1500 = np.append(wind_dir1500, hourly["wind_direction_850hPa"])
    wind_dir1900 = np.append(wind_dir1900, hourly["wind_direction_800hPa"])
    wind_dir3000 = np.append(wind_dir3000, hourly["wind_direction_700hPa"])
    wind_dir4200 = np.append(wind_dir4200, hourly["wind_direction_600hPa"])
    wind_dir5600 = np.append(wind_dir5600, hourly["wind_direction_500hPa"])
# other values
    radiation = np.append(radiation, hourly["direct_radiation"])
    precipitation = np.append(precipitation, hourly["precipitation"])
    cloud_cover_low = np.append( cloud_cover_low, hourly["cloud_cover_low"])
    cloud_cover_mid = np.append( cloud_cover_mid, hourly["cloud_cover_mid"])
    cloud_cover_high = np.append( cloud_cover_high, hourly["cloud_cover_high"])
    pressure_msl = np.append( pressure_msl, hourly["pressure_msl"])
    freezing_level = np.append( freezing_level, hourly["freezing_level_height"])

    i = i + 1
# convert Lists to arrays with two dimensions
temp700 = temp700.reshape(i, -1)
temp1000 = temp1000.reshape(i, -1)
temp1500 = temp1500.reshape(i, -1)
temp1900 = temp1900.reshape(i, -1)
temp3000 = temp3000.reshape(i, -1)
temp4200 = temp4200.reshape(i, -1)
temp5600 = temp5600.reshape(i, -1)
dew700 = dew700.reshape(i, -1)
dew1000 = dew1000.reshape(i, -1)
dew1500 = dew1500.reshape(i, -1)
dew1900 = dew1900.reshape(i, -1)
dew3000 = dew3000.reshape(i, -1)
dew4200 = dew4200.reshape(i, -1)
dew5600 = dew5600.reshape(i, -1)
wind700 = wind700.reshape(i, -1)
wind1000 = wind1000.reshape(i, -1)
wind1500 = wind1500.reshape(i, -1)
wind1900 = wind1900.reshape(i, -1)
wind3000 = wind3000.reshape(i, -1)
wind4200 = wind4200.reshape(i, -1)
wind5600 = wind5600.reshape(i, -1)
wind_dir700 = wind_dir700.reshape(i, -1)
wind_dir1000 = wind_dir1000.reshape(i, -1)
wind_dir1500 = wind_dir1500.reshape(i, -1)
wind_dir1900 = wind_dir1900.reshape(i, -1)
wind_dir3000 = wind_dir3000.reshape(i, -1)
wind_dir4200 = wind_dir4200.reshape(i, -1)
wind_dir5600 = wind_dir5600.reshape(i, -1)
radiation = radiation.reshape(i, -1)
precipitation = precipitation.reshape(i, -1)
cloud_cover_low = cloud_cover_low.reshape(i, -1)
cloud_cover_mid = cloud_cover_mid.reshape(i, -1)
cloud_cover_high = cloud_cover_high.reshape(i, -1)
pressure_msl = pressure_msl.reshape(i, -1)
freezing_level = freezing_level.reshape(i, -1)

# test purpose
print('nptemp700 - reshaped: ', temp700)
print('nptemp4200 - reshaped: ', temp4200)
print('dewpoint 1000 - reshaped: ', dew1000)

###################
# prepare diagram
###################
w, h = 1140, 680
hmax = 6000
border = 60
tx, ty = 560, 560
t_dist = 150
wind_dot = 6
padding = 5
shape = [(border, border), (w - border, h - border)]

# font
font = ImageFont.truetype("arial.ttf", 18, encoding="unic")
font_sm = ImageFont.truetype("arial.ttf", 14, encoding="unic")
font_el = ImageFont.truetype("arial.ttf", 64, encoding="unic")

#################################
# main loop over all locations  #
#################################

loc = 0
while loc < max_locations:
    # create new image
    img = Image.new("RGB", (w, h), color=(240, 240, 250, 250))
    # create rectangle image
    img1 = ImageDraw.Draw(img) # Emagramm Image
    img1.rectangle(shape, fill="#ffffff", outline="white")