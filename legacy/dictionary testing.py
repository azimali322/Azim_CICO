from datetime import date, timedelta

import pandas as pd

dict1 = {'userProfileId': 80512511, 'totalKilocalories': 2887.0, 'activeKilocalories': 731.0, 'bmrKilocalories': 2156.0, 'wellnessKilocalories': 2887.0, 'burnedKilocalories': None, 'consumedKilocalories': None, 'remainingKilocalories': 2887.0, 'totalSteps': 5103, 'netCalorieGoal': 1510, 'totalDistanceMeters': 4638, 'wellnessDistanceMeters': 4638, 'wellnessActiveKilocalories': 731.0, 'netRemainingKilocalories': 2241.0, 'userDailySummaryId': 80512511, 'calendarDate': '2021-01-28', 'rule': {'typeId': 4, 'typeKey': 'groups'}, 'uuid': 'a92152650d2e4218ac7f452ae5a129f6', 'dailyStepGoal': 5560, 'wellnessStartTimeGmt': '2021-01-28T06:00:00.0', 'wellnessStartTimeLocal': '2021-01-28T00:00:00.0', 'wellnessEndTimeGmt': '2021-01-29T06:00:00.0', 'wellnessEndTimeLocal': '2021-01-29T00:00:00.0', 'durationInMilliseconds': 86400000, 'wellnessDescription': None, 'highlyActiveSeconds': 1835, 'activeSeconds': 3424, 'sedentarySeconds': 58821, 'sleepingSeconds': 22320, 'includesWellnessData': True, 'includesActivityData': True, 'includesCalorieConsumedData': False, 'privacyProtected': False, 'moderateIntensityMinutes': 3, 'vigorousIntensityMinutes': 64, 'floorsAscendedInMeters': None, 'floorsDescendedInMeters': None, 'floorsAscended': None, 'floorsDescended': None, 'intensityMinutesGoal': 150, 'userFloorsAscendedGoal': 10, 'minHeartRate': 49, 'maxHeartRate': 199, 'restingHeartRate': 54, 'lastSevenDaysAvgRestingHeartRate': 54, 'source': 'GARMIN', 'averageStressLevel': 18, 'maxStressLevel': 97, 'stressDuration': 9900, 'restStressDuration': 30540, 'activityStressDuration': 6780, 'uncategorizedStressDuration': 37500, 'totalStressDuration': 84720, 'lowStressDuration': 6240, 'mediumStressDuration': 3360, 'highStressDuration': 300, 'stressPercentage': 11.69, 'restStressPercentage': 36.05, 'activityStressPercentage': 8.0, 'uncategorizedStressPercentage': 44.26, 'lowStressPercentage': 7.37, 'mediumStressPercentage': 3.97, 'highStressPercentage': 0.35, 'stressQualifier': 'UNKNOWN', 'measurableAwakeDuration': 34920, 'measurableAsleepDuration': 12300, 'lastSyncTimestampGMT': None, 'minAvgHeartRate': 51, 'maxAvgHeartRate': 196, 'bodyBatteryChargedValue': 75, 'bodyBatteryDrainedValue': 50, 'bodyBatteryHighestValue': 100, 'bodyBatteryLowestValue': 27, 'bodyBatteryMostRecentValue': 52, 'abnormalHeartRateAlertsCount': None, 'averageSpo2': 95.0, 'lowestSpo2': 86, 'latestSpo2': 96, 'latestSpo2ReadingTimeGmt': '2021-01-29T05:59:00.0', 'latestSpo2ReadingTimeLocal': '2021-01-28T23:59:00.0', 'averageMonitoringEnvironmentAltitude': None}

