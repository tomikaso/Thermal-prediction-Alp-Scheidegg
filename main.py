import requests
import json
import math
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime

# initialize variable
temp = []
dew_point = []
wind = []
# variables for the overview
ov_days = []
ov_potential = []
ov_remark = []
now = datetime.now()
# for the data grid
col = 56
lines = 14
wds = ['Sonntag', 'Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag', 'Heute']


# get the data
def get_meteo():
    status = 'online'
    try:
        y = requests.get('https://api.open-meteo.com/v1/forecast?latitude=47.289&longitude=8.915&'  # Wald ZH
                         'hourly=temperature_2m,wind_speed_10m,wind_direction_10m,dew_point_2m,pressure_msl,'
                         'direct_radiation,precipitation,cloud_cover_low,cloud_cover_mid,cloud_cover_high,'
                         'temperature_900hPa,dew_point_900hPa,wind_speed_900hPa,wind_direction_900hPa,'
                         'temperature_850hPa,dew_point_850hPa,wind_speed_850hPa,wind_direction_850hPa,'
                         'temperature_800hPa,dew_point_800hPa,wind_speed_800hPa,wind_direction_800hPa,'
                         'temperature_700hPa,dew_point_700hPa,wind_speed_700hPa,wind_direction_700hPa,'
                         'temperature_600hPa,dew_point_600hPa,wind_speed_600hPa,wind_direction_600hPa,'
                         'temperature_500hPa,dew_point_500hPa,wind_speed_500hPa,wind_direction_500hPa,'
                         'freezing_level_height&timezone=Europe%2FBerlin&models=icon_seamless', timeout=10)
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


def get_meteo_locarno():
    status = 'online'
    try:
        z = requests.get('https://api.open-meteo.com/v1/forecast?latitude=46.16&longitude=8.8&'  # Locarno
                         'hourly=pressure_msl&timezone=Europe%2FBerlin&models=icon_seamless', timeout=10)
        response_locarno = json.loads(z.text)

        return response_locarno
    except requests.exceptions.ConnectTimeout:
        print("ICON API timed out.")
        status = 'offline'


# function to draw the temp
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


def calc_arrow(x, y, direction):
    dot = 4
    dx = dot * 2.3 * math.sin(math.radians(direction + 180)) + x
    dy = - dot * 2.3 * math.cos(math.radians(direction + 180)) + y
    dx1 = dot * 2 * math.sin(math.radians(direction + 320)) + x
    dy1 = - dot * 2 * math.cos(math.radians(direction + 320)) + y
    dx2 = dot * 1 * math.sin(math.radians(direction)) + x
    dy2 = - dot * 1 * math.cos(math.radians(direction)) + y
    dx3 = dot * 2 * math.sin(math.radians(direction + 40)) + x
    dy3 = - dot * 2 * math.cos(math.radians(direction + 40)) + y
    return dx, dy, dx1, dy1, dx2, dy2, dx3, dy3


# draw wind
def draw_wind(wind):
    while len(wind) > 0:
        direction = wind.pop()
        strength = int(wind.pop())
        hight = wind.pop()
        if strength < 16 and 180 < direction < 320:
            dot_color = "limegreen"
        elif strength < 30:
            dot_color = "orange"
        else:
            dot_color = "tomato"
        # wind-arrow
        dx = wind_dot * 2.3 * math.sin(math.radians(direction + 180)) + tx + border
        dy = - wind_dot * 2.3 * math.cos(math.radians(direction + 180)) + ty - hight / hmax * ty + border
        dx1 = wind_dot * 2 * math.sin(math.radians(direction + 320)) + tx + border
        dy1 = - wind_dot * 2 * math.cos(math.radians(direction + 320)) + ty - hight / hmax * ty + border
        dx2 = wind_dot * 1 * math.sin(math.radians(direction)) + tx + border
        dy2 = - wind_dot * 1 * math.cos(math.radians(direction)) + ty - hight / hmax * ty + border
        dx3 = wind_dot * 2 * math.sin(math.radians(direction + 40)) + tx + border
        dy3 = - wind_dot * 2 * math.cos(math.radians(direction + 40)) + ty - hight / hmax * ty + border
        img1.polygon([dx, dy, dx1, dy1, dx2, dy2, dx3, dy3], fill=dot_color)
        img1.text((tx + border + wind_dot * 2, ty - hight / hmax * ty + border - wind_dot * 1.5), str(strength),
                  (20, 20, 20), font=font)


