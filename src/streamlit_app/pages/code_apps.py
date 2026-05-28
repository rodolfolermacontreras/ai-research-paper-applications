"""Code applications page -- browse generated code from paper ideas."""
from __future__ import annotations

from pathlib import Path

import streamlit as st

from streamlit_app.utils import (
    CODE_APPLICATIONS_DIR,
    LANGUAGE_BY_SUFFIX,
    get_code_application_directories,
)


def render() -> None:
    st.header("Code Applications")

    app_dirs = get_code_application_directories()

    if not app_dirs:
        st.info(
            "No code applications yet. Once papers are analyzed, practical "
            "code implementations will appear here."
        )
        return

    st.write(f"**{len(app_dirs)}** application(s)")

    for app_dir in app_dirs:
        with st.expander(app_dir.name, expanded=False):
            readme = app_dir / "README.md"
            if readme.exists():
                st.markdown(readme.read_text(encoding="utf-8"))
                st.markdown("---")

            code_files = sorted(
                f for f in app_dir.rglob("*")
                if f.is_file() and f.suffix in LANGUAGE_BY_SUFFIX and f.name.lower() != "readme.md"
            )

            if code_files:
                st.write(f"{len(code_files)} source file(s)")
                for cf in code_files:
                    rel = cf.relative_to(app_dir)
                    lang = LANGUAGE_BY_SUFFIX.get(cf.suffix.lower(), "text")
                    with st.expander(str(rel)):
                        st.code(cf.read_text(encoding="utf-8"), language=lang)
            else:
                st.caption("No source files found in this application directory.")
