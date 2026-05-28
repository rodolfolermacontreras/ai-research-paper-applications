"""Paper detail page -- tabbed view of extraction results for a single paper."""
from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

from streamlit_app.utils import (
    OUTPUT_DIR,
    get_paper_path,
    load_analysis_results,
    format_file_size,
)


def render() -> None:
    paper_name = st.session_state.get("selected_paper")
    if not paper_name:
        st.info("Select a paper from the **Paper Library** first.")
        return

    paper_path = get_paper_path(paper_name)
    if paper_path is None:
        st.error(f"Paper file not found: {paper_name}")
        return

    st.header(paper_name)

    if st.button("Back to Library"):
        st.session_state["current_page"] = "Paper Library"
        st.rerun()

    results = load_analysis_results(paper_path)

    tabs = st.tabs(["Summary", "Sections", "Figures", "Tables", "Code", "References"])

    with tabs[0]:
        _render_summary(results.summary)

    with tabs[1]:
        _render_sections(results.sections)

    with tabs[2]:
        _render_figures(results.figures)

    with tabs[3]:
        _render_tables(results.tables)

    with tabs[4]:
        _render_code(results.code_readme, results.code_files)

    with tabs[5]:
        _render_references(results.references)


def _render_summary(summary: str | None) -> None:
    if summary:
        st.markdown(summary)
    else:
        st.info("No summary available yet. Run analysis from the Upload page.")


def _render_sections(sections: list) -> None:
    if not sections:
        st.info("No sections extracted.")
        return
    st.write(f"**{len(sections)}** section(s)")
    for title, content in sections:
        with st.expander(title):
            st.markdown(content[:3000])
            if len(content) > 3000:
                st.caption("(truncated)")


def _render_figures(figures: list) -> None:
    if not figures:
        st.info("No figures extracted.")
        return
    st.write(f"**{len(figures)}** figure(s)")
    cols = st.columns(3)
    for idx, fig_path in enumerate(figures):
        with cols[idx % 3]:
            try:
                st.image(str(fig_path), caption=fig_path.name, use_container_width=True)
            except Exception:
                st.caption(f"Could not display: {fig_path.name}")


def _render_tables(tables: list) -> None:
    if not tables:
        st.info("No tables extracted.")
        return
    st.write(f"**{len(tables)}** table(s)")
    for table_result in tables[:30]:
        with st.expander(table_result.name):
            st.dataframe(table_result.data, use_container_width=True)


def _render_code(readme: str | None, code_files: list) -> None:
    if readme:
        st.markdown(readme)
    if not code_files:
        st.info("No code applications generated yet.")
        return
    st.write(f"**{len(code_files)}** code file(s)")
    for code_file in code_files:
        with st.expander(str(code_file.path.name)):
            st.code(code_file.content, language=code_file.language)


def _render_references(references: list) -> None:
    if not references:
        st.info("No references extracted.")
        return
    st.write(f"**{len(references)}** reference(s)")
    for ref in references:
        st.markdown(f"- {ref}")