# creating new Image object
def create_lines():
    i = 0
    while i < 7:
        img1.text((10, border + ty - i * 1000 / hmax * ty), str(i * 1000), (20, 20, 20), font=font)
        if i < 4:
            shape_temp = [(border + t_dist * i, h - border), (tx + border, border + t_dist * i)]
            shape_temp2 = [(border, h - border - t_dist * i), ((w-tx) + border - t_dist * i, border)]
            img1.line(shape_temp, fill="black", width=0)
            img1.line(shape_temp2, fill="black", width=0)
            img1.text((border + t_dist * i, h - border), str((i - offset) * 10), (20, 20, 20), font=font_sm)
            img1.text((border + 70 + t_dist * i, border), str((i - offset - 3) * 10), (20, 20, 20), font=font_sm)
        i = i + 1


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
        color = ['palegreen', 'springgreen', 'limegreen', 'lawngreen', 'greenyellow', 'yellow', 'salmon', 'lightcoral',
                 'tomato', 'red']
    return color[min(int(strength / 5), 9)]


def cloud_color(octas, rain):
    if rain > 0.5:
        color = ['white', 'powderblue', 'lightblue', 'cornflowerblue', 'royalblue', 'blue', 'darkblue', 'navy', 'navy']
    else:
        color = ['white', 'whitesmoke', 'gainsboro', 'lightgrey', 'lightgray', 'silver', 'darkgrey', 'darkgray', 'grey',
                 'gray']
    return color[min(int(octas), 8)]


def temp_color(tmp):
    color = ['lightgrey', 'palegreen', 'lawngreen', 'limegreen', 'orange']
    return color[min(int(max(0, (tmp - 0.55) * 10)), 4)]


def lift_color(lft):
    color = ['lightgrey', 'palegreen', 'lawngreen', 'limegreen', 'orange']
    return color[min(int(max(0, lft)), 4)]


def dist_color(dist):
    color = ['whitesmoke', 'palegreen', 'lawngreen', 'limegreen', 'forestgreen']
    return color[min(int(max(0, dist / 40 + 0.99)), 4)]


# create thermal data lines
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
            content = str(int(wind1000[index + k])) + wind_direction(wind_dir1000[index + k])
            img1.text((2 * border + tx + padding + col * 1, border + padding + ty / lines * (k + 1)), content,
                      (20, 20, 20), font=font)
            # sun
            sun = int(abs(radiation[index + k] / 8))
            img1.text((2 * border + tx + padding + col * 2, border + padding + ty / lines * (k + 1)), str(sun) + "%",
                      (20, 20, 20), font=font)
            # clouds
            clouds_l = int(abs(cloud_cover_low[index + k] / 12.5))
            clouds_m = int(abs(cloud_cover_mid[index + k] / 12.5))
            clouds_h = int(abs(cloud_cover_high[index + k] / 12.5))
            img1.text((2 * border + tx + padding + col * 3, border + padding + ty / lines * (k + 1)),
                      str(clouds_l) + "-" + str(clouds_m) + "-" + str(clouds_h), (20, 20, 20), font=font)
            # temp
            tmp = -int(100 * ((temp1900[index + k] - temp1000[index + k]) / 9)) / 100
            img1.text((2 * border + tx + padding + col * 4, border + padding + ty / lines * (k + 1)), str(tmp),
                      (20, 20, 20), font=font)
            # lift
            if wind1500[index + k] <= 20 and wind1900[index + k] <= 25:
                begin_factor = pow(max(0, (temp700[index + k] - temp1000[index + k] - 3)), 0.3)
                lift = int(pow((max(0, ((max(0, (tmp - t1) / (tm - t1)) * tf + sun / 100) - 1)) * 2) * begin_factor,
                               0.7) * 10) / 10
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
            if wind1500[index + k] > 65:
                strong_wind = strong_wind + 100
            if wind1500[index + k] > 40:
                strong_wind = strong_wind + 10
            elif wind1500[index + k] > 25:
                strong_wind = strong_wind + 1
            # bise
            if (wind_dir1500[index + k] < 120 or wind_dir1500[index + k] > 340) and wind1500[index + k] > 20:
                bise = bise + 100
            elif (wind_dir1500[index + k] < 120 or wind_dir1500[index + k] > 340) and wind1500[index + k] > 15:
                bise = bise + 10
            elif (wind_dir1500[index + k] < 120 or wind_dir1500[index + k] > 340) and wind1500[index + k] > 5:
                bise = bise + 1
                if bise_start == 0:
                    bise_start = k + 10
            if wind1500[index + k] > wind_max:  # determine direction of the wind-max
                wind_max = wind1500[index + k]
                major_wind_dir = wind_dir1500[index + k]
            # base
            if pressure_msl_locarno[index + k] - pressure_msl[index + k] > 3:
                lift = 0
                foehn = max(foehn, pressure_msl_locarno[index + k] - pressure_msl[index + k])
                content = str(int(pressure_msl_locarno[index + k] - pressure_msl[index + k] + 0.5)) + "hPa"
            elif cloud_cover_mid[index + k] < 0.1 and cloud_cover_low[index + k] < 0.1:
                content = 'blau'
            elif precipitation[index + k] > 0.5 and temp1000[index + k] >= 1:
                content = 'Regen'
            elif precipitation[index + k] > 0.5 and temp1000[index + k] < 1:
                content = 'Schnee'
            else:
                if lift > 0:
                    base_hight = int(round((125 * (temp1000[index + k] - dew1000[index + k]) + 1000) / 50)) * 50
                    content = str(base_hight)
                else:
                    content = "-"
            img1.text((2 * border + tx + padding + col * 6, border + padding + ty / lines * (k + 1)), content,
                      (20, 20, 20), font=font)
            if lift >= 1:  # root-function gets 1 with a base of 2'000 meters
                distance = int(distance + 4 * lift * pow(max((base_hight - 1200), 0), 0.5) / 28.2)
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
              'Nullgradgrenze auf ' + str(int(freezing_level[index + 5])) + 'm. ', (20, 20, 20), font=font)
    # remember key figures for the overview
    ov_potential.append(distance)
    ov_remark.append(extra_text)


