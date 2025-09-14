import ftplib
import math
from datetime import datetime

import json
import requests
from PIL import Image, ImageDraw, ImageFont
from thermal_model import thermal_model
import constants

# initialize variable
model_html_string = []
temp = []
dew_point = []
wind = []
# varibles for the overview
ov_days = []
ov_potential = []
ov_remark = []
soar_potential = []
now = datetime.now()
# for the data grid
col = 60
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
                         'weather_code,freezing_level_height&timezone=Europe%2FBerlin&models=icon_seamless', timeout=10)
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
        print("ICON API Locarno timed out.")
        status = 'offline'


def get_meta_data(url):
    try:
        y = requests.get(url)
        response = json.loads(y.text)
        ts = int(response['last_run_availability_time'])
        return datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M') + ' CET'
    except requests.exceptions.ConnectTimeout:
        print("ICON API timed out.")


def thermal_visualisation(temp):
    data = [(-100, 'Inversion', 'thistle'), (-0.1, 'isotherm', 'PowderBlue'), (0.1, 'sehr stabil', 'paleturquoise'),
            (0.3, 'stabil', 'lightcyan'), (0.5, 'eher stabil', 'azure'), (0.6, 'etwas labil', 'palegreen'),
            (0.7, 'labil', 'greenyellow'), (0.8, 'sehr labil', 'chartreuse'), (1, 'hyperlabil', 'yellowgreen')]
    i = 0
    cont = 'unknown'
    color = 'white'
    while i < 9:
        if temp >= data[i][0]:
            cont = data[i][1]
            color = data[i][2]
        i = i + 1
    return cont, color


# function to draw the temp
def draw_temp(temp, dewp):
    t0 = temp.pop()
    h0 = temp.pop()
    d0 = dewp.pop()
    dh0 = dewp.pop()
    hd = hmax - hmin
    while len(temp) > 0:
        t1 = temp.pop()
        h1 = temp.pop()
        shape_temp_box = [(border, border + (hmax - h0) / hd * ty), (border + tx, border + (hmax - h1) / hd * ty)]
        tmp = -int(100 * ((t0 - t1) / (h0 - h1)*100)) / 100
        img1.rectangle(shape_temp_box, fill=thermal_visualisation(tmp)[1], outline=thermal_visualisation(tmp)[1])
        img1.text((2 * border + t_dist * t0 * 0.1 + h0 / hmax * tx + t_dist * offset, border + (hmax - h0) / hd * ty),
                  (thermal_visualisation(tmp)[0]), (120, 120, 120), font=font)
        shape_temp = [(border + t_dist * t0 * 0.1 + h0 / hmax * tx + t_dist * offset, border + (hmax - h0) / hd * ty),
                      (border + t_dist * t1 * 0.1 + h1 / hmax * tx + t_dist * offset, border + (hmax - h1) / hd * ty)]
        img1.line(shape_temp, fill="red", width=3)
        d1 = dewp.pop()
        dh1 = dewp.pop()
        shape_temp = [(max((border + t_dist * d0 * 0.1 + dh0 / hmax * tx + t_dist * offset), border),
                       border + (hmax - dh0) / hd * ty), (
                          max((border + t_dist * d1 * 0.1 + dh1 / hmax * tx + t_dist * offset), border),
                          border + (hmax - dh1) / hd * ty)]
        img1.line(shape_temp, fill="blue", width=3)
        t0 = t1
        h0 = h1
        d0 = d1
        dh0 = dh1


def calc_arrow(x, y, direction):
    dot = 4
    dx = dot * 2.3 * math.sin(math.radians(direction+180)) + x
    dy = - dot * 2.3 * math.cos(math.radians(direction+180)) + y
    dx1 = dot * 2 * math.sin(math.radians(direction+320)) + x
    dy1 = - dot * 2 * math.cos(math.radians(direction+320)) + y
    dx2 = dot * 1 * math.sin(math.radians(direction)) + x
    dy2 = - dot * 1 * math.cos(math.radians(direction)) + y
    dx3 = dot * 2 * math.sin(math.radians(direction+40)) + x
    dy3 = - dot * 2 * math.cos(math.radians(direction+40)) + y
    return dx, dy, dx1, dy1, dx2, dy2, dx3, dy3


