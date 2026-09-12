from typing import Dict, List, Optional
from src.config import GEMINI_API_KEY, DEFAULT_MODEL
from src.samples import SAMPLE_QA_QUESTIONS

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None


# Verified ground-truth answers for the 5 typical questions
PRESET_ANSWERS: Dict[str, Dict[str, str]] = {
    "What should I check before signing a commercial lease?": {
        "summary": "Before signing a commercial lease in Pakistan, you should verify 6 critical commercial areas. Note that tenancy terms depend on provincial rent restriction legislation and the mutually agreed written contract.",
        "key_points": """
1. **Clear Termination & Notice Period:** Avoid ambiguous phrases like 'reasonable notice'. Agree on an explicit written notice period (mutually negotiated benchmarks are commonly 60 to 90 days).
2. **Maintenance Responsibilities:** Clearly divide structural repairs (roof, exterior walls, primary plumbing = Landlord) from day-to-day internal operational maintenance (Tenant).
3. **Renewal Terms & Rent Escalation:** Specify renewal mechanisms prior to lease expiry. Annual rent escalation caps (commonly negotiated between 8% to 10%) should be explicitly agreed in writing.
4. **Security Deposit Refund:** Explicitly state that the security deposit is refundable upon vacant possession, along with inspection timelines.
5. **Permitted Use & Commercial Zoning:** Ensure the property is commercially approved by the relevant local authority (e.g., LDA in Lahore, CDA in Islamabad, KDA in Karachi) for your business activity.
6. **Withholding Tax Allocation:** If the tenant qualifies as a prescribed withholding agent, clarify whether agreed rent is inclusive or exclusive of advance income tax withholding under Section 155 of the Income Tax Ordinance 2001.

🔍 **Verification Step:** Tenancy rules and eviction procedures are governed by provincial rent laws (e.g. Punjab Rented Premises Act 2009, Sindh Rented Premises Ordinance 1979, Islamabad Rent Restriction Ordinance 2001). Always verify provincial jurisdiction and register your lease agreement.
""",
        "sources": "Provincial Rented Premises Legislation / Contract Act 1872 / Income Tax Ordinance 2001 (Section 155)"
    },
    "Can I terminate this contract early, and what notice is required?": {
        "summary": "Under Pakistani contract law, early termination rights depend strictly on the express terms of your contract and the nature of any default.",
        "key_points": """
1. **Termination for Convenience:** Review whether your agreement contains a convenience clause allowing exit without cause. If agreed, comply strictly with the written notice timeline specified in the contract.
2. **The Risk of 'Reasonable Notice':** If notice days are unspecified, courts interpret notice based on customary industry practice and payment cycles, but this frequently leads to litigation. Always specify exact days in writing.
3. **Termination for Breach & Cure Periods:** A 14 to 30-day 'Notice to Cure' is a standard commercial drafting mechanism allowing a defaulting party to rectify a defect. However, whether a cure period is legally mandatory depends on the terms of your contract and whether the breach is fundamental under Sections 39 and 73 of the Contract Act 1872.
4. **Exit Consequences & Deposit Forfeiture:** Examine clauses governing liquidated damages, unamortized fit-out costs, or deposit forfeiture upon early exit.

🔍 **Verification Step:** Review contract dispute resolution clauses and consult legal counsel if terminating for material breach or claiming damages under the Specific Relief Act 1877.
""",
        "sources": "Contract Act 1872 (Sections 39, 73, 75) & Specific Relief Act 1877"
    },
    "Who is responsible for taxes or withholding on this payment?": {
        "summary": "Under Pakistani tax law, tax liability depends on the transaction type, recipient classification, and whether the payer is a prescribed withholding agent.",
        "key_points": """
1. **General Principle:** Every business entity is legally responsible for its own net annual income tax obligations.
2. **Withholding Tax (WHT) Obligations:** Advance tax withholding is not limited to large corporations. 'Prescribed persons' under Section 153(7) (including companies, registered AOPs/partnerships, and individuals whose turnover exceeds statutory thresholds) are legally required to deduct tax at source.
3. **Applicable Withholding Rates:**
   - Rates on goods, services, and commercial contracts are determined by the First Schedule and Tenth Schedule of the Income Tax Ordinance 2001.
   - Rates vary based on whether the recipient is a company vs individual/AOP, the specific service sector, and whether the recipient is an Active Taxpayer (ATL) filer.
   - Non-filers are subject to 100% higher withholding under the Tenth Schedule.
4. **Contractual Pricing Clarity:** Commercial contracts must explicitly state whether prices are **'inclusive of all applicable taxes'** or **'exclusive of provincial sales taxes'** (PRA/SRB/KPRA) to prevent unexpected payment shortfalls.

🔍 **Verification Step:** Withholding schedules change with annual Finance Acts. Always verify active rates for the current tax year on FBR Iris (iris.fbr.gov.pk) or through a certified tax advisor.
""",
        "sources": "FBR Income Tax Ordinance 2001 (Sections 152, 153, 155, Tenth Schedule) & Provincial Sales Tax on Services Acts"
    },
    "What records should my business maintain for tax purposes?": {
        "summary": "Under Section 174 of the Income Tax Ordinance 2001 and Rule 29 of the Income Tax Rules 2002, every registered taxpayer must maintain statutory accounts and supporting documentation.",
        "key_points": """
1. **Sales & Invoicing Records:** Serially numbered sales invoices/receipts containing buyer details, dates, NTN, and tax charged.
2. **Purchases & Expense Vouchers:** Original vendor invoices, utility bills, business rental agreements, and proof of payment.
3. **Banking & Realization Records:** Dedicated business bank account statements, reconciliation statements, and foreign remittance realization certificates (e.g. PRCs for exporters).
4. **Payroll & Withholding Documents:** Employee salary sheets, tax deduction certificates, and CPR payment receipts for deposited withholding tax.
5. **Mandatory Retention Period:** Under Section 174(3), records must be maintained for a **minimum of 6 years** from the end of the relevant tax year. If an audit or assessment appeal is pending, records must be retained until final disposal.

🔍 **Verification Step:** Consult FBR Rule 29 to verify the exact format of accounts prescribed for your turnover bracket.
""",
        "sources": "Income Tax Ordinance 2001, Section 174 & Income Tax Rules 2002 (Rule 29)"
    },
    "What registrations or compliance steps apply to my business?": {
        "summary": "Commercial compliance in Pakistan follows a multi-tier framework: Federal Tax, Entity Formation, Provincial Sales Tax, and Sectoral Concessions.",
        "key_points": """
1. **Tier 1 (Federal Tax - FBR):** Register on FBR Iris to obtain a National Tax Number (NTN). Required for legal business banking and filing annual income tax returns.
2. **Tier 2 (Entity Formation):**
   - Sole Proprietorship: Register business name with FBR Iris.
   - Partnership / AOP: Register partnership deed with Registrar of Firms (Form C).
   - Company: Incorporate with SECP under the Companies Act 2017 (Single Member Company or Private Limited).
3. **Tier 3 (Provincial Sales Tax on Services):** If rendering services (software, design, consulting, marketing), register with your provincial authority (PRA in Punjab, SRB in Sindh, KPRA in KPK).
4. **Tier 4 (Sectoral Licensing & Concessions):** IT & ITeS exporters may register with Pakistan Software Export Board (PSEB). Concessionary tax treatment under Section 154A is conditional on bringing export proceeds in foreign exchange via formal banking channels and filing required tax statements.

🔍 **Verification Step:** Registration requirements and tax credits depend on your specific sector, location, and the current Finance Act. Verify active requirements on respective authority portals.
""",
        "sources": "FBR Iris Guidelines / SECP Companies Act 2017 / Income Tax Ordinance 2001 (Section 154A) / PSEB Policy"
    }
}


