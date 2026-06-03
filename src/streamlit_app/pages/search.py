"""Search page -- full-text search across papers, sections, and summaries."""

from __future__ import annotations

import json
import re
from pathlib import Path

import streamlit as st

from streamlit_app.utils import (
    OUTPUT_DIR,
    get_all_paper_ids,
    load_analysis_result,
)


def render() -> None:
    st.header("Search Research Papers")
    
    query = st.text_input(
        "Search query",
        placeholder="Enter keywords to search across papers...",
        help="Search in titles, abstracts, sections, figures, tables, code, and references.",
    )
    
    if not query or len(query.strip()) < 2:
        st.info("Enter at least 2 characters to search.")
        return
    
    search_options = st.columns(4)
    with search_options[0]:
        search_titles = st.checkbox("Titles", value=True)
    with search_options[1]:
        search_abstracts = st.checkbox("Abstracts", value=True)
    with search_options[2]:
        search_sections = st.checkbox("Sections", value=True)
    with search_options[3]:
        search_refs = st.checkbox("References", value=False)
    
    with st.spinner("Searching..."):
        results = _search_papers(
            query.strip(),
            search_titles=search_titles,
            search_abstracts=search_abstracts,
            search_sections=search_sections,
            search_refs=search_refs,
        )
    
    if not results:
        st.warning("No results found.")
        return
    
    st.success(f"Found {len(results)} matching papers.")
    
    for result in results:
        with st.expander(f"**{result['title']}** ({result['score']} matches)", expanded=False):
            if result.get("metadata"):
                meta = result["metadata"]
                st.markdown(f"**Authors:** {', '.join(meta.get('authors', [])[:3])}")
            
            for match in result["matches"][:5]:
                st.markdown(f"- **{match['source']}:** {match['snippet']}")
            
            if len(result["matches"]) > 5:
                st.caption(f"... and {len(result['matches']) - 5} more matches")


def _search_papers(
    query: str,
    search_titles: bool = True,
    search_abstracts: bool = True,
    search_sections: bool = True,
    search_refs: bool = False,
) -> list[dict]:
    """Search across all papers and return matching results."""
    
    query_lower = query.lower()
    all_results: list[dict] = []
    
    for paper_id in get_all_paper_ids():
        analysis = load_analysis_result(paper_id)
        if not analysis:
            continue
        
        matches: list[dict] = []
        
        # Search title
        if search_titles and analysis.get("metadata", {}).get("title"):
            title = analysis["metadata"]["title"]
            if query_lower in title.lower():
                matches.append({
                    "source": "Title",
                    "snippet": _highlight(title, query),
                })
        
        # Search abstract
        if search_abstracts and analysis.get("abstract"):
            abstract = analysis["abstract"]
            if query_lower in abstract.lower():
                matches.append({
                    "source": "Abstract",
                    "snippet": _extract_snippet(abstract, query),
                })
        
        # Search sections
        if search_sections:
            for section in analysis.get("sections", []):
                title_match = query_lower in section["title"].lower()
                content_match = query_lower in section["content"].lower()
                
                if title_match:
                    matches.append({
                        "source": f"Section: {section['title']}",
                        "snippet": _highlight(section["title"], query),
                    })
                elif content_match:
                    matches.append({
                        "source": f"Section: {section['title']}",
                        "snippet": _extract_snippet(section["content"], query),
                    })
        
        # Search references
        if search_refs:
            for ref in analysis.get("references", []):
                if query_lower in ref["raw_text"].lower():
                    matches.append({
                        "source": "Reference",
                        "snippet": _extract_snippet(ref["raw_text"], query, max_len=150),
                    })
        
        if matches:
            all_results.append({
                "paper_id": paper_id,
                "title": analysis.get("metadata", {}).get("title", paper_id),
                "metadata": analysis.get("metadata", {}),
                "score": len(matches),
                "matches": matches,
            })
    
    return sorted(all_results, key=lambda r: r["score"], reverse=True)


def _extract_snippet(text: str, query: str, max_len: int = 200) -> str:
    """Extract a snippet around the query match with context."""
    
    query_lower = query.lower()
    text_lower = text.lower()
    idx = text_lower.find(query_lower)
    
    if idx == -1:
        return text[:max_len] + "..."
    
    start = max(0, idx - max_len // 2)
    end = min(len(text), idx + len(query) + max_len // 2)
    snippet = text[start:end]
    
    if start > 0:
        snippet = "..." + snippet
    if end < len(text):
        snippet = snippet + "..."
    
    return _highlight(snippet, query)


def _highlight(text: str, query: str) -> str:
    """Highlight the query term in the text."""
    
    pattern = re.compile(re.escape(query), re.IGNORECASE)
    return pattern.sub(lambda m: f"**{m.group(0)}**", text)