# draw wind
def draw_wind(wind):
    hd = hmax - hmin
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
        dy = - wind_dot * 2.3 * math.cos(math.radians(direction + 180)) + border + (hmax - hight) / hd * ty
        dx1 = wind_dot * 2 * math.sin(math.radians(direction + 320)) + tx + border
        dy1 = - wind_dot * 2 * math.cos(math.radians(direction + 320))+ border + (hmax - hight) / hd * ty
        dx2 = wind_dot * 1 * math.sin(math.radians(direction)) + tx + border
        dy2 = - wind_dot * 1 * math.cos(math.radians(direction)) + border + (hmax - hight) / hd * ty
        dx3 = wind_dot * 2 * math.sin(math.radians(direction + 40)) + tx + border
        dy3 = - wind_dot * 2 * math.cos(math.radians(direction + 40)) + border + (hmax - hight) / hd * ty
        img1.polygon([dx, dy, dx1, dy1, dx2, dy2, dx3, dy3], fill=dot_color)
        img1.text((tx + border + wind_dot * 2, + border + (hmax - hight) / hd * ty - wind_dot * 1.5), str(strength),
                  (20, 20, 20), font=font)


# creating new Image object
def create_lines():
    i = 0
    while i < 6:
        img1.text((10, border + (hmax - i * 1000) / (hmax - hmin) * ty), str(i * 1000), (20, 20, 20), font=font)
        if i < 4:
            shape_temp = [(border + t_dist * i, h - border), (tx + border, border + t_dist * i + (ty-tx))]  # bottom
            img1.line(shape_temp, fill="lightgrey", width=0)
            if i > 0:
                shape_temp2 = [(border, h - border - t_dist * i), (h - border - t_dist * i, border)]  # lines from left
                img1.line(shape_temp2, fill="lightgrey", width=0)
            img1.text((border + t_dist * i, h - border), str((i - offset) * 10), (20, 20, 20), font=font_sm)
            if i < 3:
                img1.text((border + 90 + t_dist * i, border - 13), str((i - offset - 3) * 10),
                          (20, 20, 20), font=font_sm)
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
        color = ['palegreen', 'springgreen', 'limegreen', 'lawngreen', 'greenyellow', 'yellow', 'salmon', 'lightcoral', 'tomato', 'red']
    return color[min(int(strength/5), 9)]


def cloud_color(octas, rain):
    if rain > 0.1:
        color = ['white', 'powderblue', 'lightblue', 'cornflowerblue', 'royalblue', 'blue', 'darkblue', 'navy', 'navy']
    else:
        color = ['white', 'whitesmoke', 'gainsboro', 'lightgrey', 'lightgray', 'silver', 'darkgrey', 'darkgray', 'grey', 'gray']
    return color[min(int(octas), 8)]


def temp_color(tmp):
    color = ['lightgrey', 'palegreen', 'lawngreen', 'limegreen', 'orange']
    return color[min(int(max(0,(tmp-0.55)*10)), 4)]


def lift_color(lft):
    color = ['lightgrey', 'palegreen', 'lawngreen', 'limegreen', 'orange']
    return color[min(int(max(0, lft)), 4)]


def dist_color(dist):
    color = ['whitesmoke', 'palegreen', 'lawngreen', 'limegreen', 'forestgreen']
    return color[min(int(max(0, dist/40 + 0.99)), 4)]


