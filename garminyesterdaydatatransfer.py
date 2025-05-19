from garminconnect import (
    Garmin,
    GarminConnectConnectionError,
    GarminConnectTooManyRequestsError,
    GarminConnectAuthenticationError,
)
from datetime import date, timedelta
import pygsheets
import pandas as pd
import numpy as np
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

today = date.today()
yesterday = today - timedelta(days=1)

# Get credentials from environment variables
email = os.getenv('GARMIN_EMAIL')
password = os.getenv('GARMIN_PASSWORD')
if not email or not password:
    raise ValueError("Please set GARMIN_EMAIL and GARMIN_PASSWORD environment variables")

client = Garmin(email, password)
client.login()

print(yesterday)

print(client.get_full_name())

print(client.get_stats(yesterday.isoformat())) #Note that date MUST BE in isoformat

yesterdaystats = client.get_stats(yesterday.isoformat())

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

print(bmr_vs_total(yesterdaystats))

calories_burned_list = []

def yday_stats(day_of_stats):
	calories_burned_list.append(bmr_vs_total(day_of_stats))

yday_stats(yesterdaystats)

print(calories_burned_list)

df = pd.DataFrame(calories_burned_list, columns=['Burned (Garmin - Calories Burned)'])

print(df.head())

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

#update the first sheet with df, starting at cell B2. Note for df in GSheets: [row,column] 
df2 = wks.get_as_df(has_header=True, start=(1,5), end=(607,5), index_column=None, numerize=True,empty_value='', include_tailing_empty=False, include_tailing_empty_rows=False)

df3 = df2.append(df, ignore_index=True)

wks.set_dataframe(df3,(1,5))

#index = df2['Burned (Garmin - Calories Burned)'].index[df2['Burned (Garmin - Calories Burned)'].apply(np.isnan)]
#set_index_value = int(index[0])

#print(set_index_value)

#wks.set_dataframe(df,(1,set_index_value))