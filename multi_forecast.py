import json
import numpy as np
import requests
import math
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime

# initializing the most important variables
now = datetime.now()
# for the data grid
offset = 0
col = 56
lines = 14
wds = ['Sonntag', 'Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag', 'Heute']

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


def temp_color(tmp):
    color = ['lightgrey', 'palegreen', 'lawngreen', 'limegreen', 'orange']
    return color[min(int(max(0,(tmp-0.55)*10)), 4)]


def lift_color(lft):
    color = ['lightgrey', 'palegreen', 'lawngreen', 'limegreen', 'orange']
    return color[min(int(max(0, lft)), 4)]


def dist_color(dist):
    color = ['whitesmoke', 'palegreen', 'lawngreen', 'limegreen', 'forestgreen']
    return color[min(int(max(0, dist/40 + 0.99)), 4)]


# wind-direction
def wind_direction(grad):
    wd = ['N', 'NO', 'O', 'SO', 'S', 'SW', 'W', 'NW', 'N']
    return wd[int(0.5 + grad / 45)]


def wind_string(grad):
    wd = ['Nordwind', 'NO-Wind', 'Ostwind', 'SO-Wind', 'Südwind', 'SW-Wind', 'Westwind', 'NW-Wind', 'Nordwind']
    return wd[int(0.5 + grad / 45)]


def wind_color(strength, direction):
    if direction > 340 or direction < 120:
        color = ['yellow', 'yellow', 'yellow', 'yellow', 'yellow', 'orange', 'salmon', 'lightcoral', 'tomato', 'red']
    else:
        color = ['palegreen', 'springgreen', 'limegreen', 'lawngreen', 'greenyellow', 'yellow', 'salmon', 'lightcoral', 'tomato', 'red']
    return color[min(int(strength/5), 9)]


def create_lines():
    line = 0
    while line < 7:
        img1.text((10, border + ty - line * 1000 / hmax * ty), str(line * 1000), (20, 20, 20), font=font)
        if line < 4:
            shape_temp = [(border + t_dist * line, h - border), (tx + border, border + t_dist * line)]
            shape_temp2 = [(border, h - border - t_dist * line), (tx + border - t_dist * line, border)]
            img1.line(shape_temp, fill="black", width=0)
            img1.line(shape_temp2, fill="black", width=0)
            img1.text((border + t_dist * line, h - border), str((line - offset) * 10), (20, 20, 20), font=font_sm)
            img1.text((border + 70 + t_dist * line, border), str((line - offset - 3) * 10), (20, 20, 20), font=font_sm)
        line = line + 1


def draw_temp(temp, dewp):
    t0 = temp.pop()
    h0 = temp.pop()
    d0 = dewp.pop()
    dh0 = dewp.pop()
    while len(temp) > 0:
        t1 = temp.pop()
        h1 = temp.pop()
        shape_temp = [(border + t_dist * t0 * 0.1 + h0 / hmax * tx + t_dist * offset, border + ty - h0 / hmax * ty),
                      (border + t_dist * t1 * 0.1 + h1 / hmax * tx + t_dist * offset, border + ty - h1 / hmax * ty)]
        img1.line(shape_temp, fill="red", width=3)
        d1 = dewp.pop()
        dh1 = dewp.pop()
        shape_temp = [(max((border + t_dist * d0 * 0.1 + dh0 / hmax * tx + t_dist * offset), border),
                       border + ty - dh0 / hmax * ty), (
                          max((border + t_dist * d1 * 0.1 + dh1 / hmax * tx + t_dist * offset), border),
                          border + ty - dh1 / hmax * ty)]
        img1.line(shape_temp, fill="blue", width=3)
        t0 = t1
        h0 = h1
        d0 = d1
        dh0 = dh1


