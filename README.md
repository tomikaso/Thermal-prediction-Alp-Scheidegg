Since the ICON weather model is open, it is possible to predict thermal activities for paragliders.
The main.py runs everywhere and produces an esay readable thermal chart for the starting place "Alp Scheidegg" in Switzerland. It uses the data of the ICON-forcasting model.
The second file thermal_forecast is basically the same, but optimized for Raspberry Pi. The png's created can be exposed to a webserver easily.

Short Description to the files:
thermal_forecast: forecast for single location (Alp Scheidegg). JS to display the results is found in display_js_styles.js

multi_forecast.py: forcasts 8 starting-grids and writes out 8 * 5 forecast png's. JS/Html to display the results is found in multitherm26.html
