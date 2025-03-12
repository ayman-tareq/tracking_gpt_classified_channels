from datetime import datetime, timedelta, timezone
from pymongo import MongoClient, UpdateOne
from dotenv import load_dotenv
import pandas as pd
import os

def get_secondary_mongoDB_connection():
    load_dotenv()
    MONGODB_URI = os.environ.get('Secondary_MONGODB_URI')
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
        df.sort_values(['created_at', 'is_bad_channel', 'marked_as_bad_by_gpt', 'title'], inplace=True)
    except Exception as e:
        print('Error: Unable to fetch visited-channels data.', e)
    finally:
        return df
