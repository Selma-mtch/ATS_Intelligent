import os
from dotenv import load_dotenv

load_dotenv(override=True)

SECRET_KEY = os.getenv("SECRET_KEY", "change-me")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///ats_intelligent.db")
RECRUITER_COMPANY_CODE = os.getenv("RECRUITER_COMPANY_CODE", "RH_CODE_DEMO")
PORT = int(os.getenv("PORT", "5001"))
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "false").lower() == "true"
UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "uploads")
MAX_CV_SIZE_MB = int(os.getenv("MAX_CV_SIZE_MB", "5"))
