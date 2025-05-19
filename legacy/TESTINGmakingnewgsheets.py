from datetime import date, timedelta, datetime
import pygsheets
import pandas as pd
import numpy as np

#authorization
creds_file = '/Users/azima/Desktop/Python_Fun_Scripts/Azim_CICO/cico-python-sheets-638e5a4533f3.json'
gc = pygsheets.authorize(service_file=creds_file)

def create_g_sheet_file(new_file_name):
	res = gc.sheet.create(new_file_name)  # Please set the new Spreadsheet name.
	createdSpreadsheet = gc.open_by_key(res['spreadsheetId'])
	createdSpreadsheet.share('azimali322@gmail.com', role='writer', type='user')

file_create_question = input('Do you want to create new Google Sheets file (y or n)? > ')

if file_create_question == 'y':
	new_file_prompt = input('What is the file name of the new Google Sheets file? > ')
	confirm = input('File name will be ' + new_file_prompt + '. Are you sure (y or n)? > ')
		if confirm == 'n':
			return new_file_prompt
		elif NOT confirm == 'n' OR 'y':
			return confirm
		else:
			print(new_file_prompt)





# file_new = 'Test_Sheet'
# create_g_sheet_file(file_new)

sh = gc.open(file_new)

wks = sh[0]

df = wks.get_as_df(has_header=True, start=(1,1), end=(607,2), index_column=None, numerize=True,empty_value='', include_tailing_empty=False, include_tailing_empty_rows=False)

print(df.head())

# sh = gc.open("my_1st_public_test_sheet")
# wks = sh.sheet1

# # Update a single cell.                                                                                                                                                                                                                                                                                                               
# wks.update_value('A1', "some value")

# sh.share('', role='reader', type='anyone')