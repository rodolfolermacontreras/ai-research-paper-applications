from __future__ import annotations

import sys
from pathlib import Path
from typing import Callable

import streamlit as st

SRC_DIR = Path(__file__).resolve().parent.parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from streamlit_app.pages import code_apps, library, paper_detail, search, upload, wiki
from streamlit_app.utils import ensure_directories

PageRenderer = Callable[[], None]
PAGES: dict[str, PageRenderer] = {
    "Upload Paper": upload.render,
    "Paper Library": library.render,
    "Search": search.render,
    "Paper Detail": paper_detail.render,
    "Wiki / Knowledge Base": wiki.render,
    "Code Applications": code_apps.render,
}


def initialize_state() -> None:
    st.session_state.setdefault("current_page", "Paper Library")
    st.session_state.setdefault("selected_paper", None)


def inject_styles() -> None:
    st.markdown(
        """
        <style>
            .app-title {
                font-size: 2.2rem;
                font-weight: 700;
                margin-bottom: 0.25rem;
            }
            .app-subtitle {
                color: #4b5563;
                margin-bottom: 1.25rem;
            }
            .status-pill {
                display: inline-block;
                padding: 0.2rem 0.6rem;
                border-radius: 999px;
                font-size: 0.85rem;
                font-weight: 600;
                margin-bottom: 0.5rem;
                background-color: #e5eefc;
                color: #1d4ed8;
            }
            .status-pill.pending {
                background-color: #f3f4f6;
                color: #374151;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar() -> None:
    st.sidebar.title("AI Research Paper Library")
    st.sidebar.caption("Explore uploaded papers, extracted insights, and generated code assets.")

    current_page = st.session_state.get("current_page", "Paper Library")
    options = list(PAGES.keys())
    selected_index = options.index(current_page) if current_page in options else 0

    st.session_state["current_page"] = st.sidebar.radio(
        "Navigation",
        options=options,
        index=selected_index,
    )

    selected_paper = st.session_state.get("selected_paper")
    if selected_paper:
        st.sidebar.markdown("---")
        st.sidebar.write("Current paper")
        st.sidebar.info(selected_paper)


def main() -> None:
    st.set_page_config(page_title="AI Research Paper Library", layout="wide")
    ensure_directories()
    initialize_state()
    inject_styles()
    render_sidebar()

    st.markdown('<div class="app-title">AI Research Paper Library</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="app-subtitle">A Streamlit workspace for uploading, reviewing, and exploring AI research papers.</div>',
        unsafe_allow_html=True,
    )

    page_name = st.session_state.get("current_page", "Paper Library")
    page_renderer = PAGES.get(page_name, library.render)
    page_renderer()


if __name__ == "__main__":
    main()
