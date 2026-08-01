"""Application-wide constants loaded from environment variables."""

import os

from dotenv import load_dotenv

load_dotenv()

# Basics
LOCATION = os.getenv("LOCATION", "us-central1")
PROJECT_ID = os.getenv("PROJECT_ID")
LOG_FORMAT = "\n%(levelname)s: %(message)s"
IS_TESTING = bool(os.getenv("IS_TESTING"))

# Firestore Collections
USERS_COLLECTION = os.getenv("USERS_COLLECTION", "users")

# Cumplo
CUMPLO_GLOBAL_API = os.getenv("CUMPLO_GLOBAL_API", "")
CUMPLO_LOGIN_URL = os.getenv("CUMPLO_LOGIN_URL", "")
CUMPLO_BALANCE_URL = os.getenv("CUMPLO_BALANCE_URL", "")
CUMPLO_COMPANY_URL = os.getenv("CUMPLO_COMPANY_URL", "")