# calculates the effective sun, depending on the angle of the start grid. hrs is the number of hours.
def effective_sun(sun, start_angle, hrs):
    alpha = min(hrs * 15 - 8 - (start_angle - 180), 180)
    s = int(sun * max(math.sin(math.radians(alpha - 90)), 0))
    return s


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
    soar_pot = 0
    k = -1
    while k < lines - 3:
        box = [(2 * border + tx, border + ty / lines * (k + 1)), (w - border, border + ty / lines * (k + 2))]
        if 2 * int(k / 2) == k:
            img1.rectangle(box, fill="lightgrey", outline="lightgrey")
            # headline
        if k == -1:
            img1.text((2 * border + tx + padding, border + ty / lines * (k + 1)),
                      'Zeit  Wind  Sonne  Wolken  Temp  Lift  Basis Soar', (20, 20, 20), font=font)
            img1.text((2 * border + tx + padding, border + 2.5 * padding + ty / lines * (k + 1)),
                      ' LT    km/h            l-m-h  °/100m   m/s   m', (20, 20, 20), font=font)
        else:
            # call thermal model
            model = thermal_model(temp700[index + k], dew700[index + k], temp1000[index + k], dew1000[index + k],
                                  temp1500[index + k], dew1500[index + k], temp1900[index + k], dew1900[index + k],
                                  temp3000[index + k], dew3000[index + k], temp4200[index + k], dew4200[index + k],
                                  temp5600[index + k], dew5600[index + k], 1240, radiation[index + k],
                                  precipitation[index + k] - 0.1, weather_code[index + k])
            # append model-data
            m_h = 800
            for model_data in model.html_string:
                model_html_string.append('DAY' + str(j) + 'LT' + str(k+10) + 'H' + str(m_h) + ',' + model_data + ',')
                m_h += 200

            # standard calculations
            content = time[index + k][11:]
            img1.text((2 * border + tx + padding, border + padding + ty / lines * (k + 1)), content, (20, 20, 20),
                      font=font)
            # wind
            wind_calc = (wind1000[index + k] + wind1500[index + k])/2
            press_diff = pressure_msl_locarno[index + k] - pressure_msl[index + k]
            wind_calc_dir = wind_dir1500[index + k]
            content = str(int(wind_calc)) + wind_direction(wind_calc_dir)
            img1.text((2 * border + tx + padding + col * 1, border + padding + ty / lines * (k + 1)), content,
                      (20, 20, 20), font=font)
            # sun
            sun = effective_sun(abs(radiation[index + k] / 8), 200, k+10)  # 200° - south start. k+10 is the time
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
            # temp beneath of Alp Scheidegg
            temp_below = (temp1500[index + k] - temp700[index + k]) / (1500 - 694) * -100
            # lift
            if wind1500[index + k] <= 25 and wind1900[index + k] <= 30:  # not too much wind for thermals
                begin_factor = pow(max(0, temp_below - 0.5), 0.1)
                lift = model.average_lift
                content = str(lift)
            else:
                lift = 0
                content = "Wind"
            if press_diff >= 4:  # no lift with foehn
                lift = 0
                content = str(lift)
            if lift >= 1:  # real thermals with green background
                greenbox = [(2 * border + tx + col * 5, border + ty / lines * (k + 1)),
                            (2 * border + tx + col * 6, border + ty / lines * (k + 2))]
                img1.rectangle(greenbox, fill=lift_color(lift), outline=lift_color(lift))
            img1.text((2 * border + tx + padding + col * 5, border + padding + ty / lines * (k + 1)), content,
                      (20, 20, 20), font=font)
            # strong wind
            if wind_calc > 65:
                strong_wind = strong_wind + 100
            if wind_calc > 40:
                strong_wind = strong_wind + 10
            elif wind_calc > 25:
                strong_wind = strong_wind + 1
            # bise
            if (wind_calc_dir < 120 or wind_calc_dir > 340) and wind_calc > 20:
                bise = bise + 100
            elif (wind_calc_dir < 120 or wind_calc_dir > 340) and wind_calc > 15:
                bise = bise + 10
            elif (wind_calc_dir < 120 or wind_calc_dir > 340) and wind_calc > 5:
                bise = bise + 1
                if bise_start == 0:
                    bise_start = k + 10
            if wind_calc > wind_max:  # determine direction of the wind-max
                wind_max = wind_calc
                major_wind_dir = wind_calc_dir
            # base
            base_height = int(round((model.base_top / 50)) * 50)
            if press_diff >= 4:
                foehn = max(foehn, press_diff)
                content = str(int(press_diff + 0.5)) + "hPa"
            elif cloud_cover_mid[index + k] < 0.1 and cloud_cover_low[index + k] < 0.1:
                content = 'blau'
            elif precipitation[index + k] > 0.1 and temp1000[index + k] >= 1:
                content = 'Regen'
            elif precipitation[index + k] > 0.1 and temp1000[index + k] < 1:
                content = 'Schnee'
            else:
                if lift > 0:
                    content = str(base_height)
                else:
                    content = "-"
            img1.text((2 * border + tx + padding + col * 6, border + padding + ty / lines * (k + 1)), content,
                      (20, 20, 20), font=font)
            if lift >= 1:  # root-function gets 1 with a base of 2'000 meters
                distance = int(distance + 4 * lift * pow(max((base_height - 1200), 0), 0.5) / 28.2)
            elif lift > 0.5:
                distance = distance + 1
            # soaring
            content = "-"
            font_color = (20, 20, 20)
            if (220 < wind_calc_dir <= 290) and foehn < 4.5 and (15 < wind_calc <= 35) and \
                    wind1900[index + k] < 50 and (precipitation[index + k] + precipitation[index + k + 1] < 0.1):
                content = "GH"
                if soar_pot == 0:
                    soar_pot = 1
                if wind_calc > 20:
                    content = "S"
                    font_color = (20, 164, 20)  # green
                    if soar_pot < 2:
                        soar_pot = 2
                if wind_calc > 25:
                    font_color = (255, 164, 20)  # orange
                    soar_pot = 3

            img1.text((2 * border + tx + padding + col * 7, border + padding + ty / lines * (k + 1)), content,
                      font_color, font=font)
        k = k + 1
    box = [(2 * border + tx, border + ty / lines * (k + 1)), (w - border, border + ty / lines * (k + 3))]
    if bise > 1:
        extra_text = "Bisentendenz"
        if bise_start > 12:
            extra_text = "Bisentendenz ab " + str(int(bise_start)) + "Uhr"
    if strong_wind > 2:
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
              'Pot. Distanz: ' + str(distance) + 'km ' + bindung + extra_text, (20, 20, 20), font=font)
    img1.text((2 * border + tx + padding, border + ty / lines * (k + 2)),
              'Nullgradgrenze auf ' + str(int(freezing_level[index + 5])) + 'm. ', (20, 20, 20), font=font)
    # remember key figures for the overview
    ov_potential.append(distance)
    ov_remark.append(extra_text)
    soar_potential.append(soar_pot)


