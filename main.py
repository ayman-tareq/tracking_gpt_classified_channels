import math
import streamlit as st
import pandas as pd
from manage_mogodb import get_all_gpt_classified_channels

PAGE_SIZE = 20  # Show 20 records per page

# If Streamlit < 1.18, use @st.cache or @st.experimental_memo
@st.cache_data(ttl=60)  
def load_data():
    """Fetch the DataFrame. Create an extra 'channel_link' column if 'channel_url' exists."""
    df = get_all_gpt_classified_channels()
    
    # If channel_url exists, add a clickable link column
    if 'channel_url' in df.columns:
        df['channel_link'] = df['channel_url'].apply(
            lambda url: f'<a href="{url}" target="_blank">Open Channel</a>' if pd.notna(url) else ''
        )

    return df  # Return all columns unmodified (plus 'channel_link' if it exists)

def main():
    st.set_page_config(page_title="GPT Classified Channels", layout="wide")

    # Auto‐refresh once per minute via JavaScript
    st.markdown(
        """
        <script>
          setTimeout(function() {
              window.location.reload();
          }, 60 * 1000); // 60 seconds
        </script>
        """,
        unsafe_allow_html=True
    )

    st.title("GPT Classified Channels")

    # Load (cached) data
    df_display = load_data()

    # 1) Sort by `created_at` descending, if present
    if 'created_at' in df_display.columns:
        df_display = df_display.sort_values('created_at', ascending=False)

    # 2) Filtering
    # Filter by is_faceless
    if 'is_faceless' in df_display.columns:
        faceless_filter = st.selectbox("Filter by is_faceless", ["All", "True", "False"])
        if faceless_filter != "All":
            # Compare bool column with True/False
            df_display = df_display[df_display['is_faceless'] == (faceless_filter == "True")]

    # Filter by is_bad_channel
    if 'is_bad_channel' in df_display.columns:
        bad_channel_filter = st.selectbox("Filter by is_bad_channel", ["All", "True", "False"])
        if bad_channel_filter != "All":
            df_display = df_display[df_display['is_bad_channel'] == (bad_channel_filter == "True")]

    # 3) Pagination
    if "current_page" not in st.session_state:
        st.session_state.current_page = 0

    total_records = len(df_display)
    total_pages = math.ceil(total_records / PAGE_SIZE)

    # Pagination controls
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

    # Slice the DataFrame for the current page
    start_idx = st.session_state.current_page * PAGE_SIZE
    end_idx = start_idx + PAGE_SIZE
    df_page = df_display.iloc[start_idx:end_idx]

    # 4) Display as HTML, preserving clickable links
    st.markdown(
        df_page.to_html(escape=False, index=False),
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