# functions for the wind-diagram
def wind_diagram(index):
    pad = 4  # extra-Padding
    c = 0
    while c < 17:
        # headline
        img1.text((2 * border + c * col, border + pad), str(c + 6) + ":00", (20, 20, 20), font=font)
        # wind
        box = [(2 * border + c * col - pad, border - pad + 2 * ty / lines),
               (2 * border + (c + 1) * col - pad, border - pad + 2.8 * ty / lines)]
        img1.rectangle(box, fill=wind_color(wind4200[index + c], wind_dir4200[index + c]), outline='white')
        img1.text((2 * border + c * col + 6 * pad, border + 2 * ty / lines), str(int(wind4200[index + c])),
                  (20, 20, 20), font=font)
        img1.polygon(
            calc_arrow(2 * border + c * col + 2 * pad, border + 3 * pad + 2 * ty / lines, wind_dir4200[index + c]),
            fill='dimgrey')

        box = [(2 * border + c * col - pad, border - pad + 3 * ty / lines),
               (2 * border + (c + 1) * col - pad, border - pad + 3.8 * ty / lines)]
        img1.rectangle(box, fill=wind_color(wind3000[index + c], wind_dir3000[index + c]), outline='white')
        img1.text((2 * border + c * col + 6 * pad, border + 3 * ty / lines), str(int(wind3000[index + c])),
                  (20, 20, 20), font=font)
        img1.polygon(
            calc_arrow(2 * border + c * col + 2 * pad, border + 3 * pad + 3 * ty / lines, wind_dir3000[index + c]),
            fill='dimgrey')

        box = [(2 * border + c * col - pad, border - pad + 4 * ty / lines),
               (2 * border + (c + 1) * col - pad, border - pad + 4.8 * ty / lines)]
        img1.rectangle(box, fill=wind_color(wind1900[index + c], wind_dir1900[index + c]), outline='white')
        img1.text((2 * border + c * col + 6 * pad, border + 4 * ty / lines), str(int(wind1900[index + c])),
                  (20, 20, 20), font=font)
        img1.polygon(
            calc_arrow(2 * border + c * col + 2 * pad, border + 3 * pad + 4 * ty / lines, wind_dir1900[index + c]),
            fill='dimgrey')

        box = [(2 * border + c * col - pad, border - pad + 5 * ty / lines),
               (2 * border + (c + 1) * col - pad, border - pad + 5.8 * ty / lines)]
        img1.rectangle(box, fill=wind_color(wind1500[index + c], wind_dir1500[index + c]), outline='white')
        img1.text((2 * border + c * col + 6 * pad, border + 5 * ty / lines), str(int(wind1500[index + c])),
                  (20, 20, 20), font=font)
        img1.polygon(
            calc_arrow(2 * border + c * col + 2 * pad, border + 3 * pad + 5 * ty / lines, wind_dir1500[index + c]),
            fill='dimgrey')

        box = [(2 * border + c * col - pad, border - pad + 6 * ty / lines),
               (2 * border + (c + 1) * col - pad, border - pad + 6.8 * ty / lines)]
        img1.rectangle(box, fill=wind_color(wind1000[index + c], wind_dir1000[index + c]), outline='white')
        img1.text((2 * border + c * col + 6 * pad, border + 6 * ty / lines), str(int(wind1000[index + c])),
                  (20, 20, 20), font=font)
        img1.polygon(
            calc_arrow(2 * border + c * col + 2 * pad, border + 3 * pad + 6 * ty / lines, wind_dir1000[index + c]),
            fill='dimgrey')
        # clouds
        clouds_l = int(abs(cloud_cover_low[index + c] / 12.5))
        clouds_m = int(abs(cloud_cover_mid[index + c] / 12.5))
        clouds_h = int(abs(cloud_cover_high[index + c] / 12.5))
        rain = precipitation[index + c]
        # clouds_high
        box = [(2 * border + c * col - pad, border - pad + 8 * ty / lines),
               (2 * border + (c + 1) * col - pad, border - pad + 8.8 * ty / lines)]
        img1.rectangle(box, fill=cloud_color(clouds_h / 2, rain), outline='white')  # less color for high clouds
        img1.text((2 * border + c * col, border + 8 * ty / lines), "  " + str(clouds_h), (20, 20, 20), font=font)
        # clouds_mid
        box = [(2 * border + c * col - pad, border - pad + 9 * ty / lines),
               (2 * border + (c + 1) * col - pad, border - pad + 9.8 * ty / lines)]
        img1.rectangle(box, fill=cloud_color(clouds_m, rain), outline='white')
        img1.text((2 * border + c * col, border + 9 * ty / lines), "  " + str(clouds_m), (20, 20, 20), font=font)
        # clouds_low
        box = [(2 * border + c * col - pad, border - pad + 10 * ty / lines),
               (2 * border + (c + 1) * col - pad, border - pad + 10.8 * ty / lines)]
        img1.rectangle(box, fill=cloud_color(clouds_l, rain), outline='white')
        img1.text((2 * border + c * col, border + 10 * ty / lines), "  " + str(clouds_l), (20, 20, 20), font=font)
        # Temp until 3'000 meter
        grad3000 = -int(100 * ((temp3000[index + c] - temp1900[index + c]) / 11)) / 100
        box = [(2 * border + c * col - pad, border - pad + 12 * ty / lines),
               (2 * border + (c + 1) * col - pad, border - pad + 12.8 * ty / lines)]
        img1.rectangle(box, fill=temp_color(grad3000), outline='white')
        img1.text((2 * border + c * col, border + 12 * ty / lines), str(grad3000), (20, 20, 20), font=font)
        # Temp until 1'900 meter
        grad1900 = -int(100 * ((temp1900[index + c] - temp1000[index + c]) / 9)) / 100
        box = [(2 * border + c * col - pad, border - pad + 13 * ty / lines),
               (2 * border + (c + 1) * col - pad, border - pad + 13.8 * ty / lines)]
        img1.rectangle(box, fill=temp_color(grad1900), outline='white')
        img1.text((2 * border + c * col, border + 13 * ty / lines), str(grad1900), (20, 20, 20), font=font)
        # Süd-Nord-Überdruck
        sn_diff = pressure_msl_locarno[index + c] - pressure_msl[index + c]
        box = [(2 * border + c * col - pad, border - pad + 14 * ty / lines),
               (2 * border + (c + 1) * col - pad, border - pad + 14.8 * ty / lines)]
        img1.rectangle(box, fill=wind_color(max(0, (8 * sn_diff)), 270), outline='white')
        img1.text((2 * border + c * col, border + 14 * ty / lines), str(int(sn_diff + 0.5)) + "hPa", (20, 20, 20),
                  font=font)
        c = c + 1
    z = 0
    categories = ["Wind (km/h)", "4200", "3000", "1900", "1500", "1000", "Wolken (Achtel)", "hoch", "mittel", "tief"
        , "Temp (°C/100m)", "3000", "1900", "S/N", ""]
    while z < 14:
        img1.text((border, border + (z + 1) * ty / lines), categories.pop(0), (20, 20, 20), font=font)
        z = z + 1


