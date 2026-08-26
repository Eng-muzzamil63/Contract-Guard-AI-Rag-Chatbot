# Contract-Guard-AI-Rag-Chatbot

# ContractGuard AI

**GraphRAG for contract risk and business impact analysis.**

ContractGuard AI turns contracts into a connected Neo4j knowledge graph and uses a LangGraph agent to answer operational questions about vendors, obligations, clauses, products, departments, and renewal risk.

## Why this is a real business solution

Traditional document chat can answer *what a contract says*. ContractGuard is designed to answer *what the contract affects*:

- Which business operations depend on a vendor?
- What obligations or security clauses need attention?
- Which contract should the team review first?
- What could be impacted by a contract expiring?

## Architecture

`PDF → LLM extraction → Neo4j knowledge graph → Graph retrieval → LangGraph agent → grounded answer`

The workshop's GraphRAG course focuses on knowledge graphs, Cypher, and agent applications; this project applies those ideas to enterprise contract operations. Neo4j's official Python driver supports Aura connections, and Neo4j publishes an official GraphRAG package for Python/OpenAI workflows. 

## Run locally

1. Create a Neo4j Aura instance and copy its credentials.
2. Copy `.env.example` to `.env` and set Neo4j + OpenAI credentials.
3. Create a virtual environment:

```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
# macOS/Linux
# source .venv/bin/activate
```

4. Install dependencies:

```bash
pip install -r requirements.txt
```

5. Start the app:

```bash
streamlit run app.py
```

6. Click **Load demo contracts** first to see the complete workflow, then upload a PDF.

## Graph model

```text
Company ──HAS_CONTRACT──> Contract <──SUPPLIES_CONTRACT── Vendor
                              │
                              ├──COVERS_PRODUCT──> Product
                              ├──HAS_OBLIGATION──> Obligation
                              ├──HAS_CLAUSE──> Clause
                              └──SOURCE──> Source

Department ──OWNS──> Contract
```

## Demo script

1. Load demo contracts.
2. Ask: **Which contracts create the highest operational risk?**
3. Ask: **What could be affected if Acme Cloud's contract expires?**
4. Upload a real/non-sensitive sample contract.
5. Show the extracted entities and the graph-grounded answer.

## Recruiter-facing value

This project demonstrates practical skills in Python, Neo4j, Cypher, GraphRAG, structured LLM extraction, LangGraph agents, document processing, and business-risk reasoning.

> This is an operational risk prototype, not legal advice.
