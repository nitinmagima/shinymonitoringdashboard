# Trigger Monitoring Dashboard for Anticipated Action  Guide

This is a README file created for the Trigger Monitoring Dashboard for Anticipated Action Programs for WFP in various 
countries. The dashboard has been built in python using "Shiny for Python". The struture is similar to the Python 
maproom created for AA Design. The code base has been designed in such a way that only the YAML file needs to be 
updated to create a new Trigger Monitoring Dashboard. The Trigger Monitoring Dashboard takes advantage of the map rooms 
already created for respective countries and pulls  the data from there.The code has been divided  into four files: 

1. app.py - creates the front end of the dashboard. Creates filterable tables for admin 0 and admin 1 levels.  
2. utils.py - contains functions to use the maproom API
3. config.yaml - contains the data for the functions to work in utils.py 
4. get_admin1data.py - help manually update the config.yaml file of admin1_list. 



## YAML Description

In the config.yaml file, you will see that the structure of the YAML file is such that each country's map room has 
been listed, along with these variables.

1. maproom: to access the appropriate maproom
2. country: country name. The difference between the maproom variable and the country variable is that the maproom 
sometimes has the season hyphenated in it. This is why the maproom variable from the country variable has to be different
3. target_season: The target season is the season the maproom targetsmode: mode refers to the geographic level of the 
data. If you want the full country, it would be ‘0’, the next level (probably region) would be ‘1’, district (this case) 
would be ‘2’, and so on for as many levels are configured. Different admin levels are described in terms of both 
name and key, where the name is the admin level name and the key is the admin level in integer.
4. season:This field refers to the season you need data from, for now, all maptools have just one season, 
so this field will be always season1. This does not need to be changed. 
5. predictor=pnep: This refers to the variable that is predicting the season, in this case, ‘pnep’ refers to the IRI 
forecast result. It can change to total rainfall, average rainfall, or any other data set included in the tool. 
You can review all available predictors in the dropdown menu in the tool. To find the ID to use for a given variable, 
see the config file https://github.com/iridl/python-maprooms/blob/master/fbfmaproom/fbfmaproom-sample.yaml
6. predictand: This refers to the variable on which the forecast result will be compared and used to calculate 
the skill. It is usually labeled as bad years since we want to know how many of the known bad years are captured by 
the forecast. The available options are the same as for predictor (see above)
7. year: year of the season
8. issue_month0: the month you want the forecast result from. It is important to note that month counting starts at zero.
9. freq: This refers to the frequency of the event you want the forecast for. It corresponds to the ‘frequency of event’
slider in the tool
10. include_upcoming=false: This field states that the forecast for the upcoming season is not included in the 
historical statistics used to calculate the forecast or the skill. We usually include only past seasons in the 
historical data. 
11. design_tool: link to the design/maptool. Updates in the "Additional Resouces" tab in the front end
12. report: link to the AA reports.Updates in the "Additional Resouces" tab in the front end
13. username: use username if the maproom is behind a sign-in wall
14. password: use username if the maproom is behind a sign-in wall
15. threshold_protocol:The threshold protocol is decided during the respective country working groups to see if 
additional points are required to determine whether the forecast will be triggered or not
16. need_valid_keys: assign value True, without quotes (don't use "True"), if using admin1_list
17. admin1_list: this field refers to the list of keys or admin level 1 the AA project is focusing on. The admin1 list 
is there in case only certain admin1 units need to be shown in the trigger monitoring table, this list needs to be 
updated. To see the full list of keys, go to the data folder and see the respective maproom CSV file. If it's not there, 
you can use the get_admin1_data.py to create the CSV files in the data folder, and then open the CSV file that reflects 
your maproom name to update the admin1_list.

## Installation

To run the app, please follow instructions from here - https://shiny.posit.co/py/docs/install.html