dict2 = {'userProfileId': 80512511, 'totalKilocalories': 2329.0, 'activeKilocalories': 663.0, 'bmrKilocalories': 1666.0, 'wellnessKilocalories': 2329.0, 'burnedKilocalories': None, 'consumedKilocalories': None, 'remainingKilocalories': 2329.0, 'totalSteps': 4315, 'netCalorieGoal': 1510, 'totalDistanceMeters': 4035, 'wellnessDistanceMeters': 4035, 'wellnessActiveKilocalories': 663.0, 'netRemainingKilocalories': 2173.0, 'userDailySummaryId': 80512511, 'calendarDate': '2021-01-28', 'rule': {'typeId': 4, 'typeKey': 'groups'}, 'uuid': 'a92152650d2e4218ac7f452ae5a129f6', 'dailyStepGoal': 5560, 'wellnessStartTimeGmt': '2021-01-28T06:00:00.0', 'wellnessStartTimeLocal': '2021-01-28T00:00:00.0', 'wellnessEndTimeGmt': '2021-01-29T00:33:00.0', 'wellnessEndTimeLocal': '2021-01-28T18:33:00.0', 'durationInMilliseconds': 66780000, 'wellnessDescription': None, 'highlyActiveSeconds': 1250, 'activeSeconds': 2224, 'sedentarySeconds': 40986, 'sleepingSeconds': 22320, 'includesWellnessData': True, 'includesActivityData': True, 'includesCalorieConsumedData': False, 'privacyProtected': False, 'moderateIntensityMinutes': 1, 'vigorousIntensityMinutes': 60, 'floorsAscendedInMeters': None, 'floorsDescendedInMeters': None, 'floorsAscended': None, 'floorsDescended': None, 'intensityMinutesGoal': 150, 'userFloorsAscendedGoal': 10, 'minHeartRate': 49, 'maxHeartRate': 199, 'restingHeartRate': 54, 'lastSevenDaysAvgRestingHeartRate': 54, 'source': 'GARMIN', 'averageStressLevel': 14, 'maxStressLevel': 79, 'stressDuration': 4920, 'restStressDuration': 29880, 'activityStressDuration': 4980, 'uncategorizedStressDuration': 25380, 'totalStressDuration': 65160, 'lowStressDuration': 2820, 'mediumStressDuration': 2040, 'highStressDuration': 60, 'stressPercentage': 7.55, 'restStressPercentage': 45.86, 'activityStressPercentage': 7.64, 'uncategorizedStressPercentage': 38.95, 'lowStressPercentage': 4.33, 'mediumStressPercentage': 3.13, 'highStressPercentage': 0.09, 'stressQualifier': 'UNKNOWN', 'measurableAwakeDuration': 27480, 'measurableAsleepDuration': 12300, 'lastSyncTimestampGMT': None, 'minAvgHeartRate': 51, 'maxAvgHeartRate': 196, 'bodyBatteryChargedValue': 74, 'bodyBatteryDrainedValue': 42, 'bodyBatteryHighestValue': 100, 'bodyBatteryLowestValue': 27, 'bodyBatteryMostRecentValue': 59, 'abnormalHeartRateAlertsCount': None, 'averageSpo2': 94.0, 'lowestSpo2': 86, 'latestSpo2': 94, 'latestSpo2ReadingTimeGmt': '2021-01-28T08:40:00.0', 'latestSpo2ReadingTimeLocal': '2021-01-28T02:40:00.0', 'averageMonitoringEnvironmentAltitude': None}

d = {}
dtest = {}

def add_element(dict, key, value):
    if key not in dict:
        dict[key] = []
    dict[key].append(value)

def add_old_dict_to_new_dict(old_dict_name):
	for key in old_dict_name:
		add_element(d,key, old_dict_name[key])
	return 

# add_element(dtest, 'userProfileId', '4')
# print(dtest)

add_old_dict_to_new_dict(dict1)
add_old_dict_to_new_dict(dict2)

df = pd.DataFrame(d)

df = df.set_index('calendarDate')

print(df.info())

df.to_excel("/Users/azima/Desktop/Python_Fun_Scripts/Azim_CICO/outputtest2.xlsx","Sheet1")