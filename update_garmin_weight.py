import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
import garth
from garminconnect import Garmin
import traceback
import pygsheets
from pint import UnitRegistry
import pandas as pd

# Load environment variables from .env file
load_dotenv()

# Garmin setup
GARTH_HOME = os.getenv("GARTH_HOME", "~/.garth")

# Google Sheets setup
SPREADSHEET_NAME = os.getenv('GOOGLE_SHEETS_NAME', 'CICO_Spreadsheet_Automated')
CREDENTIALS_FILE = os.getenv('GOOGLE_SHEETS_CREDENTIALS_FILE')

# Test mode flag - no actual updates will be made when True
TEST_MODE = False  # Set to False for actual updates

ureg = UnitRegistry()

def lbs_to_kg(lbs):
    """Convert pounds to kilograms using pint for maximum precision."""
    return (lbs * ureg.pound).to(ureg.kilogram).magnitude

def get_garmin_client():
    """Initialize Garmin Connect client with token-based authentication."""
    if TEST_MODE:
        print("Running in TEST MODE - No actual Garmin connection will be made")
        return None
        
    email = os.getenv('GARMIN_EMAIL')
    password = os.getenv('GARMIN_PASSWORD')
    if not email or not password:
        raise ValueError("Please set GARMIN_EMAIL and GARMIN_PASSWORD environment variables")
    
    # Initialize Garmin client
    client = Garmin(email, password)
    
    # Try to login using stored tokens
    try:
        client.login(GARTH_HOME)
        print("Successfully authenticated using stored tokens!")
    except Exception as e:
        print(f"Could not resume session: {e}")
        # Login with credentials and save tokens
        client.login()
        client.garth.dump(GARTH_HOME)
        print("Successfully authenticated with credentials and saved tokens!")
    
    return client

def get_google_sheets_service():
    """Initialize and return Google Sheets service."""
    try:
        gc = pygsheets.authorize(service_file=CREDENTIALS_FILE)
        return gc
    except Exception as e:
        print(f"Error setting up Google Sheets service: {e}")
        raise

def update_weight(client, weight_lbs, date=None):
    """
    Update weight in Garmin Connect.
    
    Args:
        client: Garmin Connect client instance
        weight_lbs: Weight in pounds (float)
        date: Optional date string in YYYY-MM-DD format. Defaults to today.
    """
    try:
        if date is None:
            dt = datetime.now()
        else:
            try:
                dt = datetime.strptime(date, '%Y-%m-%d')
            except ValueError:
                raise ValueError("Date must be in YYYY-MM-DD format")
        
        # Validate weight
        if not isinstance(weight_lbs, (int, float)) or weight_lbs <= 0:
            raise ValueError("Weight must be a positive number")
        
        # Convert pounds to kilograms using pint for maximum precision
        weight_kg = lbs_to_kg(weight_lbs)
        timestamp = dt.isoformat()
        
        # Check if a weigh-in already exists for the specified date
        if not TEST_MODE and client is not None:
            existing_weigh_ins = client.get_daily_weigh_ins(dt.strftime('%Y-%m-%d'))
            if existing_weigh_ins.get("dateWeightList", []):
                print(f"A weigh-in already exists for {dt.date()}. Skipping update.")
                return None
        
        if TEST_MODE:
            print(f"\n=== TEST MODE ===")
            print(f"Would update weight to {weight_lbs} lbs ({weight_kg} kg) for {dt.date()}")
            print(f"API call would be: client.add_weigh_in(weight={weight_kg}, unitKey='kg', timestamp='{timestamp}')")
            return {"status": "test_success"}
        
        # Debug print: show exactly what will be sent
        print(f"[DEBUG] Sending to Garmin: weight={weight_kg}, unitKey='kg', timestamp='{timestamp}'")
        
        # Update weight using Garmin Connect API
        response = client.add_weigh_in(
            weight=weight_kg,
            unitKey="kg",
            timestamp=timestamp
        )
        
        print(f"Successfully updated weight to {weight_lbs} lbs ({weight_kg} kg) for {dt.date()}")
        return response
    
    except Exception as e:
        print(f"Error updating weight: {e}")
        print(traceback.format_exc())
        return None

def sync_weights_from_sheet():
    """Sync weights from Google Sheet to Garmin Connect."""
    try:
        print("\n=== RUNNING IN TEST MODE - NO ACTUAL UPDATES WILL BE MADE ===" if TEST_MODE else "")
        
        # Initialize Garmin client
        client = get_garmin_client()
        
        # Initialize Google Sheets service
        sheets_service = get_google_sheets_service()
        
        # Open the spreadsheet and get the first sheet
        sh = sheets_service.open(SPREADSHEET_NAME)
        wks = sh[0]
        
        # Get the last 30 days of data
        today = datetime.now()
        dates_to_check = [(today - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(30)]
        
        # Get all existing weigh-ins for the date range
        existing_weigh_ins = set()
        if not TEST_MODE and client is not None:
            for date in dates_to_check:
                try:
                    weigh_ins = client.get_daily_weigh_ins(date)
                    if weigh_ins.get("dateWeightList", []):
                        existing_weigh_ins.add(date)
                except Exception as e:
                    print(f"Error checking weigh-ins for {date}: {e}")
        
        print(f"Found {len(existing_weigh_ins)} existing weigh-ins in Garmin Connect")
        
        # Get all data from the sheet at once
        df = wks.get_as_df(has_header=True, start=(1,1), end=(wks.rows,5))
        df['Date'] = pd.to_datetime(df['Date'])
        
        # Process each date
        for date in dates_to_check:
            # Skip if weight already exists in Garmin
            if date in existing_weigh_ins:
                print(f"Skipping {date} - weight already exists in Garmin Connect")
                continue
            
            # Get the row for this date
            date_row = df[df['Date'] == pd.to_datetime(date)]
            
            if len(date_row) == 0:
                print(f"No data found for {date}")
                continue
            
            # Get weight from column D (4th column)
            weight = date_row.iloc[0, 3]  # 0-based index, so column D is index 3
            
            # Skip if weight is empty or not a number
            if pd.isna(weight) or not isinstance(weight, (int, float)):
                print(f"No valid weight found for {date}")
                continue
            
            print(f"\nProcessing weight for {date}: {weight} lbs")
            update_weight(client, weight, date)
            
    except Exception as e:
        print(f"An error occurred: {e}")
        print(traceback.format_exc())

def main():
    """Main function to update weight in Garmin Connect."""
    try:
        # Ask user if they want to sync from sheet or enter weight manually
        choice = input("Do you want to sync weights from Google Sheet? (y/n): ").strip().lower()
        
        if choice == 'y':
            sync_weights_from_sheet()
        else:
            # Get weight in pounds
            while True:
                try:
                    weight_lbs = float(input("Enter your weight in pounds: "))
                    if weight_lbs <= 0:
                        print("Please enter a positive number.")
                        continue
                    break
                except ValueError:
                    print("Please enter a valid number.")
            
            # Get date
            date = input("Enter date (YYYY-MM-DD) or press Enter for today: ").strip()
            if not date:
                date = None
            
            # Initialize Garmin client
            client = get_garmin_client()
            
            # Update weight
            update_weight(client, weight_lbs, date)
        
    except Exception as e:
        print(f"An error occurred: {e}")
        print(traceback.format_exc())

if __name__ == "__main__":
    main() 