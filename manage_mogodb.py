from datetime import datetime, timedelta, timezone
from pymongo import MongoClient
import streamlit as st
import pandas as pd


def get_secondary_mongoDB_connection():
    MONGODB_URI = st.secrets['Secondary_MONGODB_URI']
    client = MongoClient(MONGODB_URI, connectTimeoutMS=1000000, serverSelectionTimeoutMS=1000000)
    db = client['secondary-nexlev-extension']
    return db

def get_all_gpt_classified_channels(hours=24):
    """
    Retrieve unique visited channels from the last 'hours' hours.
    :param hours: Number of hours to filter the data.
    :return: Pandas DataFrame with unique visited channels and their latest visit time.
    """
    df = pd.DataFrame()
    try:
        db = get_secondary_mongoDB_connection()
        visited_channels_collection = db['gpt_classified_channels']

        # Calculate the timestamp for the given number of hours
        time_threshold = datetime.now(timezone.utc) - timedelta(hours=hours)

        print('Fetching channels...')
        result = list(visited_channels_collection.find())

        # Convert the result to a DataFrame (optional, for further analysis)
        df = pd.DataFrame(result)
        df.drop_duplicates(['yt_channel_id'], inplace=True)
        df['']
    except Exception as e:
        print('Error: Unable to fetch visited-channels data.', e)
    finally:
        return df