def draw_wind(wind):
    while len(wind) > 0:
        direction = wind.pop()
        strength = int(wind.pop())
        hight = wind.pop()
        if strength < 16:
            dot_color = "limegreen"
        elif strength < 30:
            dot_color = "orange"
        else:
            dot_color = "tomato"
        # wind-arrow
        dx = wind_dot * 2.3 * math.sin(math.radians(direction+180)) + tx + border
        dy = - wind_dot * 2.3 * math.cos(math.radians(direction+180)) + ty - hight / hmax * ty + border
        dx1 = wind_dot * 2 * math.sin(math.radians(direction+320)) + tx + border
        dy1 = - wind_dot * 2 * math.cos(math.radians(direction+320)) + ty - hight / hmax * ty + border
        dx2 = wind_dot * 1 * math.sin(math.radians(direction)) + tx + border
        dy2 = - wind_dot * 1 * math.cos(math.radians(direction)) + ty - hight / hmax * ty + border
        dx3 = wind_dot * 2 * math.sin(math.radians(direction+40)) + tx + border
        dy3 = - wind_dot * 2 * math.cos(math.radians(direction+40)) + ty - hight / hmax * ty + border
        img1.polygon ([dx, dy, dx1, dy1, dx2, dy2, dx3, dy3], fill=dot_color)
        img1.text((tx + border + wind_dot * 2, ty - hight / hmax * ty + border - wind_dot*1.5), str(strength), (20, 20, 20), font=font)


