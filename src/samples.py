"""
Sample contracts and reference rubrics provided for BizShield AI testing and demo.
"""

SAMPLE_1_LEASE_TITLE = "Commercial Lease Agreement (ABC Properties & XYZ Software Solutions)"

SAMPLE_1_LEASE_TEXT = """COMMERCIAL LEASE AGREEMENT
This Agreement is made between:
Landlord: ABC Properties
Tenant: XYZ Software Solutions
Premises: Office No. 12, Lahore

1. Lease Term
The lease shall remain valid for a period of two years, commencing on 1 October 2026.

2. Monthly Rent
The Tenant shall pay monthly rent of PKR 150,000 to the Landlord.

3. Security Deposit
The Tenant shall pay a refundable security deposit of PKR 300,000 before taking possession of the premises.

4. Payment
The monthly rent shall be paid by the Tenant on a monthly basis.

5. Termination
Either party may terminate this Agreement by providing reasonable notice to the other party.

6. Maintenance
The Tenant shall maintain the premises and keep it in good condition as required.

7. Utilities
The Tenant shall be responsible for payment of electricity, water and other utility charges.

8. Use of Premises
The premises shall be used for lawful business activities by the Tenant.

9. Repairs and Alterations
The Tenant shall not make major structural changes to the premises without the Landlord's permission. Minor changes may be made by the Tenant as necessary for business operations.

10. Subletting
The Tenant shall not transfer or sublet the premises to another party without the prior consent of the Landlord.

11. Insurance
The Tenant shall be responsible for obtaining any insurance that it considers necessary for its business operations.

12. Late Payment
If the Tenant fails to pay rent on time, the Landlord may take appropriate action after notifying the Tenant.

13. Damage to Premises
The Tenant shall be responsible for damage caused by its employees, customers or representatives, except for normal wear and tear.

14. Renewal
The Agreement may be renewed upon mutual agreement between the Landlord and Tenant.

15. Dispute Resolution
The parties shall first attempt to resolve any dispute through mutual discussion. If the dispute cannot be resolved, either party may pursue the remedies available under applicable law.

16. Governing Law
This Agreement shall be governed by the applicable laws of Pakistan.

17. Notices
Any notice under this Agreement may be communicated through an appropriate written method agreed upon by the parties.

18. Entire Agreement
This Agreement represents the understanding between the Landlord and Tenant concerning the leased premises.
________________________________________
Landlord Signature: ABC Properties
Tenant Signature: XYZ Software Solutions
Date: 1 October 2026
"""

