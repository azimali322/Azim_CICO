from garminconnect import (
    Garmin,
    GarminConnectConnectionError,
    GarminConnectTooManyRequestsError,
    GarminConnectAuthenticationError,
)
from datetime import date, timedelta

import pandas as pd


today = date.today()
yesterday = today - timedelta(days=1)

client = Garmin('azimali322@gmail.com', 'Saf!994Fan')
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

#n=44 days ago


