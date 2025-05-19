import os
from datetime import datetime, timedelta
import pandas as pd
from garminconnect import Garmin
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Google Sheets API setup
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = os.getenv('GOOGLE_SHEETS_CREDENTIALS_FILE')  # Get from environment variable
SPREADSHEET_ID = os.getenv('GOOGLE_SHEETS_ID')  # Get from environment variable
RANGE_NAME = "'2021-2025 AZIM CICO Spreadsheet'!A:E"

# Test mode flag
TEST_MODE = True  # Set to False to actually update the sheet

def get_google_sheets_service():
    """Set up Google Sheets API service."""
    if not SERVICE_ACCOUNT_FILE:
        raise ValueError("Please set GOOGLE_SHEETS_CREDENTIALS_FILE environment variable")
    if not SPREADSHEET_ID:
        raise ValueError("Please set GOOGLE_SHEETS_ID environment variable")
    
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('sheets', 'v4', credentials=creds)
    return service

def get_garmin_client():
    """Initialize Garmin Connect client."""
    email = os.getenv('GARMIN_EMAIL')
    password = os.getenv('GARMIN_PASSWORD')
    
    if not email or not password:
        raise ValueError("Please set GARMIN_EMAIL and GARMIN_PASSWORD environment variables")
    
    client = Garmin(email, password)
    client.login()
    return client

def get_current_month_dates():
    """Get list of dates from start of current month until yesterday."""
    today = datetime.now()
    start_of_month = today.replace(day=1)
    dates = []
    current_date = start_of_month
    
    while current_date < today:
        dates.append(current_date.strftime('%Y-%m-%d'))
        current_date += timedelta(days=1)
    
    return dates

def get_calories_from_garmin(client, dates):
    """Fetch calories burned for given dates from Garmin Connect."""
    calories_data = {}
    
    print("\n=== Testing Garmin Data Fetch ===")
    for date in dates:
        try:
            # Get daily summary for the date
            stats = client.get_stats(date)
            calories_burned = stats.get('totalKilocalories', 0)
            # Format as formula
            calories_data[date] = f"={calories_burned}"
            print(f"Date: {date}, Calories Burned: {calories_burned}")
        except Exception as e:
            print(f"Error fetching data for {date}: {e}")
            calories_data[date] = None
    
    return calories_data

def update_google_sheet(service, calories_data):
    """Update Google Sheet with calories data."""
    try:
        # First, get existing data
        result = service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=RANGE_NAME
        ).execute()
        
        rows = result.get('values', [])
        updates = []
        
        print("\n=== Testing Google Sheet Updates ===")
        print("The following updates would be made:")
        
        # Process each row
        for row_idx, row in enumerate(rows):
            if len(row) >= 1:  # Make sure row has at least a date
                try:
                    # Convert date format from sheet (if needed)
                    sheet_date = datetime.strptime(row[0], '%m/%d/%Y').strftime('%Y-%m-%d')
                    
                    # If we have calories data for this date
                    if sheet_date in calories_data and calories_data[sheet_date] is not None:
                        formula = calories_data[sheet_date]
                        cell_reference = f"'2021-2025 AZIM CICO Spreadsheet'!E{row_idx + 1}"
                        
                        if TEST_MODE:
                            print(f"Would update cell {cell_reference} with value: {formula}")
                        else:
                            updates.append({
                                'range': cell_reference,
                                'values': [[formula]]
                            })
                except ValueError:
                    # Skip rows with invalid dates
                    continue
        
        # Only update if not in test mode
        if not TEST_MODE and updates:
            body = {
                'valueInputOption': 'USER_ENTERED',  # This allows formulas to be interpreted
                'data': updates
            }
            service.spreadsheets().values().batchUpdate(
                spreadsheetId=SPREADSHEET_ID,
                body=body
            ).execute()
            print(f"\nUpdated {len(updates)} rows in the spreadsheet")
        elif TEST_MODE:
            print(f"\nTest Mode: Would have updated {len(updates)} rows in the spreadsheet")
            
    except HttpError as error:
        print(f"An error occurred: {error}")

def main():
    try:
        if TEST_MODE:
            print("\n=== RUNNING IN TEST MODE - NO ACTUAL UPDATES WILL BE MADE ===\n")
        
        # Initialize services
        sheets_service = get_google_sheets_service()
        garmin_client = get_garmin_client()
        
        # Get dates to process
        dates = get_current_month_dates()
        print(f"Processing dates: {dates}")
        
        # Get calories data from Garmin
        calories_data = get_calories_from_garmin(garmin_client, dates)
        
        # Update Google Sheet
        update_google_sheet(sheets_service, calories_data)
        
        if TEST_MODE:
            print("\n=== TEST MODE COMPLETE - NO CHANGES WERE MADE TO THE SPREADSHEET ===")
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main() 