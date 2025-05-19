import os
import json
from pathlib import Path
import garth
from dotenv import load_dotenv

def get_stored_credentials(token_dir=".garth"):
    """Get stored credentials from the token directory."""
    token_path = Path(token_dir).expanduser()
    if not token_path.exists():
        return None
    
    try:
        with open(token_path / "token.json", "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None

def save_credentials(token_data, token_dir=".garth"):
    """Save credentials to the token directory."""
    token_path = Path(token_dir).expanduser()
    token_path.mkdir(parents=True, exist_ok=True)
    
    with open(token_path / "token.json", "w") as f:
        json.dump(token_data, f)

def handle_mfa_request():
    """Handle MFA code input from user."""
    print("\nMFA authentication required!")
    print("Please check your email/phone for the MFA code.")
    while True:
        mfa_code = input("Enter your MFA code: ").strip()
        if mfa_code:
            return mfa_code
        print("MFA code cannot be empty. Please try again.")

def get_garmin_client(token_dir=".garth"):
    """Initialize Garmin Connect client with token-based authentication."""
    load_dotenv()
    
    # First try to use stored tokens
    try:
        garth.resume(token_dir)
        print("Successfully authenticated using stored tokens!")
        return garth
    except Exception as e:
        print(f"Could not resume session: {e}")
    
    # If no tokens or tokens are invalid, authenticate with email/password
    email = os.getenv("GARMIN_EMAIL")
    password = os.getenv("GARMIN_PASSWORD")
    
    if not email or not password:
        raise ValueError("Please provide GARMIN_EMAIL and GARMIN_PASSWORD in your .env file")
    
    try:
        # Login with MFA handling
        garth.login(email, password)
        print("Successfully authenticated with credentials!")
        
        # Save the tokens for future use
        garth.save(token_dir)
        
        return garth
    except Exception as err:
        print(f"Error occurred during Garmin Connect Client authentication: {err}")
        raise 