import math
import streamlit as st
import pandas as pd
from manage_mogodb import get_all_gpt_classified_channels

# Constants
PAGE_SIZE = 20  # Show 20 records per page
REFRESH_INTERVAL = 60  # Refresh every 60 seconds

# Columns to display
DISPLAY_COLUMNS = [
    'yt_channel_id', 'title', 'subscriber_count', 'video_count', 'channel_url', 
    'final_category', 'format', 'is_faceless', 'is_bad_channel', 'created_at'
]

@st.cache_data(ttl=REFRESH_INTERVAL)
def load_data():
    """Fetch the DataFrame and process it."""
    df = get_all_gpt_classified_channels()

    # Filter to only include the required columns
    df = df[DISPLAY_COLUMNS]

    return df

def main():
    st.set_page_config(page_title="GPT Classified Channels", layout="wide")

    # Auto‐refresh once per minute
    st.markdown(
        f"""
        <script>
          setTimeout(function() {{
              window.location.reload();
          }}, {REFRESH_INTERVAL * 1000}); // {REFRESH_INTERVAL} seconds
        </script>
        """,
        unsafe_allow_html=True
    )

    st.title("GPT Classified Channels")

    # 1) Load data (cached)
    df_display = load_data()
    st.dataframe(df_display)

if __name__ == "__main__":
    main()