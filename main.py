import math
import streamlit as st
import pandas as pd
from manage_mogodb import get_all_gpt_classified_channels

# Constants
PAGE_SIZE = 20  # Show 20 records per page
REFRESH_INTERVAL = 60  # Refresh every 60 seconds

# Columns to display
DISPLAY_COLUMNS = [
    'title', 'channel_url', 'category', 'final_category', 'format', 
    'is_faceless', 'is_bad_channel', 'subscriber_count', 'video_count', 
    'created_at'
]

@st.cache_data(ttl=REFRESH_INTERVAL)
def load_data():
    """Fetch the DataFrame and process it."""
    df = get_all_gpt_classified_channels()

    # Create a clickable link column for 'channel_url'
    if 'channel_url' in df.columns:
        df['channel_url'] = df['channel_url'].apply(
            lambda url: f'<a href="{url}" target="_blank">Open Channel</a>' if pd.notna(url) else ''
        )

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

    # 2) If no data, show a warning and bail out
    if df_display.empty:
        st.warning("No data found. Check if your database is empty or if columns don't match.")
        return

    # 3) Sort by created_at descending to show the latest records first
    if 'created_at' in df_display.columns:
        df_display = df_display.sort_values('created_at', ascending=False)

    # 4) Filter by is_faceless if present
    if 'is_faceless' in df_display.columns:
        faceless_filter = st.selectbox("Filter by is_faceless", ["All", "True", "False"], index=0)
        if faceless_filter != "All":
            df_display = df_display[df_display["is_faceless"] == (faceless_filter == "True")]

    # 5) Filter by is_bad_channel if present
    if 'is_bad_channel' in df_display.columns:
        bad_channel_filter = st.selectbox("Filter by is_bad_channel", ["All", "True", "False"], index=0)
        if bad_channel_filter != "All":
            df_display = df_display[df_display["is_bad_channel"] == (bad_channel_filter == "True")]

    # 6) Pagination
    if "current_page" not in st.session_state:
        st.session_state.current_page = 0

    total_records = len(df_display)
    total_pages = math.ceil(total_records / PAGE_SIZE)

    cols = st.columns([1, 1, 4])
    with cols[0]:
        if st.button("Previous"):
            if st.session_state.current_page > 0:
                st.session_state.current_page -= 1

    with cols[1]:
        if st.button("Next"):
            if st.session_state.current_page < total_pages - 1:
                st.session_state.current_page += 1

    with cols[2]:
        st.markdown(
            f"**Page:** {st.session_state.current_page + 1}/{total_pages} "
            f"(Total: {total_records} records)"
        )

    start_idx = st.session_state.current_page * PAGE_SIZE
    end_idx = start_idx + PAGE_SIZE
    df_page = df_display.iloc[start_idx:end_idx]

    # 7) Display table with clickable links
    st.markdown(
        df_page.to_html(escape=False, index=False),
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()