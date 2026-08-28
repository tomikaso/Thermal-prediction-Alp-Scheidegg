# thermal model to simulate a rising air parcel in the given atmosphere.
import math
from datetime import datetime
import time

# thermodynamic parameters
updraft_factor = 48
dry_adiabatic = 0.979
moisture_adiabatic = 0.562
mixing_dry = 0.1
mixing_wet = 0.10
std_pressure = 101325


# calculate density
def density(pressure, temp, humi):
    Rda = 287.058  # R dry air
    Rva = 461.51  # R vapor
    Pp_sat = 611 * math.exp(17.62 * temp / (243.12 + temp))
    Rma = Rda / (1 - (humi * (Pp_sat / pressure)) * (1 - Rda / Rva))  # R moisturized air
    return pressure / Rma / (temp + 273.15)


# calculate pressure, depending on the altitude
def alt2pres(altitude):
    return 100 * ((44331.514 - altitude) / 11880.516) ** (1 / 0.1902632)


# relative humidity
def rh_from_tdew(temp_air, temp_dew):
    # Calculate vapor pressure (e) and saturation vapor pressure (es)
    e = 6.112 * 2.718281 ** ((17.62 * temp_air) / (243.12 + temp_air))
    es = 6.112 * 2.718281 ** ((17.62 * temp_dew) / (243.12 + temp_dew))
    return es / e


