import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a-very-secret-key'
    # Builder Store specific configurations
    STORE_NAME = os.environ.get('STORE_NAME') or 'AI Department Store'
    API_VERSION = os.environ.get('API_VERSION') or 'v1'
    # Add other configuration variables here