SAMPLE_1_EXPECTED_FINDINGS = [
    {
        "clause": "Clause 5: Termination",
        "issue": "Notice period is unquantified ('reasonable notice'). In commercial practice, parties typically define an agreed written timeline (such as 60 or 90 days as a negotiated benchmark) rather than relying on ambiguous terms, subject to applicable provincial tenancy laws.",
        "risk": "High",
        "category": "Vague Termination Rights (Commercial Risk)",
        "action": "Specify an agreed written notice period (e.g. 60 or 90 days as a negotiated commercial benchmark) and define explicit grounds for termination.",
        "legal_basis": "Contract Act 1872 (Sections 39, 73) & Provincial Rented Premises Legislation (Termination notice & grounds)"
    },
    {
        "clause": "Clause 6: Maintenance",
        "issue": "The clause does not clearly distinguish structural repairs from routine tenant upkeep, which may create disputes. Clarify the respective responsibilities of both parties.",
        "risk": "Medium",
        "category": "Broad / Unclear Obligations (Ambiguous Clause)",
        "action": "Clarify in the clause that landlord maintains structural integrity and external premises, while tenant handles internal operational upkeep.",
        "legal_basis": "Provincial Rented Premises Legislation (e.g. Punjab Rented Premises Act 2009 / Sindh 1979) – Statutory Maintenance Allocation"
    },
    {
        "clause": "Clause 12: Late Payment",
        "issue": "Consequences of late payment are vague ('appropriate action'). Lacks a clear grace period and agreed consequences.",
        "risk": "Medium",
        "category": "Unclear Payment Terms (Potential Risk)",
        "action": "Define a clear grace period and applicable consequences to avoid arbitrary dispute.",
        "legal_basis": "Contract Act 1872 (Section 74 - Liquidated damages & penalty limits)"
    },
    {
        "clause": "Clause 14: Renewal",
        "issue": "Missing renewal mechanism, notice window, and agreed rent revision mechanism.",
        "risk": "High",
        "category": "Missing Protections (Potential Risk)",
        "action": "Add clause defining an agreed/negotiated renewal mechanism and clear notice window prior to lease expiry.",
        "legal_basis": "Provincial Rented Premises Legislation & Contract Act 1872 (Mutual consent & notice mechanism)"
    },
    {
        "clause": "Clause 17: Notices",
        "issue": "Method of notice is unspecified ('appropriate written method'). Needs exact physical addresses, registered courier, or official email.",
        "risk": "Low",
        "category": "Procedural Ambiguity",
        "action": "State that notices must be served via registered courier or official designated business email addresses.",
        "legal_basis": "Contract Act 1872 & Provincial Tenancy Rules (Service of notice & proof of receipt)"
    },
    {
        "clause": "Clause 11: Insurance",
        "issue": "Property vs. business insurance is conflated. Landlord should insure the physical building structure, while tenant covers internal equipment/business content.",
        "risk": "Low",
        "category": "Unclear Allocation of Risk",
        "action": "Clarify that building fire/structure insurance rests with landlord; internal contents rest with tenant.",
        "legal_basis": "General Commercial Practice & Property Law Principles (Allocation of structural vs internal business risk)"
    },
    {
        "clause": "Tax Considerations (Missing Clause)",
        "issue": "The agreement does not specify whether rent payments are inclusive or exclusive of applicable withholding tax deductions where the tenant qualifies as a prescribed withholding agent under Section 155 of the Income Tax Ordinance 2001.",
        "risk": "High",
        "category": "Tax / Withholding Responsibility Missing (Potential Risk)",
        "action": "Add an explicit clause clarifying whether the agreed rent is gross or net of statutory withholding deductions where the payer is a prescribed withholding agent under applicable law.",
        "legal_basis": "Income Tax Ordinance 2001 (Section 155 - Deduction of Tax on Rent for Prescribed Withholding Agents)"
    }
]

SAMPLE_2_VENDOR_TITLE = "Service & Vendor Agreement (ABC Retail Solutions & DigitalPro Services)"

SAMPLE_2_VENDOR_TEXT = """SAMPLE SERVICE & VENDOR AGREEMENT
This Agreement is made between:
Client: ABC Retail Solutions
Vendor: DigitalPro Services
Service: Website Development and Digital Support
Effective Date: 1 October 2026

1. Scope of Services
The Vendor will provide website development, basic maintenance, and digital support services to the Client.
The exact features and services will be discussed between the parties and may be adjusted according to the Client's business needs.

2. Contract Term
This Agreement will remain effective for one year from the Effective Date.
The Agreement may continue after the initial term if both parties agree.

3. Fees and Payment
The Client will pay the Vendor PKR 120,000 for the services.
Payment will be made in installments as mutually agreed by the parties.
The Vendor may revise its charges if additional work or circumstances require it.

4. Delivery Timeline
The Vendor will make reasonable efforts to complete the website within an appropriate timeframe.
Any delay caused by changes requested by the Client may result in an adjustment to the delivery schedule.

5. Termination
Either party may terminate this Agreement by providing reasonable notice to the other party.
The Vendor may also terminate the Agreement if the Client fails to cooperate or provide required information.

6. Intellectual Property
Materials created specifically for the Client may be used by the Client for its business purposes.
The Vendor may retain ownership of its pre-existing materials, tools, templates, and other resources used during the project.

7. Confidentiality
Both parties agree to keep confidential information private and not disclose it to third parties unless reasonably necessary for providing the services.

8. Liability
The Vendor will not be responsible for losses arising from circumstances beyond its reasonable control.
The Vendor's responsibility for any other loss will be limited to an amount considered reasonable in the circumstances.

9. Data and Information
The Client may provide business information, customer information, login details, and other materials required for the services.
The Vendor will take reasonable steps to protect such information.

10. Subcontracting
The Vendor may involve employees, contractors, or third-party service providers where necessary to complete the services.

11. Dispute Resolution
The parties will first attempt to resolve any dispute through mutual discussion.
If the dispute cannot be resolved, either party may pursue remedies available under the applicable laws.

12. Taxes
Each party will be responsible for its own applicable taxes and obligations arising from this Agreement, subject to any applicable withholding or tax requirements.

13. Changes to Agreement
Any significant changes to the services, fees, or other terms may be agreed between the parties through written or electronic communication.

14. Governing Law
This Agreement will be governed by the applicable laws of Pakistan.

15. Entire Agreement
This Agreement represents the understanding between the parties regarding the services described above.
________________________________________
SIGNATURES
For ABC Retail Solutions
Name: ABC Retail Solutions
Signature: ________________
Date: 1 October 2026

For DigitalPro Services
Name: DigitalPro Services
Signature: ________________
Date: 1 October 2026
"""

