from pyspark.sql import SparkSession
from pyspark.sql.functions import *
import os
import gspread
# from gspread import gspread_dataframe
from gspread_dataframe import set_with_dataframe # check documentation to understand this.

# initialize spark session
spark = SparkSession.builder.appName("GoogleSheetEdit").getOrCreate()

# create sample dataframe
df = spark.createDataFrame([(1, "John", 25), (2, "Jane", 30), (3, "Jim", 35)], ["id", "name", "age"])

# authenticate Google Sheets API
gc = gspread.service_account(filename=os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'))

# open a sheet
sh = gc.open("MySheet")

# select a specific worksheet
worksheet = sh.get_worksheet(0)

# clear the sheet
worksheet.clear()

# write the dataframe to the sheet
set_with_dataframe(worksheet, df)
