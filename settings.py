import os
from dotenv import load_dotenv

CURRENT_DIRECTORY = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(CURRENT_DIRECTORY, 'creds.env'))

USERNAME = os.getenv('USERNAME')
PASSWORD = os.getenv('PASSWORD')
OTP_KEY = os.getenv('OTP_KEY')
GECKODRIVER_LOCATION = os.getenv('GECKODRIVER_LOCATION')