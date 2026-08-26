import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from models import ContractExtraction


def get_llm():
    return ChatOpenAI(model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"), temperature=0)


def extract_contract(text: str) -> ContractExtraction:
    llm = get_llm().with_structured_output(ContractExtraction)
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an enterprise contract intelligence analyst. Extract only facts supported by the supplied document.\n"
         "Infer reasonable categories but never invent dates or obligations. Risk levels: high for termination/liability/data/security/major SLA exposure; medium for material commercial constraints; low for routine clauses."""),
        ("human", "Extract this contract:\n\n{text}"),
    ])
    return (prompt | llm).invoke({"text": text[:50000]})


def answer_question(question: str, context: list[dict]) -> str:
    llm = get_llm()
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are ContractGuard AI, an enterprise contract-risk analyst. Answer ONLY from the graph context provided. Explain connected relationships, cite contract/vendor names in plain text, and clearly distinguish evidence from recommendation. If evidence is insufficient, say so. Do not give legal advice; frame findings as operational/commercial risk signals."""),
        ("human", "Question: {question}\n\nNeo4j GraphRAG context:\n{context}"),
    ])
    return (prompt | llm).invoke({"question": question, "context": context}).content