# functions for the wind-diagram
def wind_diagram(index):
    pad = 4 # extra-Padding
    c = 0
    while c < 17:
        # headline
        img1.text((2 * border + c * col, border + pad), str(c+6) + ":00", (20, 20, 20), font=font)
        # wind
        box = [(2 * border + c * col - pad, border - pad + 2 * ty / lines), (2 * border + (c+1) * col - pad, border - pad + 2.8 * ty / lines)]
        img1.rectangle(box, fill=wind_color(wind4200[index + c], wind_dir4200[index + c]), outline='white')
        img1.text((2 * border + c * col + 6 * pad, border + 2 * ty / lines), str(int(wind4200[index + c])), (20, 20, 20), font=font)
        img1.polygon(calc_arrow(2 * border + c * col + 2 * pad, border + 3 * pad + 2 * ty / lines, wind_dir4200[index + c]), fill='dimgrey')

        box = [(2 * border + c * col - pad, border - pad + 3 * ty / lines), (2 * border + (c+1) * col - pad, border - pad + 3.8 * ty / lines)]
        img1.rectangle(box, fill=wind_color(wind3000[index + c], wind_dir3000[index + c]), outline='white')
        img1.text((2 * border + c * col + 6 * pad, border + 3 * ty / lines), str(int(wind3000[index + c])), (20, 20, 20), font=font)
        img1.polygon(calc_arrow(2 * border + c * col + 2 * pad, border + 3 * pad + 3 * ty / lines, wind_dir3000[index + c]), fill='dimgrey')

        box = [(2 * border + c * col - pad, border - pad + 4 * ty / lines), (2 * border + (c+1) * col - pad, border - pad + 4.8 * ty / lines)]
        img1.rectangle(box, fill=wind_color(wind1900[index + c], wind_dir1900[index + c]), outline='white')
        img1.text((2 * border + c * col + 6 * pad, border + 4 * ty / lines), str(int(wind1900[index + c])), (20, 20, 20), font=font)
        img1.polygon(calc_arrow(2 * border + c * col + 2 * pad, border + 3 * pad + 4 * ty / lines, wind_dir1900[index + c]), fill='dimgrey')

        box = [(2 * border + c * col - pad, border - pad + 5 * ty / lines), (2 * border + (c+1) * col - pad, border - pad + 5.8 * ty / lines)]
        img1.rectangle(box, fill=wind_color(wind1500[index + c], wind_dir1500[index + c]), outline='white')
        img1.text((2 * border + c * col + 6 * pad, border + 5 * ty / lines), str(int(wind1500[index + c])), (20, 20, 20), font=font)
        img1.polygon(calc_arrow(2 * border + c * col + 2 * pad, border + 3 * pad + 5 * ty / lines, wind_dir1500[index + c]), fill='dimgrey')

        box = [(2 * border + c * col - pad, border - pad + 6 * ty / lines), (2 * border + (c+1) * col - pad, border - pad + 6.8 * ty / lines)]
        img1.rectangle(box, fill=wind_color(wind1000[index + c], wind_dir1000[index + c]), outline='white')
        img1.text((2 * border + c * col + 6 * pad, border + 6 * ty / lines), str(int(wind1000[index + c])), (20, 20, 20), font=font)
        img1.polygon(calc_arrow(2 * border + c * col + 2 * pad, border + 3 * pad + 6 * ty / lines, wind_dir1000[index + c]), fill='dimgrey')
        # clouds
        clouds_l = int(abs(cloud_cover_low[index + c] / 12.5))
        clouds_m = int(abs(cloud_cover_mid[index + c] / 12.5))
        clouds_h = int(abs(cloud_cover_high[index + c] / 12.5))
        rain = precipitation[index + c]
        # clouds_high
        box = [(2 * border + c * col - pad, border - pad + 8 * ty / lines), (2 * border + (c+1) * col - pad, border - pad + 8.8 * ty / lines)]
        img1.rectangle(box, fill=cloud_color(clouds_h / 2, rain), outline='white')  # less color for high clouds
        img1.text((2 * border + c * col, border + 8 * ty / lines), "  " + str(clouds_h), (20, 20, 20), font=font)
        # clouds_mid
        box = [(2 * border + c * col - pad, border - pad + 9 * ty / lines), (2 * border + (c+1) * col - pad, border - pad + 9.8 * ty / lines)]
        img1.rectangle(box, fill=cloud_color(clouds_m, rain), outline='white')
        img1.text((2 * border + c * col, border + 9 * ty / lines), "  " + str(clouds_m), (20, 20, 20), font=font)
        # clouds_low
        box = [(2 * border + c * col - pad, border - pad + 10 * ty / lines), (2 * border + (c+1) * col - pad, border - pad + 10.8 * ty / lines)]
        img1.rectangle(box, fill=cloud_color(clouds_l, rain), outline='white')
        img1.text((2 * border + c * col, border + 10 * ty / lines), "  " + str(clouds_l), (20, 20, 20), font=font)
        # Temp until 3'000 meter
        grad3000 = -int(100 * ((temp3000[index + c] - temp1900[index + c]) / 11)) / 100
        box = [(2 * border + c * col - pad, border - pad + 12 * ty / lines), (2 * border + (c+1) * col - pad, border - pad + 12.8 * ty / lines)]
        img1.rectangle(box, fill=temp_color(grad3000), outline='white')
        img1.text((2 * border + c * col, border + 12 * ty / lines), str(grad3000), (20, 20, 20), font=font)
        # Temp until 1'900 meter
        grad1900 = -int(100 * ((temp1900[index + c] - temp1000[index + c]) / 9)) / 100
        box = [(2 * border + c * col - pad, border - pad + 13 * ty / lines), (2 * border + (c+1) * col - pad, border - pad + 13.8 * ty / lines)]
        img1.rectangle(box, fill=temp_color(grad1900), outline='white')
        img1.text((2 * border + c * col, border + 13 * ty / lines), str(grad1900), (20, 20, 20), font=font)
        # Süd-Nord-Überdruck
        sn_diff = pressure_msl_locarno[index + c] - pressure_msl[index + c]
        box = [(2 * border + c * col - pad, border - pad + 14 * ty / lines), (2 * border + (c+1) * col - pad, border - pad + 14.8 * ty / lines)]
        img1.rectangle(box, fill=wind_color(max(0,(8 * sn_diff)), 270), outline='white')
        img1.text((2 * border + c * col, border + 14 * ty / lines), str(int(sn_diff + 0.5)) + "hPa", (20, 20, 20), font=font)
        c = c + 1
    z = 0
    categories = ["Wind (km/h)", "4200", "3000", "1900", "1500", "1000", "Wolken (Achtel)", "hoch", "mittel", "tief"
        , "Temp (°C/100m)", "3000", "1900", "Föhn", ""]
    while z < 14:
        img1.text((border, border + (z + 1) * ty / lines), categories.pop(0), (20, 20, 20), font=font)
        z = z + 1


