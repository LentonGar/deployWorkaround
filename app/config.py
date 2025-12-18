# Loads .env variables


import os
from dotenv import load_dotenv

# load .env file when this module is imported
load_dotenv()

class Config:
    """
    Configuration for the application. 
    Anything about model parameters is set and changed here.
    """

    # Get API key - try Streamlit secrets first, fall back to .env
    try:
        import streamlit as st
        OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
    except:
        OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    # Set model

    MODEL_NAME = "gpt-4.1-mini"

    @classmethod
    def validate(cls):
        '''
        Checks essential config is present
        '''
        if not cls.OPENAI_API_KEY:
            raise ValueError(
                "ERROR: OPENAI_API_KEY not found"
                "Make sure .env file is there and has the key!"
            )

Config.validate()
    