import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = 'a7fb08c548e833e5f43896aed38e68d4'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://dylanteehan:Metrics.123@dylanteehan.mysql.pythonanywhere-services.com/dylanteehan$MetricsDB'

config = Config()