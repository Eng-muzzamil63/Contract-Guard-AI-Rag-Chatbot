import os
from typing import Any, Dict, List
from neo4j import GraphDatabase

class ContractGraph:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            os.environ["NEO4J_URI"],
            auth=(os.environ["NEO4J_USERNAME"], os.environ["NEO4J_PASSWORD"]),
        )
        self.database = os.getenv("NEO4J_DATABASE", "neo4j")
        self.driver.verify_connectivity()

    def close(self):
        self.driver.close()

    def setup(self):
        statements = [
            "CREATE CONSTRAINT company_name IF NOT EXISTS FOR (n:Company) REQUIRE n.name IS UNIQUE",
            "CREATE CONSTRAINT vendor_name IF NOT EXISTS FOR (n:Vendor) REQUIRE n.name IS UNIQUE",
            "CREATE CONSTRAINT contract_id IF NOT EXISTS FOR (n:Contract) REQUIRE n.id IS UNIQUE",
            "CREATE CONSTRAINT product_name IF NOT EXISTS FOR (n:Product) REQUIRE n.name IS UNIQUE",
            "CREATE CONSTRAINT department_name IF NOT EXISTS FOR (n:Department) REQUIRE n.name IS UNIQUE",
            "CREATE CONSTRAINT obligation_id IF NOT EXISTS FOR (n:Obligation) REQUIRE n.id IS UNIQUE",
            "CREATE CONSTRAINT clause_id IF NOT EXISTS FOR (n:Clause) REQUIRE n.id IS UNIQUE",
            "CREATE CONSTRAINT source_id IF NOT EXISTS FOR (n:Source) REQUIRE n.id IS UNIQUE",
        ]
        with self.driver.session(database=self.database) as session:
            for statement in statements:
                session.run(statement).consume()

    def ingest(self, data: Dict[str, Any], source_name: str):
        contract_id = self._slug(data["contract_title"])
        with self.driver.session(database=self.database) as s:
            s.run("""
                MERGE (c:Company {name:$company})
                MERGE (v:Vendor {name:$vendor})
                MERGE (ct:Contract {id:$contract_id})
                SET ct.title=$title, ct.type=$contract_type,
                    ct.effective_date=$effective_date, ct.expiry_date=$expiry_date,
                    ct.auto_renewal=$auto_renewal, ct.summary=$summary
                MERGE (c)-[:HAS_CONTRACT]->(ct)
                MERGE (v)-[:SUPPLIES_CONTRACT]->(ct)
            """, **{**data, "contract_id": contract_id, "title": data["contract_title"]}).consume()

            s.run("""
                MATCH (ct:Contract {id:$contract_id})
                MERGE (src:Source {id:$source_id})
                SET src.name=$source_name, src.text=$source_text
                MERGE (ct)-[:SOURCE]->(src)
            """, contract_id=contract_id, source_id=contract_id, source_name=source_name,
                 source_text=data.get("summary", "")).consume()

            for product in data.get("products", []):
                s.run("""
                    MATCH (ct:Contract {id:$contract_id})
                    MERGE (p:Product {name:$name})
                    MERGE (ct)-[:COVERS_PRODUCT]->(p)
                """, contract_id=contract_id, name=product).consume()
            for dept in data.get("departments", []):
                s.run("""
                    MATCH (ct:Contract {id:$contract_id})
                    MERGE (d:Department {name:$name})
                    MERGE (d)-[:OWNS]->(ct)
                """, contract_id=contract_id, name=dept).consume()
            for i, ob in enumerate(data.get("obligations", [])):
                oid = f"{contract_id}:ob:{i}"
                s.run("""
                    MATCH (ct:Contract {id:$contract_id})
                    MERGE (o:Obligation {id:$oid})
                    SET o.title=$title, o.description=$description,
                        o.due_date=$due_date, o.owner=$owner, o.consequence=$consequence
                    MERGE (ct)-[:HAS_OBLIGATION]->(o)
                """, contract_id=contract_id, oid=oid, **ob).consume()
            for i, cl in enumerate(data.get("clauses", [])):
                cid = f"{contract_id}:cl:{i}"
                s.run("""
                    MATCH (ct:Contract {id:$contract_id})
                    MERGE (cl:Clause {id:$cid})
                    SET cl.title=$title, cl.text=$text, cl.category=$category, cl.risk_level=$risk_level
                    MERGE (ct)-[:HAS_CLAUSE]->(cl)
                """, contract_id=contract_id, cid=cid, **cl).consume()

    def overview(self) -> List[Dict[str, Any]]:
        with self.driver.session(database=self.database) as s:
            return [dict(r) for r in s.run("""
                MATCH (v:Vendor)-[:SUPPLIES_CONTRACT]->(c:Contract)
                OPTIONAL MATCH (c)-[:HAS_OBLIGATION]->(o:Obligation)
                RETURN c.title AS contract, v.name AS vendor,
                       c.expiry_date AS expiry_date, c.auto_renewal AS auto_renewal,
                       count(o) AS obligations
                ORDER BY c.expiry_date
            """)]

    def graph_context(self, question: str, limit: int = 20) -> List[Dict[str, Any]]:
        tokens = [t for t in question.replace("?", " ").replace(",", " ").split() if len(t) >= 4][:8]
        with self.driver.session(database=self.database) as s:
            # Graph-first retrieval: find matching contracts/entities, then expand their neighborhoods.
            rows = s.run("""
                MATCH (c:Contract)
                OPTIONAL MATCH (v0:Vendor)-[:SUPPLIES_CONTRACT]->(c)
                OPTIONAL MATCH (c)-[:HAS_OBLIGATION]->(o0:Obligation)
                OPTIONAL MATCH (c)-[:HAS_CLAUSE]->(cl0:Clause)
                OPTIONAL MATCH (c)-[:COVERS_PRODUCT]->(p0:Product)
                OPTIONAL MATCH (d0:Department)-[:OWNS]->(c)
                WITH c, v0, o0, cl0, p0, d0
                WHERE any(term IN $terms WHERE
                    toLower(coalesce(c.title,'')) CONTAINS toLower(term) OR
                    toLower(coalesce(c.summary,'')) CONTAINS toLower(term) OR
                    toLower(coalesce(v0.name,'')) CONTAINS toLower(term) OR
                    toLower(coalesce(o0.title,'')) CONTAINS toLower(term) OR
                    toLower(coalesce(o0.description,'')) CONTAINS toLower(term) OR
                    toLower(coalesce(cl0.title,'')) CONTAINS toLower(term) OR
                    toLower(coalesce(cl0.text,'')) CONTAINS toLower(term) OR
                    toLower(coalesce(p0.name,'')) CONTAINS toLower(term) OR
                    toLower(coalesce(d0.name,'')) CONTAINS toLower(term))
                WITH DISTINCT c
                CALL (c) {
                    MATCH (v:Vendor)-[:SUPPLIES_CONTRACT]->(c)
                    OPTIONAL MATCH (co:Company)-[:HAS_CONTRACT]->(c)
                    OPTIONAL MATCH (c)-[:HAS_OBLIGATION]->(o:Obligation)
                    OPTIONAL MATCH (c)-[:HAS_CLAUSE]->(cl:Clause)
                    OPTIONAL MATCH (c)-[:COVERS_PRODUCT]->(p:Product)
                    OPTIONAL MATCH (d:Department)-[:OWNS]->(c)
                    RETURN v.name AS vendor, co.name AS company, c.title AS contract,
                           c.expiry_date AS expiry_date, c.auto_renewal AS auto_renewal,
                           c.summary AS summary,
                           collect(DISTINCT {title:o.title, due_date:o.due_date, owner:o.owner, consequence:o.consequence}) AS obligations,
                           collect(DISTINCT {title:cl.title, category:cl.category, risk_level:cl.risk_level, text:cl.text}) AS clauses,
                           collect(DISTINCT p.name) AS products, collect(DISTINCT d.name) AS departments
                }
                RETURN vendor, company, contract, expiry_date, auto_renewal, summary, obligations, clauses, products, departments
                LIMIT $limit
            """, terms=tokens or ["contract"], limit=limit)
            return [dict(r) for r in rows]

    def risks(self) -> List[Dict[str, Any]]:
        with self.driver.session(database=self.database) as s:
            return [dict(r) for r in s.run("""
                MATCH (v:Vendor)-[:SUPPLIES_CONTRACT]->(c:Contract)
                OPTIONAL MATCH (c)-[:HAS_CLAUSE]->(cl:Clause)
                OPTIONAL MATCH (c)-[:HAS_OBLIGATION]->(o:Obligation)
                WITH c,v,
                     max(CASE cl.risk_level WHEN 'high' THEN 3 WHEN 'medium' THEN 2 ELSE 1 END) AS max_clause_risk,
                     collect(DISTINCT {title:o.title, due_date:o.due_date, consequence:o.consequence}) AS obligations
                RETURN c.title AS contract, v.name AS vendor, c.expiry_date AS expiry_date,
                       c.auto_renewal AS auto_renewal, max_clause_risk, obligations,
                       CASE WHEN max_clause_risk=3 THEN 'HIGH'
                            WHEN c.expiry_date IS NOT NULL AND c.expiry_date < '2027-02-01' THEN 'MEDIUM'
                            ELSE 'LOW' END AS priority
                ORDER BY max_clause_risk DESC, c.expiry_date
            """)]

    @staticmethod
    def _slug(value: str) -> str:
        return "-".join("".join(ch.lower() for ch in value if ch.isalnum() or ch == " ").split())
