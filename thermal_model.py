# thermal model to simulate a rising air parcel in the given atmosphere.
import math
updraft_factor = 30
dry_adiabatic = 0.979
moisture_adiabatic = 0.562
mixing_100 = 0.10


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
    __start_level = 1000

    def __init__(self, temp_1000, dew_1000, temp_1500, dew_1500, temp_1900, dew_1900, temp_3000, dew_3000,
                 temp_4200, dew_4200, temp_5600, dew_5600, temp_advance):
        self.__temps = []
        self.__dews = []
        self.__parcel_temps = []
        self.__parcel_dews = []
        self.__condensation = []
        self.__parcel_density = []
        self.__air_density = []
        self.__heights = []
        self.__updraft = []
        updraft = 1
        i = self.__start_level
        while i <= 5600 and updraft > 0:
            if i <= 1500:
                self.__temps.append(temp_1000 * (1500 - i) / 500 + temp_1500 * (i - 1000) / 500)
                self.__dews.append(dew_1000 * (1500 - i) / 500 + dew_1500 * (i - 1000) / 500)
            elif i <= 1900:
                self.__temps.append(temp_1500 * (1900 - i) / 400 + temp_1900 * (i - 1500) / 400)
                self.__dews.append(dew_1500 * (1900 - i) / 400 + dew_1900 * (i - 1500) / 400)
            elif i <= 3000:
                self.__temps.append(temp_1900 * (3000 - i) / 1100 + temp_3000 * (i - 1900) / 1100)
                self.__dews.append(dew_1900 * (3000 - i) / 1100 + dew_3000 * (i - 1900) / 1100)
            elif i <= 4200:
                self.__temps.append(temp_3000 * (4200 - i) / 1200 + temp_4200 * (i - 3000) / 1200)
                self.__dews.append(dew_3000 * (4200 - i) / 1200 + dew_4200 * (i - 3000) / 1200)
            elif i <= 5600:
                self.__temps.append(temp_4200 * (5600 - i) / 1400 + temp_5600 * (i - 4200) / 1400)
                self.__dews.append(dew_4200 * (5600 - i) / 1400 + dew_5600 * (i - 4200) / 1400)
            self.__heights.append(i)

            # parcel conditions
            if i == self.__start_level:
                self.__parcel_temps.append(temp_1000 + temp_advance)
                self.__parcel_dews.append(dew_1000)
                self.__condensation.append('no')
            else:
                if self.__temps[-1] > self.__parcel_dews[-1] + 0.5:
                    # no condensation case
                    self.__parcel_temps.append(self.__parcel_temps[-1] - dry_adiabatic)
                    self.__parcel_dews.append(self.__parcel_dews[-1] * (1 - mixing_100)
                                              + mixing_100 * self.__dews[-1])
                    self.__condensation.append('no')
                else:
                    self.__condensation.append('yes')
                    # condensation case
                    self.__parcel_temps.append(self.__parcel_temps[-1] - moisture_adiabatic)
                    self.__parcel_dews.append(self.__parcel_temps[-1] * (1 - mixing_100)
                                              + mixing_100 * self.__dews[-1])
            #  density of the air parcel
            self.__parcel_density.append(density(alt2pres(i), self.__parcel_temps[-1],
                                                 rh_from_tdew(self.__parcel_temps[-1], self.__parcel_dews[-1])))
            #  density of the ambient air
            self.__air_density.append(density(alt2pres(i), self.__temps[-1],
                                                 rh_from_tdew(self.__temps[-1], self.__dews[-1])))
            #  updraft
            updraft = updraft_factor * max(self.__air_density[-1] - (self.__parcel_density[-1]), 0) ** 0.5
            self.__updraft.append(updraft)
            i = i + 100

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