def create_thermal_data(index):
    # model-variables
    t1 = 0.6  # at this point thermals begin to be usable
    tm = 1.2  # maximum possible temp
    tf = 5  # temp factor
    distance = 0
    bise = 0
    bise_start = 0
    strong_wind = 0
    foehn = 0
    major_wind_dir, wind_max = 0, 0
    extra_text = ""
    k = -1
    while k < lines - 3:
        box = [(2 * border + tx, border + ty / lines * (k + 1)), (w - border, border + ty / lines * (k + 2))]
        if 2 * int(k / 2) == k:
            img1.rectangle(box, fill="lightgrey", outline="lightgrey")
            # headline
        if k == -1:
            img1.text((2 * border + tx + padding, border + padding + ty / lines * (k + 1)),
                      'Zeit   Wind   Sonne Wolken  Temp  Lift  Basis', (20, 20, 20), font=font)
        else:
            content = time[index + k][11:]
            img1.text((2 * border + tx + padding, border + padding + ty / lines * (k + 1)), content, (20, 20, 20),
                      font=font)
            # wind
            content = str(int(wind1000[loc, index + k])) + wind_direction(wind_dir1000[loc, index + k])
            img1.text((2 * border + tx + padding + col * 1, border + padding + ty / lines * (k + 1)), content,
                      (20, 20, 20), font=font)
            # sun
            sun = int(abs(radiation[loc, index + k] / 8))
            img1.text((2 * border + tx + padding + col * 2, border + padding + ty / lines * (k + 1)), str(sun) + "%",
                      (20, 20, 20), font=font)
            # clouds
            clouds_l = int(abs(cloud_cover_low[loc, index + k] / 12.5))
            clouds_m = int(abs(cloud_cover_mid[loc, index + k] / 12.5))
            clouds_h = int(abs(cloud_cover_high[loc, index + k] / 12.5))
            img1.text((2 * border + tx + padding + col * 3, border + padding + ty / lines * (k + 1)),
                      str(clouds_l) + "-" + str(clouds_m) + "-" + str(clouds_h) , (20, 20, 20), font=font)
            # temp
            tmp = -int(100 * ((temp1900[loc, index + k] - temp1000[loc, index + k]) / 9)) / 100
            img1.text((2 * border + tx + padding + col * 4, border + padding + ty / lines * (k + 1)), str(tmp),
                      (20, 20, 20), font=font)
            # lift
            if wind1500[loc, index + k] <= 20 and wind1900[loc, index + k] <= 25:
                begin_factor = pow(max(0, (temp700[loc, index + k] - temp1000[loc, index + k] - 3)), 0.3)
                lift = int(pow((max(0, ((max(0, (tmp - t1) / (tm - t1)) * tf + sun / 100) - 1)) * 2) * begin_factor, 0.7) * 10) / 10
                content = str(lift)
            else:
                lift = 0
                content = "Wind"
            if lift >= 1:  # real thermals with green background
                distance = int(distance + 4 * lift)
                greenbox = [(2 * border + tx + col * 5, border + ty / lines * (k + 1)),
                            (2 * border + tx + col * 6, border + ty / lines * (k + 2))]
                img1.rectangle(greenbox, fill=lift_color(lift), outline=lift_color(lift))
            img1.text((2 * border + tx + padding + col * 5, border + padding + ty / lines * (k + 1)), content,
                      (20, 20, 20), font=font)
            # strong wind
            if wind1500[loc, index + k] > 65:
                strong_wind = strong_wind + 100
            if wind1500[loc, index + k] > 40:
                strong_wind = strong_wind + 10
            elif wind1500[loc, index + k] > 25:
                strong_wind = strong_wind + 1
            # bise
            if (wind_dir1500[loc, index + k] < 120 or wind_dir1500[loc, index + k] > 340) and wind1500[loc, index + k] > 20:
                bise = bise + 100
            elif (wind_dir1500[loc, index + k] < 120 or wind_dir1500[loc, index + k] > 340) and wind1500[loc, index + k] > 15:
                bise = bise + 10
            elif (wind_dir1500[loc, index + k] < 120 or wind_dir1500[loc, index + k] > 340) and wind1500[loc, index + k] > 5:
                bise = bise + 1
                if bise_start == 0:
                    bise_start = k + 10
            if wind1500[loc, index + k] > wind_max:  # determine direction of the wind-max
                wind_max = wind1500[loc, index + k]
                major_wind_dir = wind_dir1500[loc, index + k]
            # base
            #if pressure_msl_locarno[index + k] - pressure_msl[index + k] > 3:
            #    lift = 0
            #    foehn = max(foehn, pressure_msl_locarno[index + k] - pressure_msl[index + k])
            #    content = str(int(pressure_msl_locarno[index + k] - pressure_msl[index + k] + 0.5)) + "hPa"
            elif cloud_cover_mid[loc, index + k] < 0.1 and cloud_cover_low[loc, index + k] < 0.1:
                content = 'blau'
            elif precipitation[loc, index + k] > 0.5 and temp1000[loc, index + k] >= 1:
                content = 'Regen'
            elif precipitation[loc, index + k] > 0.5 and temp1000[loc, index + k] < 1:
                content = 'Schnee'
            else:
                if lift > 0:
                    base_hight = int(round((125 * (temp1000[loc, index + k] - dew1000[loc, index + k]) + 1000) / 50)) * 50
                    content = str(base_hight)
                else:
                    content = "-"
            img1.text((2 * border + tx + padding + col * 6, border + padding + ty / lines * (k + 1)), content,
                      (20, 20, 20), font=font)
            if lift >= 1:  # root-function gets 1 with a base of 2'000 meters
                distance = int(distance + 4 * lift * pow(max((base_hight-1200), 0), 0.5)/28.2)
            elif lift > 0.5:
                distance = distance + 1
        k = k + 1
    box = [(2 * border + tx, border + ty / lines * (k + 1)), (w - border, border + ty / lines * (k + 3))]
    if bise > 1:
        extra_text = "Bisentendenz"
        if bise_start > 12:
            extra_text = "Bisentendenz ab " + str(int(bise_start)) + "Uhr"
    if strong_wind > 4:
        extra_text = "mässiger " + wind_string(major_wind_dir)
    if bise > 25:
        extra_text = "Bise"
    if foehn > 4:
        extra_text = "Druckdifferenz " + str(int(foehn + 0.5)) + "hPa!"
    if bise > 250:
        extra_text = "zügige Bise"
    if strong_wind > 50:
        extra_text = "kräftiger " + wind_string(major_wind_dir)
    if foehn > 6:
        extra_text = "Druckdifferenz " + str(int(foehn + 0.5)) + "hPa!"
    if strong_wind > 150:
        extra_text = "stürmischer " + wind_string(major_wind_dir)
    if extra_text == '':
        bindung = ''
    else:
        bindung = '- '
    img1.rectangle(box, fill=dist_color(distance), outline=dist_color(distance))
    img1.text((2 * border + tx + padding, border + padding + ty / lines * (k + 1)),
              'Pot. Distanz ' + str(distance) + 'km ' + bindung + extra_text, (20, 20, 20), font=font)
    img1.text((2 * border + tx + padding, border + padding + ty / lines * (k + 2)),
              'Nullgradgrenze auf ' + str(int(freezing_level[loc, index + 5])) + 'm. ', (20, 20, 20), font=font)
    # remember key figures for the overview


