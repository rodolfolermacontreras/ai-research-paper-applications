"""Upload page -- allows users to upload PDFs and trigger extraction."""
from __future__ import annotations

import shutil
from pathlib import Path

import streamlit as st

from streamlit_app.utils import (
    PAPERS_DIR,
    ensure_directories,
    get_paper_metadata,
)


def render() -> None:
    st.header("Upload a Research Paper")

    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=["pdf"],
        help="Upload a research paper in PDF format.",
    )

    if uploaded_file is not None:
        dest = PAPERS_DIR / uploaded_file.name
        if dest.exists():
            st.warning(f"A paper named **{uploaded_file.name}** already exists in the library.")
        else:
            with open(dest, "wb") as fh:
                fh.write(uploaded_file.getbuffer())
            st.success(f"Uploaded **{uploaded_file.name}** successfully.")

        if st.button("Analyze this paper now"):
            _run_analysis(dest)

    st.markdown("---")
    st.subheader("Bulk upload")
    st.info(
        "You can also drop PDF files directly into the `Papers/` folder "
        "on disk and they will appear in the library automatically."
    )


def _run_analysis(paper_path: Path) -> None:
    import sys, os

    src_dir = Path(__file__).resolve().parents[2]
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))

    from extraction.pipeline import run_pipeline
    from streamlit_app.utils import OUTPUT_DIR

    with st.spinner(f"Analyzing {paper_path.name} ..."):
        try:
            result = run_pipeline(str(paper_path), str(OUTPUT_DIR))
            st.success(
                f"Analysis complete: {len(result.sections)} sections, "
                f"{len(result.figures)} figures, {len(result.tables)} tables, "
                f"{len(result.code_blocks)} code blocks, {len(result.references)} references."
            )
        except Exception as exc:
            st.error(f"Analysis failed: {exc}")
