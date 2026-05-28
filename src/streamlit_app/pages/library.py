"""Library page -- lists all papers with metadata and analysis status."""
from __future__ import annotations

import streamlit as st

from streamlit_app.utils import (
    format_file_size,
    get_all_paper_metadata,
)


def render() -> None:
    st.header("Paper Library")

    papers = get_all_paper_metadata()

    if not papers:
        st.info("No papers found. Upload a PDF on the **Upload Paper** page or drop files into the `Papers/` folder.")
        return

    st.write(f"**{len(papers)}** paper(s) in library")
    st.markdown("---")

    for paper in papers:
        col1, col2, col3 = st.columns([5, 2, 2])
        with col1:
            st.markdown(f"**{paper.name}**")
        with col2:
            st.caption(f"{paper.page_count} pages | {format_file_size(paper.size_bytes)}")
        with col3:
            status_label = "Analyzed" if paper.analyzed else "Pending"
            if st.button(f"View {status_label}", key=f"view_{paper.name}"):
                st.session_state["selected_paper"] = paper.name
                st.session_state["current_page"] = "Paper Detail"
                st.rerun()
        st.markdown("---")
