import requests, json, datetime
import math
from PIL import Image, ImageDraw, ImageFont
from datetime import date

# initialize variable
temp = []
dew_point = []
wind = []
now = date.today()
# for the data grid
col = 56
lines = 14


# get the data
def get_meteo():
    status = 'online'
    try:
        y = requests.get('https://api.open-meteo.com/v1/forecast?latitude=47.289&longitude=8.915&'
                         'hourly=temperature_2m,wind_speed_10m,wind_direction_10m,dew_point_2m,'
                         'direct_radiation,precipitation,cloud_cover,'
                         'temperature_900hPa,dew_point_900hPa,wind_speed_900hPa,wind_direction_900hPa,'
                         'temperature_850hPa,dew_point_850hPa,wind_speed_850hPa,wind_direction_850hPa,'
                         'temperature_800hPa,dew_point_800hPa,wind_speed_800hPa,wind_direction_800hPa,'
                         'temperature_700hPa,dew_point_700hPa,wind_speed_700hPa,wind_direction_700hPa,'
                         'temperature_600hPa,dew_point_600hPa,wind_speed_600hPa,wind_direction_600hPa,'
                         'temperature_500hPa,dew_point_500hPa,wind_speed_500hPa,wind_direction_500hPa'
                         '&timezone=Europe%2FBerlin&models=icon_seamless', timeout=10)
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


# draw wind
def draw_wind(wind):
    while len(wind) > 0:
        direction = wind.pop()
        strength = int(wind.pop())
        hight = wind.pop()
        if strength < 16 and direction > 180 and direction < 290:
            dot_color = "limegreen"
        elif strength < 30:
            dot_color = "orange"
        else:
            dot_color = "tomato"
        # wind-arrow
        dx = wind_dot * 2 * math.sin(math.radians(direction)) + tx + border
        dy = - wind_dot * 2 * math.cos(math.radians(direction)) + ty - hight / hmax * ty + border
        dx1 = wind_dot * 0.5 * math.sin(math.radians(direction + 90)) + tx + border
        dy1 = - wind_dot * 0.5 * math.cos(math.radians(direction + 90)) + ty - hight / hmax * ty + border
        dx2 = wind_dot * 0.5 * math.sin(math.radians(direction - 90)) + tx + border
        dy2 = - wind_dot * 0.5 * math.cos(math.radians(direction - 90)) + ty - hight / hmax * ty + border
        img1.polygon([dx, dy, dx1, dy1, dx2, dy2], fill="black")
        img1.ellipse((tx + border - wind_dot, ty - hight / hmax * ty - wind_dot + border, tx + border + wind_dot,
                      ty - hight / hmax * ty + wind_dot + border), fill=dot_color)
        img1.text((tx + border - wind_dot / 2, ty - hight / hmax * ty - wind_dot / 2 + border), str(strength),
                  (20, 20, 20), font=font)


# creating new Image object
def create_lines():
    i = 0
    while i < 7:
        img1.text((10, border + ty - i * 1000 / hmax * ty), str(i * 1000), (20, 20, 20), font=font)
        if i < 4:
            shape_temp = [(border + t_dist * i, h - border), (tx + border, border + t_dist * i)]
            shape_temp2 = [(border, h - border - t_dist * i), (tx + border - t_dist * i, border)]
            img1.line(shape_temp, fill="black", width=0)
            img1.line(shape_temp2, fill="black", width=0)
            img1.text((border + t_dist * i, h - border), str((i - offset) * 10), (20, 20, 20), font=font_sm)
        i = i + 1


# wind-direction
def wind_direction(grad):
    wd = ['N', 'NO', 'O', 'SO', 'S', 'SW', 'W', 'NW', 'N']
    return wd[int(0.5 + grad / 45)]


