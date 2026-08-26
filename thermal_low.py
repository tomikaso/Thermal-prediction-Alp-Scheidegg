# ----------------------------------------------------
# - Class to calculate the strength of the thermal low
# ----------------------------------------------------
from datetime import datetime
now = datetime.now()
snow_level = {1: 1200, 2: 1000, 3: 1600, 4: 1800, 5: 2200, 6: 2600,
              7: 3000, 8: 3300, 9: 3500, 10: 3200, 11: 2500, 12: 1600, 13: 1200}
month_fraction = int(now.strftime('%d')) / 31
month = int(now.strftime('%m'))  # interpolation of monthly snow levels
snow_l = snow_level[int(month)] * (1 - month_fraction) + snow_level[int(month + 1)] * month_fraction


class thermal_low:
    html_string = ''
    thermal_activity = []

    def __init__(self, temp1500, temp3000, radiation, start_height):

        # idea: for all alpine starting grids: average Temp 1500-3000, average radiation, snow frontier
        # build: sliding averages to be time lagging.
        # one percentage per thermal_low per hour from 10:00 to 20:00
        # estimate the snow frontier by the date
        day = 0
        snow_factor = snow_l / 3500
        while day < 5:
            time = 10
            while time <= 20:
                loc = 0
                alpine_count = 0
                alps_convection = 0
                while loc < len(start_height):
                    if start_height[loc] > 1600:  # we have an alpine starting grid
                        alpine_count += 1
                        tmp = (temp1500[loc, day * 24 + time] - temp3000[loc, day * 24 + time]) / 15  # 15 -> 1'500m
                        alps_convection += max(tmp-0.4, 0) * radiation[loc, day * 24 + time] * snow_factor
                    loc += 1
                self.thermal_activity.append(alps_convection/alpine_count)  # sum of convection / number of stations
                print('day: ', day, ' time:', time, ' convection: ', alps_convection/alpine_count)
                time += 1
            day += 1
        # create the HTML
        day = 0
        while day < 5:
            t = 1
            while t <= 11:
                value = sum(self.thermal_activity[max(0, (t - 3)) + day * 11: t + day * 11]) * 0.07  # Scaling-Factor
                self.html_string += str(round(value, 1)) + ', '
                t += 1
            day += 1
        print('HTML-String: ')
        print(self.html_string)