# here we start
meteo_forcast = get_meteo()
print(meteo_forcast)
forcast_dump = json.dumps(meteo_forcast)
forcast_payload = json.loads(forcast_dump)
hourly = forcast_payload["hourly"]
time = hourly["time"]
# temperatures
temp700 = hourly["temperature_2m"]
temp1000 = hourly["temperature_900hPa"]
temp1500 = hourly["temperature_850hPa"]
temp1900 = hourly["temperature_800hPa"]
temp3000 = hourly["temperature_700hPa"]
temp4200 = hourly["temperature_600hPa"]
temp5600 = hourly["temperature_500hPa"]
# dew-points
dew700 = hourly["dew_point_2m"]
dew1000 = hourly["dew_point_900hPa"]
dew1500 = hourly["dew_point_850hPa"]
dew1900 = hourly["dew_point_800hPa"]
dew3000 = hourly["dew_point_700hPa"]
dew4200 = hourly["dew_point_600hPa"]
dew5600 = hourly["dew_point_500hPa"]
# wind-speeds
wind700 = hourly["wind_speed_10m"]
wind1000 = hourly["wind_speed_900hPa"]
wind1500 = hourly["wind_speed_850hPa"]
wind1900 = hourly["wind_speed_800hPa"]
wind3000 = hourly["wind_speed_700hPa"]
wind4200 = hourly["wind_speed_600hPa"]
wind5600 = hourly["wind_speed_500hPa"]
# wind-direction
wind_dir700 = hourly["wind_direction_10m"]
wind_dir1000 = hourly["wind_direction_900hPa"]
wind_dir1500 = hourly["wind_direction_850hPa"]
wind_dir1900 = hourly["wind_direction_800hPa"]
wind_dir3000 = hourly["wind_direction_700hPa"]
wind_dir4200 = hourly["wind_direction_600hPa"]
wind_dir5600 = hourly["wind_direction_500hPa"]
# other values
radiation = hourly["direct_radiation"]
precipitation = hourly["precipitation"]
cloud_cover_low = hourly["cloud_cover_low"]
cloud_cover_mid = hourly["cloud_cover_mid"]
cloud_cover_high = hourly["cloud_cover_high"]
pressure_msl = hourly["pressure_msl"]
freezing_level = hourly["freezing_level_height"]
# get Locarno Pressure-Reference
meteo_forcast_locarno = get_meteo_locarno()
print(meteo_forcast_locarno)
forcast_dump_locarno = json.dumps(meteo_forcast_locarno)
forcast_payload_locarno = json.loads(forcast_dump_locarno)
hourly_locarno = forcast_payload_locarno["hourly"]
pressure_msl_locarno = hourly_locarno["pressure_msl"]

