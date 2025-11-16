# here the class starts
def wind_angle(angle1, angle2, fraction):
    if angle1 - angle2 > 180:
        angle2 = angle2 + 360
    if angle2 - angle1 > 180:
        angle1 = angle1 + 360
    return (angle1 * fraction + angle2 * (1-fraction)) % 360  # returns an angle in the range 0 to 359


class wind_interpolation:
    # interpolate the wind values
    html_string = []

    def __init__(self, wind_500, dir_500, wind_1000, dir_1000, wind_1500, dir_1500, wind_1900, dir_1900, wind_3000,
                 dir_3000, wind_4200, dir_4200):
        self.html_string.clear()
        i = 800
        wind = 0
        direction = 0
        while i <= 4200:
            if i <= 1000:
                wind = (wind_500 * (1000 - i) / 500 + wind_1000 * (i - 500) / 500)
                direction = wind_angle(dir_500, dir_1000, (1000 - i) / 500)
            if 1500 >= i > 1000:
                wind = (wind_1000 * (1500 - i) / 500 + wind_1500 * (i - 1000) / 500)
                direction = wind_angle(dir_1000, dir_1500, (1500 - i) / 500)
            elif 1900 >= i > 1500:
                wind = (wind_1500 * (1900 - i) / 400 + wind_1900 * (i - 1500) / 400)
                direction = wind_angle(dir_1500, dir_1900, (1900 - i) / 400)
            elif 3000 >= i > 1900:
                wind = (wind_1900 * (3000 - i) / 1100 + wind_3000 * (i - 1900) / 1100)
                direction = wind_angle(dir_1900, dir_3000, (3000 - i) / 1100)
            elif 4200 >= i > 3000:
                wind = (wind_3000 * (4200 - i) / 1200 + wind_4200 * (i - 3000) / 1200)
                direction = wind_angle(dir_3000, dir_4200, (4200 - i) / 1200)
            # write out results
            self.html_string.append(str(i) + ',' + str(int(wind)).rjust(3, '0') + 'KMH'
                                    + str(int(direction)).rjust(3, '0') + 'DEG')
            i = i + 200
