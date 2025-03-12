import math
import streamlit as st
from manage_mogodb import get_all_gpt_classified_channels

PAGE_SIZE = 20

@st.cache_data(ttl=60)  # or @st.cache if on older Streamlit
def load_data():
    """Fetch DataFrame, sort descending by created_at, and build a clickable URL column."""
    df = get_all_gpt_classified_channels()

    # Sort newest first
    df = df.sort_values("created_at", ascending=False)

    # Create a clickable link column
    df["channel_link"] = df["channel_url"].apply(
        lambda url: f'<a href="{url}" target="_blank">Open Channel</a>'
    )

    # Select columns to display
    df_display = df[
        [
            "title",
            "subscriber_count",
            "video_count",
            "channel_link",
            "final_category",
            "channel_language",
            "format",
            "is_bad_channel",
            "is_faceless",
            "marked_as_bad_by_gpt",
            "created_at",
        ]
    ]

    # Rename columns for clarity
    df_display = df_display.rename(
        columns={
            "title": "Title",
            "subscriber_count": "Subscribers",
            "video_count": "Videos",
            "channel_link": "Channel",
            "final_category": "Category",
            "channel_language": "Language",
            "format": "Format",
            "is_bad_channel": "Is Bad?",
            "is_faceless": "Is Faceless?",
            "marked_as_bad_by_gpt": "GPT Marked Bad?",
            "created_at": "Created At",
        }
    )

    return df_display

def main():
    # Basic page config
    st.set_page_config(page_title="GPT Classified Channels", layout="wide")

    # Auto-refresh page via JavaScript every 60 seconds
    st.markdown(
        """
        <script>
          setTimeout(function() {
              window.location.reload(1);
          }, 60 * 1000); // 60 seconds
        </script>
        """,
        unsafe_allow_html=True
    )

    st.title("GPT Classified Channels")

    # Load the data (cached)
    df_display = load_data()

    # ------------------ FILTERS ------------------
    # 'Is Faceless?' filter
    is_faceless_filter = st.selectbox(
        "Filter by 'Is Faceless?'", ["All", "True", "False"]
    )
    if is_faceless_filter != "All":
        bool_val = (is_faceless_filter == "True")
        df_display = df_display[df_display["Is Faceless?"] == bool_val]

    # 'Is Bad?' filter
    is_bad_filter = st.selectbox(
        "Filter by 'Is Bad Channel?'", ["All", "True", "False"]
    )
    if is_bad_filter != "All":
        bool_val = (is_bad_filter == "True")
        df_display = df_display[df_display["Is Bad?"] == bool_val]
    # ---------------------------------------------

    # Pagination setup
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

    # Slice data for current page
    start_idx = st.session_state.current_page * PAGE_SIZE
    end_idx = start_idx + PAGE_SIZE
    df_page = df_display.iloc[start_idx:end_idx]

    # Display as HTML table with clickable links
    st.markdown(
        df_page.to_html(escape=False, index=False),
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
