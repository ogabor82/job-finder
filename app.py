import streamlit as st
import pandas as pd

from src.pipeline import run_job_finder

st.set_page_config(page_title="Startup Job Finder", layout="wide")

st.title("Startup Job Finder (MVP)")
st.caption("Tavily → company discovery → careers scrape → LLM structuring → results")

with st.sidebar:
    st.header("Search")
    default_query = '"AI startup" ("about us" OR "company" OR "who we are") -news -blog -article -wikipedia -linkedin -medium'
    query = st.text_area("Tavily query", value=default_query, height=120)

    limit_companies = st.slider("Companies to process", 5, 50, 10, step=5)
    max_llm = st.slider("Max LLM analyses", 1, 25, 5, step=1)

    run_btn = st.button("Run", type="primary")

if run_btn:
    with st.spinner("Running pipeline..."):
        rows = run_job_finder(query, limit_companies=limit_companies, max_llm=max_llm)

    st.success(f"Done. Rows: {len(rows)}")

    if not rows:
        st.warning("No results. Try a different query or increase limits.")
        st.stop()

    df = pd.DataFrame(rows)

    # quick filters
    col1, col2, col3 = st.columns(3)
    with col1:
        company_filter = st.text_input("Filter company contains", value="")
    with col2:
        title_filter = st.text_input("Filter title contains", value="")
    with col3:
        stack_filter = st.text_input("Filter tech stack contains", value="python")

    def contains(hay: str, needle: str) -> bool:
        if not needle:
            return True
        return needle.lower() in (hay or "").lower()

    filtered = []
    for r in rows:
        if not contains(r.get("company", ""), company_filter):
            continue
        if not contains(r.get("title", "") or "", title_filter):
            continue
        if not contains(r.get("tech_stack", ""), stack_filter):
            continue
        filtered.append(r)

    st.subheader(f"Results ({len(filtered)})")
    st.dataframe(pd.DataFrame(filtered), use_container_width=True)

    st.subheader("Details")
    for r in filtered:
        label = f"{r.get('company')} — {r.get('title')}"
        with st.expander(label):
            st.write("**Careers URL:**", r.get("careers_url"))
            st.write("**Seniority:**", r.get("seniority"))
            st.write("**Remote:**", r.get("remote_friendly"))
            st.write("**Tech stack:**", r.get("tech_stack"))
            st.write("**Summary:**", r.get("summary"))
            st.write("**Title evidence:**", r.get("title_evidence"))
            st.write("**Evidence:**", r.get("evidence"))
else:
    st.info("Set query and click Run.")
