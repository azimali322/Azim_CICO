import pygsheets
import pandas as pd

#authorization
creds_file = '/Users/azima/Desktop/Python_Fun_Scripts/Azim_CICO/cico-python-sheets-638e5a4533f3.json'
gc = pygsheets.authorize(service_file=creds_file)
# gcdrive = pygsheets.drive.DriveAPIWrapper(http, data_path, retries=3, logger=<Logger pygsheets.drive (WARNING)>)

def are_you_sure(file):
	global new_file_name
	new_file_name = file
	confirm = input('File name will be "' + file + '". Are you sure (y or n)? \n> ')
	if confirm in ['y','Yes','yes','YES']:
		res = gc.sheet.create(file)  # Please set the new Spreadsheet name.
		createdSpreadsheet = gc.open_by_key(res['spreadsheetId'])
		createdSpreadsheet.share('azimali322@gmail.com', role='writer', type='user') # Change user email shared here.
		return print(new_file_name + ' has been created and shared.')
	elif confirm in ['n','No','no','NO']:
		return new_file_prompt()
	else:
		return are_you_sure(file)

def new_file_prompt():
	y = input('What is the file name of the new Google Sheets file? \n> ')
	are_you_sure(y)

def file_create_question():
	x = input('Do you want to create new Google Sheets file (y or n)? \n> ')
	if x in ['y','Yes','yes','YES']:
		return new_file_prompt()
	elif x in ['n','No','no','NO']:
		return existing_file_prompt()
	else:
		return file_create_question()

def get_gsheetdf_from(file_name):
	global gsheetdf
	sh = gc.open(file_name)
	wks = sh[0] #select sheet index
	gsheetdf = wks.get_as_df(has_header=False, start=(1,1), end=(10,2), index_column=None, numerize=True,empty_value='', include_tailing_empty=False, include_tailing_empty_rows=False)
	return gsheetdf

def existing_file_prompt():
	global u
	u = input('Do you know of a file name you want to access? \nType "n" if you do not know of the file name. \nMake sure to be case sensitive. \n> ')
	if u in ['n','No','no','NO']:
		return exit()
	else: #after prompt for old file wanted is given
		get_gsheetdf_from(u)
		return


print(gc.spreadsheet_titles())

# gcdrive.delete('sampleTitle1')


#run questionnaire code
# print(file_create_question())

# print(gsheetdf.head())

#after new file is created
# sh = gc.open(new_file_name)

# wks = sh[0]

# df = wks.get_as_df(has_header=True, start=(1,1), end=(10,2), index_column=None, numerize=True,empty_value='', include_tailing_empty=False, include_tailing_empty_rows=False)

# print(df.head())