# here we start
forcast_payload = get_meteo()
# print(meteo_forcast)
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
weather_code = hourly["weather_code"]
freezing_level = hourly["freezing_level_height"]
# get Locarno Pressure-Reference
meteo_forcast_locarno = get_meteo_locarno()
print(meteo_forcast_locarno)
forcast_dump_locarno = json.dumps(meteo_forcast_locarno)
forcast_payload_locarno = json.loads(forcast_dump_locarno)
hourly_locarno = forcast_payload_locarno["hourly"]
pressure_msl_locarno = hourly_locarno["pressure_msl"]
# get meta-data of the weather model
icon_eu = get_meta_data('https://api.open-meteo.com/data/dwd_icon_eu/static/meta.json')
icon_d2 = get_meta_data('https://api.open-meteo.com/data/dwd_icon_d2/static/meta.json')


###################
# prepare diagram
###################
w, h = 1140, 680
hmax, hmin = 5600, 700
border = 60
tx, ty = 500, 560 # position of data-box
t_dist = 150
wind_dot = 6
padding = 8
shape = [(border, border), (w - border, h - border)]

# font
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
font_sm = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
font_el = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 64)

# create new image
img = Image.new("RGB", (w, h), color=(240, 240, 250, 250))
# create rectangle image
img1 = ImageDraw.Draw(img)
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
        offset = - int(temp1900[i] / 10)  # for negative temperatures 1, then 0 for low positive and +1 if hot.
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
        # draw the temp
        draw_temp(temp, dew_point)
        # create temperature lines
        create_lines()
        # draw the wind
        draw_wind(wind)
        # create thermal data
        create_thermal_data(i - 4)  # 14:00 - 4 = 10:00 Uhr
        # title
        if j < 2:
            img1.text((10, 20), "Alp Scheidegg forecast for " + x.strftime("%A, %d/%m/%Y")
                  + ", ICON-D2, run: " + icon_d2 + ", updated: " + now.strftime("%d/%m/%Y %H:%M")
                  + " CET", (20, 20, 20), font=font)
        else:
            img1.text((10, 20), "Alp Scheidegg forecast for " + x.strftime("%A, %d/%m/%Y")
                + ", ICON-EU (7km), run: " + icon_eu + ", updated: " + now.strftime("%d/%m/%Y %H:%M")
                + " CET", (20, 20, 20), font=font)
        # save the image here
        img.save("/var/www/html/thermals/forecast" + str(j) + ".png")
        # remember the weekday for the overview
        if j == 0:
            ov_days.append("7")
        else:
            ov_days.append(x.strftime("%w"))
        # the second image for the wind
        img = Image.new("RGB", (w, h), color=(250, 250, 250, 250))
        img1 = ImageDraw.Draw(img)
        img1.rectangle(shape, fill="#ffffff", outline="white")
        wind_diagram(i - 8) # 14:00 - 8 = 06:00Uhr
        if j < 2:
            img1.text((10, 20), "Alp Scheidegg forecast for " + x.strftime("%A, %d/%m/%Y")
                      + ", ICON-D2, run: " + icon_d2 + ". updated: " + now.strftime("%d/%m/%Y %H:%M")
                      + " CET", (20, 20, 20), font=font)
        else:
            img1.text((10, 20), "Alp Scheidegg forecast for " + x.strftime("%A, %d/%m/%Y")
                      + ", ICON-EU (7km), run: " + icon_eu + ". updated: " + now.strftime("%d/%m/%Y %H:%M")
                      + " CET", (20, 20, 20), font=font)
        img.save("/var/www/html/thermals/meteo_wind" + str(j) + ".png")

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

