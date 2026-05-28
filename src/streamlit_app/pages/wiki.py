"""Wiki page -- knowledge base with cross-references between papers."""
from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

from streamlit_app.utils import WIKI_DIR, get_all_paper_metadata


def render() -> None:
    st.header("Wiki / Knowledge Base")

    index_path = WIKI_DIR / "index.md"
    if index_path.exists():
        st.markdown(index_path.read_text(encoding="utf-8"))
        st.markdown("---")

    wiki_files = sorted(WIKI_DIR.glob("*.md")) if WIKI_DIR.exists() else []
    wiki_files = [f for f in wiki_files if f.name != "index.md"]

    if not wiki_files:
        st.info(
            "The wiki is empty. Once papers are analyzed the wiki will be "
            "populated with cross-referenced summaries and concept pages."
        )
        return

    st.write(f"**{len(wiki_files)}** wiki page(s)")

    selected = st.selectbox("Select a wiki page", [f.stem for f in wiki_files])
    if selected:
        match = next((f for f in wiki_files if f.stem == selected), None)
        if match:
            st.markdown(match.read_text(encoding="utf-8"))