# here the class starts
class thermal_model:
    # simple thermal model
    ground_level = 700
    html_string = []
    average_lift = 0
    base_top = 0

    def __init__(self, temp_2m, dew_2m, temp_1000, dew_1000, temp_1500, dew_1500, temp_1900, dew_1900, temp_3000,
                 dew_3000, temp_4200, dew_4200, temp_5600, dew_5600, start_height, mountain_top, radiation,
                 precipitation, weather_cd, time_hr, terrain):
        self.__ground_level = 500
        self.__temps = []
        self.__dews = []
        self.__parcel_temps = []
        self.__parcel_dews = []
        self.__condensation = []
        self.__parcel_density = []
        self.__air_density = []
        self.__heights = []
        self.__updraft = []
        calculation_base = max(self.ground_level, start_height - 500)
        condensed = 0
        updraft = 0
        # astro parameters for alpine starting places.
        latitude = 47.255
        date = datetime.now()
        post_winter_solstice = date.month * 30 + date.day - 20
        if post_winter_solstice >= 360:
            post_winter_solstice = post_winter_solstice - 360
        # calculate the position of the sun
        maxdeclination = 90 - latitude - 23.5 * math.cos(post_winter_solstice / 360 * 6.28)
        # maxdeclination = 19.5
        # post_winter_solstice = 0
        if time.localtime().tm_isdst > 0:  # adjust midday to daylight saving time
            midday = 13.5
        else:
            midday = 12.5
        daylength = 12.2 - 3.74 * math.cos(post_winter_solstice / 360 * 6.28)
        delta_zenit = (midday - time_hr) * 12 / daylength
        sun_angle = max(math.asin(math.sin(math.radians(maxdeclination))
                                  * math.cos(math.radians(delta_zenit * 15))) * 180 / math.pi, 0)
        rad90 = radiation / math.sin(max(math.radians(sun_angle), 0.1))
        print('time: ', time_hr, ' sun angle: ', sun_angle, ' post winter solstice:', post_winter_solstice,
              ' max decl. ', maxdeclination, ' Terrain: ', terrain, ' radiation:', radiation, ' 90-deg:', rad90)

        # calculate the distribution of sun in the valley and in the mountains from the declination of the sun
        if terrain == 'alpine':
            rad_effective = math.sin(math.radians(sun_angle + 40)) * rad90  # 40° steepness
        elif terrain == 'pre-alpine':
            rad_effective = math.sin(math.radians(sun_angle + 20)) * rad90  # 20° steepness
        else:
            rad_effective = 0  # hotplate case
        self.html_string.clear()
        i = self.__ground_level
        while i <= 5600:
            if i <= 1000:
                val2st = 1000 - self.__ground_level  # valley to start level
                self.__temps.append(temp_2m * (1000 - i) / val2st + temp_1000 * (i - self.__ground_level) / val2st)
                self.__dews.append(dew_2m * (1000 - i) / val2st + dew_1000 * (i - self.__ground_level) / val2st)
            if 1460 >= i > 1000:
                self.__temps.append(temp_1000 * (1460 - i) / 460 + temp_1500 * (i - 1000) / 460)
                self.__dews.append(dew_1000 * (1460 - i) / 460 + dew_1500 * (i - 1000) / 460)
            elif 1930 >= i > 1460:
                self.__temps.append(temp_1500 * (1930 - i) / 470 + temp_1900 * (i - 1460) / 470)
                self.__dews.append(dew_1500 * (1930 - i) / 470 + dew_1900 * (i - 1460) / 470)
            elif 3000 >= i > 1930:
                self.__temps.append(temp_1900 * (3000 - i) / 1100 + temp_3000 * (i - 1930) / 1100)
                self.__dews.append(dew_1900 * (3000 - i) / 1100 + dew_3000 * (i - 1930) / 1100)
            elif 4200 >= i > 3000:
                self.__temps.append(temp_3000 * (4200 - i) / 1200 + temp_4200 * (i - 3000) / 1200)
                self.__dews.append(dew_3000 * (4200 - i) / 1200 + dew_4200 * (i - 3000) / 1200)
            elif 5600 >= i > 4200:
                self.__temps.append(temp_4200 * (5600 - i) / 1400 + temp_5600 * (i - 4200) / 1400)
                self.__dews.append(dew_4200 * (5600 - i) / 1400 + dew_5600 * (i - 4200) / 1400)
            self.__heights.append(i)

            # parcel conditions
            if i == self.__ground_level:  # boilerplate-case
                self.__parcel_temps.append(temp_2m + radiation / 2400)  # just 1/3 rd
                self.__parcel_dews.append(dew_2m)
                self.__condensation.append('no')
            elif calculation_base <= i < calculation_base + 100:  # add 1 Kelvin under perfect conditions
                self.__parcel_temps.append(self.__temps[-1] + std_pressure / alt2pres(i) * radiation / 800)
                self.__parcel_dews.append(self.__parcel_dews[-1] * (1 - mixing_dry)
                                          + mixing_dry * self.__dews[-1])
                self.__condensation.append('no')
            else:
                factor = max(1, 2 - updraft)  # the weaker the updraft, the more mixes ambient air into the parcel
                if self.__temps[-1] > self.__parcel_dews[-1] + 0.5:
                    # no condensation case
                    if i <= mountain_top:  # add some energy as long as the peaks of the mountains are reached
                        self.__parcel_temps.append(self.__parcel_temps[-1] - dry_adiabatic
                                                   + std_pressure / alt2pres(i) * rad_effective / 3300)
                    else:
                        self.__parcel_temps.append((self.__parcel_temps[-1] - dry_adiabatic) * (1 - mixing_dry * factor)
                                                   + mixing_dry * factor * self.__temps[-1])
                    self.__parcel_dews.append(self.__parcel_dews[-1] * (1 - mixing_dry * factor)
                                              + mixing_dry * factor * self.__dews[-1])
                    self.__condensation.append('no')
                else:
                    self.__condensation.append('yes')
                    # condensation case
                    self.__parcel_temps.append((self.__parcel_temps[-1] - moisture_adiabatic)
                                               * (1 - mixing_wet * factor) + mixing_wet * factor * self.__temps[-1])
                    self.__parcel_dews.append((self.__parcel_dews[-1] - moisture_adiabatic) * (1 - mixing_wet * factor)
                                              + mixing_wet * factor * self.__dews[-1])

            #  density of the air parcel
            self.__parcel_density.append(density(alt2pres(i), self.__parcel_temps[-1],
                                                 rh_from_tdew(self.__parcel_temps[-1], self.__parcel_dews[-1])))
            #  density of the ambient air
            self.__air_density.append(density(alt2pres(i), self.__temps[-1],
                                              rh_from_tdew(self.__temps[-1], self.__dews[-1])))
            #  updraft
            updraft = max(0, (updraft_factor * max(self.__air_density[-1] - (self.__parcel_density[-1]), 0) ** 0.6))
            self.__updraft.append(updraft)
            # print('effective, rad90, rad', rad_effective, rad90, radiation, '  sun-angle: ', sun_angle)
            # write out results
            if 800 <= i <= 4000 and i % 200 == 0:  # one data point each 200 meters
                if i <= calculation_base:
                    self.html_string.append(str(i) + ',Green')
                else:
                    if self.__condensation[-1] == 'yes':
                        if 95 <= weather_cd < 100:
                            if self.__temps[-1] >= 0:
                                self.html_string.append(str(i) + ',cloud_flash')
                            else:
                                self.html_string.append(str(i) + ',cloud_flash_snow')
                        elif precipitation > 2:
                            if self.__temps[-1] >= 0:
                                self.html_string.append(str(i) + ',cloud_rain2')
                            else:
                                self.html_string.append(str(i) + ',cloud_snow2')
                        elif precipitation > 0:
                            if self.__temps[-1] >= 0:
                                self.html_string.append(str(i) + ',cloud_rain1')
                            else:
                                self.html_string.append(str(i) + ',cloud_snow1')
                        elif updraft > 0:
                            self.html_string.append(str(i) + ',cloud_cumulus')
                        condensed = 1
                    elif condensed == 0 and updraft > 0:
                        self.html_string.append(str(i) + ',' + str(round(updraft, 1)))
            i = i + 100

            # average lift and base / top
            if i > start_height and updraft > 0.5 and condensed == 0:
                self.average_lift = round(max(updraft, self.average_lift), 1)
                self.base_top = i

    # print out results
    def show_results(self):
        i = 0
        while i < len(self.__heights):
            print(self.__heights[i], 'm, T:', round(self.__temps[i], 2), '°, DP:',
                  round(self.__dews[i], 2), '°, Parcel-temp:',
                  round(self.__parcel_temps[i], 2), '°, Parcel-DP:', round(self.__parcel_dews[i], 2), '° Cond=',
                  self.__condensation[i], ', Density=', round(self.__parcel_density[i], 4), ' ambient:',
                  round(self.__air_density[i], 4), ' updraft: ', round(self.__updraft[i], 2))
            i += 1

    # print out results
    def result_diagram(self):
        i = 0
        cloud = ''
        while i < len(self.__heights) and self.__updraft[i] > 0:
            if self.__condensation[i] == 'yes':
                cloud = 'cloud'
            else:
                cloud = ''
            print(self.__heights[i], 'm, Up=', round(self.__updraft[i], 2), ' ', cloud)
            i += 1