###################
# prepare diagram
###################
w, h = 1140, 680
hmax = 6000
border = 60
tx, ty = 500, 560 # position of data-box
t_dist = 150
wind_dot = 6
padding = 5
shape = [(border, border), (w - border, h - border)]

# font
font = ImageFont.truetype("arial.ttf", 18, encoding="unic")
font_sm = ImageFont.truetype("arial.ttf", 14, encoding="unic")
font_el = ImageFont.truetype("arial.ttf", 64, encoding="unic")
# font = ImageFont.load_default(size=20)
# font_sm = ImageFont.load_default(size=10)

# create new image
img = Image.new("RGB", (w, h), color=(240, 240, 250, 250))
# create rectangle image
img1 = ImageDraw.Draw(img)  # Emagramm Image
img1.rectangle(shape, fill="#ffffff", outline="white")

# get the data ready
print(len(time))
i = 0
j = 0
while i < len(time) and j < 5:
    if time[i][11:] == '14:00':
        print(time[i], ' Posi:', i, ' create forecast')
        x = datetime(int(time[i][:4]), int(time[i][5:-9]), int(time[i][8:-6]), 0, 0, 0)
        # fix scale
        if temp1900[i] > 0:
            offset = 0
        else:
            offset = 1
        # create lists for the emagramm
        temp.append(700)
        temp.append(temp700[i])
        temp.append(1000)
        temp.append(temp1000[i])
        temp.append(1500)
        temp.append(temp1500[i])
        temp.append(1900)
        temp.append(temp1900[i])
        temp.append(3000)
        temp.append(temp3000[i])
        temp.append(4200)
        temp.append(temp4200[i])
        temp.append(5600)
        temp.append(temp5600[i])
        # now the dew_point ;-)
        dew_point.append(700)
        dew_point.append(dew700[i])
        dew_point.append(1000)
        dew_point.append(dew1000[i])
        dew_point.append(1500)
        dew_point.append(dew1500[i])
        dew_point.append(1900)
        dew_point.append(dew1900[i])
        dew_point.append(3000)
        dew_point.append(dew3000[i])
        dew_point.append(4200)
        dew_point.append(dew4200[i])
        dew_point.append(5600)
        dew_point.append(dew5600[i])
        # finally the wind
        wind.append(700)
        wind.append(wind700[i])
        wind.append(wind_dir700[i])
        wind.append(1000)
        wind.append(wind1000[i])
        wind.append(wind_dir1000[i])
        wind.append(1500)
        wind.append(wind1500[i])
        wind.append(wind_dir1500[i])
        wind.append(1900)
        wind.append(wind1900[i])
        wind.append(wind_dir1900[i])
        wind.append(3000)
        wind.append(wind3000[i])
        wind.append(wind_dir3000[i])
        wind.append(4200)
        wind.append(wind4200[i])
        wind.append(wind_dir4200[i])
        wind.append(5600)
        wind.append(wind5600[i])
        wind.append(wind_dir5600[i])
        # create temperature lines
        create_lines()
        # draw the temp
        draw_temp(temp, dew_point)
        # draw the wind
        draw_wind(wind)
        # create thermal data
        create_thermal_data(i - 4)  # 14:00 - 4 = 10:00 Uhr
        # title
        img1.text((10, 25), "Alp Scheidegg forecast for " + x.strftime("%A, %d/%m/%Y")
                  + ", data-source: open-meteo / ICON. Last update: " + now.strftime("%d/%m/%Y %H:%M")
                  + " CET", (20, 20, 20), font=font)
        # save the image here
        img.save("forecast" + str(j) + ".png")
        # remember the weekday for the overview
        if j == 0:
            ov_days.append("7")
        else:
            ov_days.append(x.strftime("%w"))
        # the second image for the wind
        img = Image.new("RGB", (w, h), color=(250, 250, 250, 250))
        img1 = ImageDraw.Draw(img)
        img1.rectangle(shape, fill="#ffffff", outline="white")
        wind_diagram(i - 8)  # 14:00 - 8 = 06:00Uhr
        img1.text((10, 25), "Alp Scheidegg forecast for " + x.strftime("%A, %d/%m/%Y")
                  + ", data-source: open-meteo" + " / ICON. Last update: " + now.strftime("%d/%m/%Y %H:%M")
                  + " CET", (20, 20, 20), font=font)
        img.save("meteo_wind" + str(j) + ".png")

        # reset variables
        j = j + 1
        temp.clear()
        dew_point.clear()
        wind.clear()
        # create next image
        img = Image.new("RGB", (w, h), color=(250, 250, 250, 250))
        img1 = ImageDraw.Draw(img)
        img1.rectangle(shape, fill="#ffffff", outline="white")
    i = i + 1
print("Create overview")
# create new image
h = 180
img = Image.new("RGB", (w, h), color=(240, 240, 250, 250))
# create rectangle image
img1 = ImageDraw.Draw(img)  # overview image
i = 0
days = 5
while i < days:
    box = [(i * w / days, 0), ((i + 1) * w / days, h)]
    distance = ov_potential.pop(0)
    img1.rectangle(box, fill=dist_color(distance), outline=dist_color(distance))
    img1.text((i * w / days + 3 * padding, 3 * padding), wds[int(ov_days.pop(0))], (20, 20, 20), font=font)
    img1.text(((i + 0.3) * w / days, 0.3 * h), str(distance), (20, 20, 20), font=font_el)
    img1.text((i * w / days + 3 * padding, h - 36), ov_remark.pop(0), (20, 20, 20), font=font)
    i = i + 1
img.save("thermal_overview.png")
print("Hoi Thomas")
