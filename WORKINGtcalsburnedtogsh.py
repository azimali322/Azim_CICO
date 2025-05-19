from garminconnect import (
    Garmin,
    GarminConnectConnectionError,
    GarminConnectTooManyRequestsError,
    GarminConnectAuthenticationError,
)
from datetime import date, timedelta, datetime
import pygsheets
import pandas as pd
import numpy as np
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Get credentials from environment variables
email = os.getenv('GARMIN_EMAIL')
password = os.getenv('GARMIN_PASSWORD')
if not email or not password:
    raise ValueError("Please set GARMIN_EMAIL and GARMIN_PASSWORD environment variables")

#log into Garmin Connect
client = Garmin(email, password)
client.login()

#authorization
credentials_file = os.getenv('GOOGLE_SHEETS_CREDENTIALS_FILE')
spreadsheet_name = os.getenv('GOOGLE_SHEETS_NAME', 'CICO_Spreadsheet_Automated')  # Use environment variable with default value
if not credentials_file:
    raise ValueError("Please set GOOGLE_SHEETS_CREDENTIALS_FILE environment variable")
gc = pygsheets.authorize(service_file=credentials_file)

#open the google spreadsheet
#REMINDER THAT YOU NEED TO SHARE THE GSHEET TO THE EMAIL IN THE CREDENTIALS FILE!
sh = gc.open(spreadsheet_name)

#select the first sheet 
wks = sh[0]


#Today's date in datetime object
today = date.today()

#Generates Dataframes for A column (df4) and E column (df2), then merges them into df5 to see the last date calories burned was updated
df4 = wks.get_as_df(has_header=True, start=(1,1), end=(607,1), index_column=None, numerize=True,empty_value='', include_tailing_empty=False, include_tailing_empty_rows=False)
df2 = wks.get_as_df(has_header=True, start=(1,5), end=(607,5), index_column=None, numerize=True,empty_value='', include_tailing_empty=False, include_tailing_empty_rows=False)
df5 = pd.merge(df4, df2,left_index=True,right_index=True, how='inner')

#Generates string of last date calories burned was updated in GSheet
last_date_updated = df5.iloc[-1,0]

#generates datetime object from string
date_time_obj = datetime.strptime(last_date_updated, '%Y-%m-%d')

#generates datetime (timedelta) object from difference in dates (today's date - last date updated). This line can be removed because of while loop
days_prior_to_update = datetime.today() - date_time_obj

#generates integer value from difference in dates (today's date - last date entered). Note that if 2 past entries are missing, then this value would be 3.
x_days_back = (datetime.today() - date_time_obj).days

print(x_days_back) #Debugging to see if day difference. Can be removed.


#Initialize the list
calories_burned_list = []

#Find the number of calories in a specified day. day_of_stats = dictionary pulled from garminconnect
def calories_burned(day_of_stats):
	for key in day_of_stats:
		if key == 'totalKilocalories':
			return day_of_stats[key]
	return None

def bmr_calories_burned(day_of_stats):
	for key in day_of_stats:
		if key == 'bmrKilocalories':
			return day_of_stats[key]
	return None

def bmr_vs_total(day_of_stats):
	if calories_burned(day_of_stats) == bmr_calories_burned(day_of_stats):
		return 0
	else:
		return int(calories_burned(day_of_stats))

def xday_stats(day_of_stats):
	calories_burned_list.append(bmr_vs_total(day_of_stats))

def update_calories_burned_up_to_yesterday(n):
	while True:
		days_back = today - timedelta(days = n - 1) #Number of days back before last update as datetime object. Minus 1 because x_days_back is back to LAST entry day
		print(client.get_stats(days_back.isoformat())) #This step can be deleted later. It's for debugging to see if loop is working properly. Prints dictionary of stats for each day that needs to be updated.
		days_back_stats = client.get_stats(days_back.isoformat()) #Note that date MUST BE in isoformat datetime object
		xday_stats(days_back_stats) #Append initialized list of calories_burned_list. Use isoformat datetime object in bmr_vs_total function
		print(calories_burned_list) #Debugging to see if list is getting populated after every day of updating
		n = n - 1
		if n == 1:
			break
	df = pd.DataFrame(calories_burned_list, columns=['Burned (Garmin - Calories Burned)']) #Generate dataframe from calories_burned_list
	df3 = df2.append(df, ignore_index=True) #generate cumulative df3 that will append df to df2
	wks.set_dataframe(df3,(1,5)) #wks.set_dataframe(df3,(1,5))

update_calories_burned_up_to_yesterday(x_days_back)
