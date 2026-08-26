import os
import uuid
import streamlit as st
from dotenv import load_dotenv
from pypdf import PdfReader

from graph import ContractGraph
from llm import extract_contract
from agent import build_graph_agent
from sample_data import SAMPLES

load_dotenv()
st.set_page_config(page_title="ContractGuard AI", page_icon="🛡️", layout="wide")

st.title("🛡️ ContractGuard AI")
st.caption("GraphRAG for contract risk, obligations, dependencies, and renewal decisions")

missing = [k for k in ["NEO4J_URI", "NEO4J_USERNAME", "NEO4J_PASSWORD", "OPENAI_API_KEY"] if not os.getenv(k)]
if missing:
    st.error("Missing environment variables: " + ", ".join(missing) + ". Copy .env.example to .env and fill them in.")
    st.stop()

@st.cache_resource
def get_kg():
    kg = ContractGraph()
    kg.setup()
    return kg

kg = get_kg()
agent = build_graph_agent(kg)

with st.sidebar:
    st.header("Workspace")
    if st.button("Load demo contracts", use_container_width=True):
        for item in SAMPLES:
            kg.ingest(item, item["contract_title"] + ".demo")
        st.success("Demo graph loaded")
    st.divider()
    st.write("**Neo4j:** connected")
    st.write("**GraphRAG:** active")
    st.write("**Agent:** LangGraph")

uploaded = st.file_uploader("Upload a contract PDF", type=["pdf"])
if uploaded:
    reader = PdfReader(uploaded)
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    with st.spinner("Extracting entities, clauses, and obligations…"):
        extracted = extract_contract(text)
        kg.ingest(extracted.model_dump(), uploaded.name)
    st.success(f"Added **{extracted.contract_title}** to the Neo4j knowledge graph.")
    with st.expander("What was extracted"):
        st.json(extracted.model_dump())

st.subheader("Business Risk Dashboard")
risks = kg.risks()
if risks:
    c1, c2, c3 = st.columns(3)
    c1.metric("Contracts", len(risks))
    c2.metric("High-risk clauses", sum(1 for r in risks if r.get("max_clause_risk") == 3))
    c3.metric("Renewal / expiry items", sum(1 for r in risks if r.get("expiry_date")))
    st.dataframe(risks, use_container_width=True, hide_index=True)
else:
    st.info("Load the demo contracts or upload your first PDF.")

st.subheader("Ask the Contract Graph")
examples = [
    "Which contracts create the highest operational risk?",
    "What could be affected if Acme Cloud's contract expires?",
    "Which vendors have obligations related to security or service levels?",
    "Which contract should the operations team review first and why?",
]
selected = st.selectbox("Example question", ["Custom question"] + examples)
question = st.text_input("Your business question", value="" if selected == "Custom question" else selected)
if st.button("🔎 Investigate", type="primary", use_container_width=True) and question:
    with st.spinner("Traversing Neo4j relationships and reasoning over the graph…"):
        result = agent.invoke({"question": question})
    st.markdown("### 🧠 GraphRAG Answer")
    st.write(result["answer"])
    with st.expander("Graph evidence used"):
        st.json(result.get("context", []))

st.divider()
st.markdown("**Why GraphRAG?** ContractGuard does not treat each PDF as an isolated document. Neo4j connects vendors → contracts → products → departments → obligations → clauses, so the agent can answer impact and dependency questions across the business.")