# create thermal data lines
def create_thermal_data(index):
    # model-variables
    t1 = 0.6  # at this point thermals begin to be usable
    tm = 1.1  # maximum possible temp
    tf = 5  # temp factor
    distanz = 0
    bise = 0
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
            content = str(int(wind1500[index + k])) + " " + wind_direction(wind_dir1500[index + k])
            img1.text((2 * border + tx + padding + col * 1, border + padding + ty / lines * (k + 1)), content,
                      (20, 20, 20), font=font)
            # sun
            sun = int(abs(radiation[index + k] / 8))
            img1.text((2 * border + tx + padding + col * 2, border + padding + ty / lines * (k + 1)), str(sun) + "%",
                      (20, 20, 20), font=font)
            # clouds
            clouds = int(abs(cloud_cover[index + k] / 12.5))
            img1.text((2 * border + tx + padding + col * 3, border + padding + ty / lines * (k + 1)),
                      str(clouds) + "/8", (20, 20, 20), font=font)

            # temp
            # tmp = -int(100*((temp3000[index+k]-temp1000[index+k])/20))/100
            tmp = -int(100 * ((temp1900[index + k] - temp1000[index + k]) / 9)) / 100
            img1.text((2 * border + tx + padding + col * 4, border + padding + ty / lines * (k + 1)), str(tmp),
                      (20, 20, 20), font=font)
            # lift
            if wind1500[index + k] <= 30:
                lift = int(pow((max(0, ((max(0, (tmp - t1) / (tm - t1)) * tf + sun / 100) - 1)) * 2), 0.8) * 10) / 10
                content = str(lift)
                if wind_dir1500[index + k] < 120:
                    bise = 1
            else:
                lift = 0
                content = "Wind"
            img1.text((2 * border + tx + padding + col * 5, border + padding + ty / lines * (k + 1)), content,
                      (20, 20, 20), font=font)
            # base
            if cloud_cover[index + k] < 0.1:
                content = 'blau'
            elif precipitation[index + k] > 0.5:
                content = 'rain'
            else:
                if lift > 0:
                    content = str(int(round(100 * ((temp1000[index + k] - dew1000[index + k]) * 100 + 1000)) / 100))
                    distanz = int(distanz + 4 * lift)
                else:
                    content = "-"
            img1.text((2 * border + tx + padding + col * 6, border + padding + ty / lines * (k + 1)), content,
                      (20, 20, 20), font=font)
        k = k + 1
    box = [(2 * border + tx, border + ty / lines * k), (w - border, border + ty / lines * (k + 2))]
    color = "lightgrey"
    if distanz > 100:
        color = "forestgreen"
    if distanz > 50 and distanz <= 100:
        color = "springgreen"
    if distanz > 0 and distanz <= 50:
        color = "lightgreen"
    if bise == 1:
        extra_text = " (Bise)"
    img1.rectangle(box, fill=color, outline=color)
    img1.text((2 * border + tx + padding, border + padding + ty / lines * k),
              'Pot. Distanz = ' + str(distanz) + ' km' + extra_text, (20, 20, 20), font=font)


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
cloud_cover = hourly["cloud_cover"]
###################
# prepare diagram
###################
w, h = 1140, 680
hmax = 6000
border = 60
tx, ty = 560, 560
t_dist = 150
wind_dot = 20
padding = 5
offset = 0  # in winter = 1
shape = [(border, border), (w - border, h - border)]

# font
# font = ImageFont.truetype("arial.ttf", 18, encoding="unic")
# font_sm = ImageFont.truetype("arial.ttf", 14, encoding="unic")
# font = ImageFont.load_default(size=18)
# font_sm = ImageFont.load_default(size=14)
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
font_sm = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)

# create new image
img = Image.new("RGB", (w, h), color=(250, 250, 250, 250))
# create rectangle image
img1 = ImageDraw.Draw(img)
img1.rectangle(shape, fill="#ffffff", outline="white")
# create temperature lines
create_lines()

# get the data ready
print(len(time))
i = 0
j = 0
while i < len(time) and j < 5:
    if time[i][11:] == '14:00':
        print(time[i], ' Posi:', i, ' create forecast')
        x = datetime.datetime(int(time[i][:4]), int(time[i][5:-9]), int(time[i][8:-6]))
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
        # draw the temp
        draw_temp(temp, dew_point)
        # draw the wind
        draw_wind(wind)
        # create temperature lines
        create_lines()
        # create thermal data
        create_thermal_data(i - 4)  # 14:00 - 4 = 10:00 Uhr
        # title
        img1.text((10, 30), "Alp Scheidegg forecast for " + x.strftime("%A, %d/%m/%Y")
                  + ", data-source: open-meteo / ICON from " + now.strftime("%d/%m/%Y"), (20, 20, 20), font=font)
        # save the image here
        img.save("/var/www/html/thermals/forecast" + str(j) + ".png")

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
print("Temp_list", temp)
print("Hoi Thomas")