h = 180
days = 5
wov = int(w / days)
# create rectangle image
i = 0
while i < days:
    img = Image.new("RGB", (wov, h), color=(240, 240, 250, 250))
    # create rectangle image
    img1 = ImageDraw.Draw(img)  # overview image

    box = ((0, 0), (wov, h))
    distance = ov_potential.pop(0)
    soar = soar_potential.pop(0)
    img1.rectangle(box, fill=dist_color(distance), outline=dist_color(distance))
    img1.text((3 * padding, 3 * padding), wds[int(ov_days.pop(0))], (20, 20, 20), font=font)
    img1.text((0.3 * wov, 0.3 * h), str(distance), (20, 20, 20), font=font_el)
    img1.text((3 * padding, h - 36), ov_remark.pop(0), (20, 20, 20), font=font)
    # soaring
    if soar > 0:
        color = 'grey'
        soar_text = ' S'
        if soar == 1:
            soar_text = 'GH'
        if soar == 2:
            color = 'green'
        if soar == 3:
            color = 'orange'
        img1.ellipse((140, 15, 170, 45), fill=color)
        img1.text((141, 20), soar_text, (240, 240, 240), font=font)
    img.save("/var/www/html/thermals/thermal_button" + str(i) + ".png")
    i = i + 1

# create csv with thermal updrafts
image_path = "/var/www/html/thermals/"
final_string = ''
for data in model_html_string:
    final_string += data
