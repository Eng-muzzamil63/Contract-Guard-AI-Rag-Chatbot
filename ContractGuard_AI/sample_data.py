SAMPLES = [
    {
        "contract_title": "Acme Cloud Services Agreement",
        "contract_type": "Cloud Services Agreement",
        "effective_date": "2026-01-15",
        "expiry_date": "2027-01-15",
        "auto_renewal": False,
        "company": "Northstar Retail",
        "vendor": "Acme Cloud",
        "products": ["Checkout Platform", "Customer Data Platform"],
        "departments": ["Engineering", "Operations"],
        "obligations": [
            {"title":"Availability SLA", "description":"Maintain 99.9% monthly availability.", "due_date":"Monthly", "owner":"Acme Cloud", "consequence":"Service credits apply after SLA breach."},
            {"title":"Security Incident Notice", "description":"Notify Northstar of a security incident within 24 hours.", "due_date":"24 hours after discovery", "owner":"Acme Cloud", "consequence":"Escalation and remediation review."}
        ],
        "clauses": [
            {"title":"Data Processing", "text":"Vendor processes customer data on behalf of Northstar.", "category":"data", "risk_level":"high"},
            {"title":"Termination for Cause", "text":"Either party may terminate for material breach after notice and cure period.", "category":"termination", "risk_level":"medium"}
        ],
        "summary":"Cloud infrastructure contract supporting checkout and customer data operations. Expires January 15, 2027 without automatic renewal."
    },
    {
        "contract_title": "BrightShip Logistics Agreement",
        "contract_type": "Logistics Services Agreement",
        "effective_date": "2026-03-01",
        "expiry_date": "2027-03-31",
        "auto_renewal": True,
        "company": "Northstar Retail",
        "vendor": "BrightShip Logistics",
        "products": ["Fulfillment Network", "Last-Mile Delivery"],
        "departments": ["Supply Chain", "Operations"],
        "obligations": [
            {"title":"Delivery SLA", "description":"Maintain 96% on-time delivery for covered shipments.", "due_date":"Monthly", "owner":"BrightShip Logistics", "consequence":"Credits for sustained service failure."}
        ],
        "clauses": [
            {"title":"Service Levels", "text":"On-time delivery target is 96% across covered shipments.", "category":"sla", "risk_level":"medium"}
        ],
        "summary":"Logistics agreement supporting fulfillment and last-mile delivery with automatic renewal."
    }
]