SAMPLE_2_EXPECTED_FINDINGS = [
    {
        "clause": "Clause 1: Scope of Services",
        "issue": "Scope is vague ('features will be discussed'). Lacks defined deliverables, specifications, and client acceptance milestones.",
        "risk": "High",
        "category": "Missing Scope / Deliverables",
        "action": "Attach a concrete Statement of Work (SOW) with exact deliverables and milestone sign-off criteria.",
        "legal_basis": "Contract Act 1872 (Section 29 - Certainty of terms and contractual obligations)"
    },
    {
        "clause": "Clause 3: Fees & Payment",
        "issue": "Vendor has unilateral right to revise charges ('if additional work or circumstances require it'). Highly risky for client budget.",
        "risk": "High",
        "category": "Unilateral Price/Fee Changes",
        "action": "Require a formal written change-order signed by both parties before any additional fee can be charged.",
        "legal_basis": "Contract Act 1872 & Income Tax Ordinance 2001 (Section 153 - Prescribed Withholding Requirements)"
    },
    {
        "clause": "Clause 4: Delivery Timeline",
        "issue": "Delivery timeline is vague ('reasonable efforts within an appropriate timeframe'). Lacks fixed launch date.",
        "risk": "High",
        "category": "Vague Delivery Schedule",
        "action": "Specify concrete milestone dates and define what constitutes an excusable vs unexcusable delay.",
        "legal_basis": "Contract Act 1872 (Section 55 - Time as essence of contract)"
    },
    {
        "clause": "Clause 6: Intellectual Property",
        "issue": "Client is only granted right to 'use' materials for business purposes, leaving underlying ownership of custom deliverables unallocated.",
        "risk": "High",
        "category": "Unclear IP Ownership (Missing Protection)",
        "action": "As a contractual option, specify that bespoke source code, designs, and deliverables are assigned to Client upon full payment, with vendor retaining pre-existing tools.",
        "legal_basis": "Copyright Ordinance 1962 (Section 13) & IPO-Pakistan – Ownership of works and assignment of bespoke deliverables"
    },
    {
        "clause": "Clause 8: Liability",
        "issue": "Liability is capped at an ambiguous 'amount considered reasonable in the circumstances'.",
        "risk": "Medium",
        "category": "Unclear Liability Cap (Potential Risk)",
        "action": "Define an explicit agreed liability cap and clear exclusions/carve-outs (such as gross negligence or confidentiality breach).",
        "legal_basis": "Contract Act 1872 (Sections 73 & 74 - Enforceability of liability limits & breach compensation)"
    },
    {
        "clause": "Clause 10: Subcontracting",
        "issue": "Vendor can subcontract work to third parties without prior notice or approval from Client.",
        "risk": "Medium",
        "category": "Unclear Subcontracting (Potential Risk)",
        "action": "Require prior written consent from Client before subcontracting core services, with binding confidentiality on subcontractors.",
        "legal_basis": "Contract Act 1872 (Sections 40 & 41 - Performance of contracts & third-party delegation)"
    }
]

COMMON_LEGAL_TRAPS = [
    "Vague termination rights or notice periods",
    "Unclear payment terms or late-payment consequences",
    "Unilateral price/fee changes",
    "Auto-renewal without clear notice requirements",
    "Unclear ownership of intellectual property",
    "Broad or unclear liability/indemnity clauses",
    "Confidentiality and business-data handling not clearly defined",
    "Unclear subcontracting/third-party access",
    "Missing scope, deliverables or acceptance criteria",
    "Tax/withholding responsibilities not clearly specified"
]

SAMPLE_QA_QUESTIONS = [
    "What should I check before signing a commercial lease?",
    "Can I terminate this contract early, and what notice is required?",
    "Who is responsible for taxes or withholding on this payment?",
    "What records should my business maintain for tax purposes?",
    "What registrations or compliance steps apply to my business?"
]