print(final_string)  # append model-data)
result_file = open(image_path + "thermal_data.txt", "w")
result_file.write(final_string)
result_file.close()

print("Hoi Thomas")
# send it to DCZO-webserver
session = ftplib.FTP('ftp.dczo.ch', constants.ftp_user, constants.ftp_pw)
file = open('/var/www/html/thermals/forecast0.png','rb')                  # file to send
file1 = open('/var/www/html/thermals/forecast1.png','rb')                  # file to send
file2 = open('/var/www/html/thermals/forecast2.png','rb')                  # file to send
file3 = open('/var/www/html/thermals/forecast3.png','rb')                  # file to send
file4 = open('/var/www/html/thermals/forecast4.png','rb')                  # file to send
wind_file0 = open('/var/www/html/thermals/meteo_wind0.png','rb')           # wind_file to send
wind_file1 = open('/var/www/html/thermals/meteo_wind1.png','rb')           # wind_file to send
wind_file2 = open('/var/www/html/thermals/meteo_wind2.png','rb')           # wind_file to send
wind_file3 = open('/var/www/html/thermals/meteo_wind3.png','rb')           # wind_file to send
wind_file4 = open('/var/www/html/thermals/meteo_wind4.png','rb')           # wind_file to send
ovr_file0 = open('/var/www/html/thermals/thermal_button0.png','rb')        # overview0 to send
ovr_file1 = open('/var/www/html/thermals/thermal_button1.png','rb')        # overview1 to send
ovr_file2 = open('/var/www/html/thermals/thermal_button2.png','rb')        # overview2 to send
ovr_file3 = open('/var/www/html/thermals/thermal_button3.png','rb')        # overview3 to send
ovr_file4 = open('/var/www/html/thermals/thermal_button4.png','rb')        # overview4 to send
therm_model = open('/var/www/html/thermals/thermal_data.txt','rb')        # thermal_model to send
session.storbinary('STOR forecast0.png', file)     # send the file
session.storbinary('STOR forecast1.png', file1)     # send the file
session.storbinary('STOR forecast2.png', file2)     # send the file
session.storbinary('STOR forecast3.png', file3)     # send the file
session.storbinary('STOR forecast4.png', file4)     # send the file
session.storbinary('STOR meteo_wind0.png', wind_file0)  # send the file
session.storbinary('STOR meteo_wind1.png', wind_file1)  # send the file
session.storbinary('STOR meteo_wind2.png', wind_file2)  # send the file
session.storbinary('STOR meteo_wind3.png', wind_file3)  # send the file
session.storbinary('STOR meteo_wind4.png', wind_file4)  # send the file
session.storbinary('STOR thermal_button0.png', ovr_file0)  # send the file
session.storbinary('STOR thermal_button1.png', ovr_file1)  # send the file
session.storbinary('STOR thermal_button2.png', ovr_file2)  # send the file
session.storbinary('STOR thermal_button3.png', ovr_file3)  # send the file
session.storbinary('STOR thermal_button4.png', ovr_file4)  # send the file
session.storbinary('STOR thermal_data.txt', therm_model)  # send the file
file.close()                                    # close file and FTP
session.quit()
print ("files sent to DCZO")