from src.rag_store import LegalRAGStore


class LegalAdvisorAgent:
    """
    Legal & Tax Q&A Advisor:
    RAG-powered conversational engine that retrieves verified Pakistani statutes
    via semantic vector search before generating educational legal guidance.
    """

    def __init__(self):
        self.client = None
        self.rag_store = LegalRAGStore()
        if GEMINI_API_KEY and genai:
            try:
                self.client = genai.Client(api_key=GEMINI_API_KEY)
            except Exception as e:
                print(f"[LegalAdvisorAgent] Client error: {e}")

    def answer_question(self, user_query: str) -> Dict[str, Any]:
        """
        Provides educational legal and tax guidance augmented with semantic RAG retrieval.
        Returns:
            - answer: generated response text
            - source: primary statute or authority citation
            - retrieved_chunks: list of top retrieved RAG chunks with similarity scores
        """
        # 1. Semantic RAG Retrieval
        retrieved_chunks = self.rag_store.search(user_query, top_k=3)
        context_str = "\n\n".join([
            f"[Source {i+1}: {c['title']} | Authority: {c['authority']} | Statute: {c['statute']}]\n{c['content']}"
            for i, c in enumerate(retrieved_chunks)
        ])

        # 2. Check if query exactly matches one of our 5 preset questions for instant verified response
        for q_key, q_data in PRESET_ANSWERS.items():
            if q_key.lower() in user_query.lower() or user_query.lower() in q_key.lower():
                return {
                    "answer": f"### 📌 Overview\n{q_data['summary']}\n\n### ⚖️ Key Legal & Tax Guidance\n{q_data['key_points']}\n\n---\n**📚 Official Statutory Reference:**\n*{q_data['sources']}*\n\n> *⚠️ Disclaimer: BizShield AI provides educational and informational guidance based on official Pakistani regulations, not formal legal advice.*",
                    "source": q_data["sources"],
                    "retrieved_chunks": retrieved_chunks
                }

        # 3. Live Gemini AI Response Augmented with RAG Context
        if not self.client:
            return {
                "answer": f"BizShield AI provides informational guidance based on Pakistani legal and tax frameworks.\n\n### Retrieved Statutory Context:\n{context_str}",
                "source": "FBR & SECP Official Guidelines",
                "retrieved_chunks": retrieved_chunks
            }

        prompt = f"""
You are BizShield AI, an intelligent legal and tax educational advisor for Pakistani small businesses, startups, and freelancers.

USER QUESTION:
\"{user_query}\"

VERIFIED STATUTORY CONTEXT (RETRIEVED FROM RAG KNOWLEDGE STORE):
\"\"\"
{context_str}
\"\"\"

PEDAGOGICAL & STATUTORY INSTRUCTIONS:
1. Provide a clear, simple, and direct explanation in plain English that a non-lawyer can understand.
2. Directly apply and cite the retrieved statutory context (SECP Companies Act 2017, FBR Income Tax Ordinance 2001, PRA/SRB Sales Tax, Contract Act 1872).
3. Use structured bullet points.
4. Distinguish between mandatory statutory requirements and recommended commercial negotiation practices.
5. Avoid hard-coding fixed tax rates or timelines as universal laws where they depend on the taxpayer category, province, or tax year.
6. Conclude with a clear 'Verification Step' advising verification against the current Finance Act or relevant authority portal.
7. Emphasize that this is educational guidance, not formal attorney advice.
"""

        try:
            response = self.client.models.generate_content(
                model=DEFAULT_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.3
                )
            )
            primary_statute = retrieved_chunks[0]["statute"] if retrieved_chunks else "Pakistani Commercial Law"
            return {
                "answer": response.text.strip(),
                "source": primary_statute,
                "retrieved_chunks": retrieved_chunks
            }
        except Exception as e:
            print(f"[LegalAdvisorAgent] Query error: {e}")
            return {
                "answer": f"Unable to fetch live response ({e}). Please review our preset guides or try again.",
                "source": "System Fallback",
                "retrieved_chunks": retrieved_chunks
            }
