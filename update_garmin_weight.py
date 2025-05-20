import os
from datetime import datetime
from dotenv import load_dotenv
import garth
from garminconnect import Garmin
import traceback
from pint import UnitRegistry

# Load environment variables from .env file
load_dotenv()

# Garmin setup
GARTH_HOME = os.getenv("GARTH_HOME", "~/.garth")

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

def main():
    """Main function to update weight in Garmin Connect."""
    try:
        print("\n=== RUNNING IN TEST MODE - NO ACTUAL UPDATES WILL BE MADE ===" if TEST_MODE else "")
        
        # Initialize Garmin client
        client = get_garmin_client()
        
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
        
        # Update weight
        update_weight(client, weight_lbs, date)
        
    except Exception as e:
        print(f"An error occurred: {e}")
        print(traceback.format_exc())

if __name__ == "__main__":
    main() 