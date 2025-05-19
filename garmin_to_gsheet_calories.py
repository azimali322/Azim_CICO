import os
from datetime import datetime, timedelta
import pandas as pd
import pygsheets
from dotenv import load_dotenv
import traceback
from garminconnect import Garmin
import garth
import time

# Load environment variables from .env file
load_dotenv()

# Google Sheets setup
SPREADSHEET_NAME = os.getenv('GOOGLE_SHEETS_NAME', 'CICO_Spreadsheet_Automated')
CREDENTIALS_FILE = os.getenv('GOOGLE_SHEETS_CREDENTIALS_FILE')
TOKEN_DIR = ".garth_tokens"

# Test mode flag - no actual updates will be made when True
TEST_MODE = False

def get_google_sheets_service():
    """Initialize and return Google Sheets service."""
    try:
        gc = pygsheets.authorize(service_file=CREDENTIALS_FILE)
        return gc
    except Exception as e:
        print(f"Error setting up Google Sheets service: {e}")
        raise

def get_garmin_client():
    """Initialize Garmin Connect client with token-based authentication."""
    email = os.getenv('GARMIN_EMAIL')
    password = os.getenv('GARMIN_PASSWORD')
    if not email or not password:
        raise ValueError("Please set GARMIN_EMAIL and GARMIN_PASSWORD environment variables")
    client = Garmin(email, password)
    # Try to load tokens
    try:
        garth.resume(TOKEN_DIR)
        print("Successfully authenticated using stored tokens!")
    except Exception as e:
        print(f"Could not resume session: {e}")
        client.login()
        garth.save(TOKEN_DIR)
        print("Successfully authenticated with credentials and saved tokens!")
    return client

def get_calories_data(client, date):
    """Get calories data from Garmin Connect for a specific date."""
    try:
        # Validate date format (YYYY-MM-DD)
        try:
            datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format")
        
        # Get daily summary data using get_stats method
        summary = client.get_stats(date)
        
        # Extract relevant calorie data
        calories_data = {
            'date': date,
            'bmr_calories': summary.get('bmrKilocalories', 0),
            'total_calories': summary.get('totalKilocalories', 0),
            'active_calories': summary.get('activeKilocalories', 0)
        }
        
        return calories_data
    except Exception as e:
        print(f"Error getting calories data for {date}: {e}")
        return None

def update_google_sheet(gc, data):
    """Update Google Sheet with the provided data."""
    try:
        # Open the spreadsheet and get the first sheet
        sh = gc.open(SPREADSHEET_NAME)
        wks = sh[0]
        
        # Get existing data - dynamically determine the number of rows
        total_rows = wks.rows
        df = wks.get_as_df(has_header=True, start=(1,1), end=(total_rows,5), index_column=None, numerize=True, empty_value='', include_tailing_empty=False, include_tailing_empty_rows=False)
        
        # Convert date to datetime for comparison
        garmin_date = pd.to_datetime(data['date'])
        df['Date'] = pd.to_datetime(df['Date'])
        
        # Find the row where the date matches the Garmin data date
        date_row = df[df['Date'] == garmin_date].index
        if len(date_row) == 0:
            print(f"No matching date found for {data['date']}")
            return
        
        # Update column E (5th column) for the matching row
        row_index = date_row[0] + 1  # +1 because Google Sheets is 1-indexed
        wks.update_value((row_index, 5), data['total_calories'])
        
        print(f"Sheet updated successfully for date {data['date']}")
    except Exception as e:
        print(f"Error updating Google Sheet: {e}")
        raise

def main():
    """Main function to sync Garmin calories data to Google Sheets."""
    try:
        print("\n=== RUNNING IN TEST MODE - NO ACTUAL UPDATES WILL BE MADE ===" if TEST_MODE else "")
        
        # Initialize Garmin client using token-based authentication
        client = get_garmin_client()
        
        # Initialize Google Sheets service
        sheets_service = get_google_sheets_service()
        
        # Get the last 30 days of data, starting from the day before today
        today = datetime.now()
        for i in range(1, 31):  # Start from 1 to get the day before today
            date = (today - timedelta(days=i)).strftime('%Y-%m-%d')
            print(f"Fetching data for: {date}")
            
            # Get calories data
            calories_data = get_calories_data(client, date)
            
            if calories_data:
                # Update Google Sheet
                update_google_sheet(sheets_service, calories_data)
            else:
                print(f"No calories data available for {date}")
            
    except Exception as e:
        print(f"An error occurred: {e}")
        print(traceback.format_exc())

if __name__ == "__main__":
    main() 