def create_forecast(loc, i):
    # initialize variable
    temp = []
    dew_point = []
    wind = []
    # fix scale
    if temp1900[loc, i] > 0:
        offset = 0
    else:
        offset = 1
    # create lists for the emagramm
    temp.append(700)
    temp.append(temp700[loc, i])
    temp.append(1000)
    temp.append(temp1000[loc, i])
    temp.append(1500)
    temp.append(temp1500[loc, i])
    temp.append(1900)
    temp.append(temp1900[loc, i])
    temp.append(3000)
    temp.append(temp3000[loc, i])
    temp.append(4200)
    temp.append(temp4200[loc, i])
    temp.append(5600)
    temp.append(temp5600[loc, i])
    # now the dew_point ;-)
    dew_point.append(700)
    dew_point.append(dew700[loc, i])
    dew_point.append(1000)
    dew_point.append(dew1000[loc, i])
    dew_point.append(1500)
    dew_point.append(dew1500[loc, i])
    dew_point.append(1900)
    dew_point.append(dew1900[loc, i])
    dew_point.append(3000)
    dew_point.append(dew3000[loc, i])
    dew_point.append(4200)
    dew_point.append(dew4200[loc, i])
    dew_point.append(5600)
    dew_point.append(dew5600[loc, i])
    # finally the wind
    wind.append(700)
    wind.append(wind700[loc, i])
    wind.append(wind_dir700[loc, i])
    wind.append(1000)
    wind.append(wind1000[loc, i])
    wind.append(wind_dir1000[loc, i])
    wind.append(1500)
    wind.append(wind1500[loc, i])
    wind.append(wind_dir1500[loc, i])
    wind.append(1900)
    wind.append(wind1900[loc, i])
    wind.append(wind_dir1900[loc, i])
    wind.append(3000)
    wind.append(wind3000[loc, i])
    wind.append(wind_dir3000[loc, i])
    wind.append(4200)
    wind.append(wind4200[loc, i])
    wind.append(wind_dir4200[loc, i])
    wind.append(5600)
    wind.append(wind5600[loc, i])
    wind.append(wind_dir5600[loc, i])
    # create temperature lines
    create_lines()
    # draw the temp
    draw_temp(temp, dew_point)
    # draw the wind
    draw_wind(wind)
    # create thermal data
    create_thermal_data(i - 4)  # 14:00 - 4 = 10:00 Uhr
    # title
    img1.text((10, 25), locations[loc] + "forecast for " + x.strftime("%A, %d/%m/%Y")
              + ", data-source: open-meteo / ICON. Last update: " + now.strftime("%d/%m/%Y %H:%M")
              + " CET", (20, 20, 20), font=font)
    # save the image here
    img.save("forecast" + locations[loc] + str(day) + ".png")
    # remember the weekday for the overview


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
    temp1000 = np.append(temp1000, hourly["temperature_900hPa"])
    temp1500 = np.append(temp1500, hourly["temperature_850hPa"])
    temp1900 = np.append(temp1900, hourly["temperature_800hPa"])
    temp3000 = np.append(temp3000, hourly["temperature_700hPa"])
    temp4200 = np.append(temp4200, hourly["temperature_600hPa"])
    temp5600 = np.append(temp5600, hourly["temperature_500hPa"])
    # dew-points
    dew700 = np.append(dew700, hourly["dew_point_2m"])
    dew1000 = np.append(dew1000, hourly["dew_point_900hPa"])
    dew1500 = np.append(dew1500, hourly["dew_point_850hPa"])
    dew1900 = np.append(dew1900, hourly["dew_point_800hPa"])
    dew3000 = np.append(dew3000, hourly["dew_point_700hPa"])
    dew4200 = np.append(dew4200, hourly["dew_point_600hPa"])
    dew5600 = np.append(dew5600, hourly["dew_point_500hPa"])

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

# create new image
img = Image.new("RGB", (w, h), color=(240, 240, 250, 250))
# create rectangle image
img1 = ImageDraw.Draw(img) # Emagramm Image
img1.rectangle(shape, fill="#ffffff", outline="white")
# font
font = ImageFont.truetype("arial.ttf", 18, encoding="unic")
font_sm = ImageFont.truetype("arial.ttf", 14, encoding="unic")
font_el = ImageFont.truetype("arial.ttf", 64, encoding="unic")

#################################
# main loop over all locations  #
#################################

i = 0
day = 0
loc = 0
while loc < max_locations:  # loops over all locations
    while i < len(time) and day < 5:
        if time[i][11:] == '14:00':
            print(time[i], ' Posi:', i, ' create forecast')
            x = datetime(int(time[i][:4]), int(time[i][5:-9]), int(time[i][8:-6]), 0, 0, 0)
            create_forecast(loc, i)
            img1.rectangle([(0, 0), (w, h)], fill="#ffffff", outline="white")  # clear picture after saving
            day = day + 1
        i = i + 1
    i = 0
    day = 0
    loc = loc + 1
