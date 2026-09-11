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
        "summary": "Before signing a commercial lease in Pakistan, you must verify 6 critical points to prevent surprise evictions, sudden rent spikes, and unexpected repair bills.",
        "key_points": """
1. **Clear Termination & Notice Period:** Avoid vague phrases like 'reasonable notice'. Insist on an exact written notice timeframe (typically 60 to 90 days).
2. **Maintenance Split:** Clearly separate structural repairs (roof, pillars, exterior walls, main plumbing = Landlord) from minor day-to-day internal operational repairs (Tenant).
3. **Renewal Rights & Rent Escalation Cap:** Ensure the contract specifies your right to renew upon expiry, with an exact cap on rent increment (typically 8% to 10% per annum).
4. **Security Deposit Refund Terms:** Ensure the deposit is explicitly stated as 'refundable within 14-30 days of vacant possession'.
5. **Permitted Use & Municipal Zoning:** Verify that the premises are commercially zoned by the local development authority (e.g. LDA in Lahore, CDA in Islamabad, KDA in Karachi).
6. **Withholding Tax Allocation:** If your business is a corporate entity or registered taxpayer, clarify Section 155 Income Tax withholding deductions from rent.
""",
        "sources": "Punjab Rented Premises Act 2009 / Islamabad Rent Restriction Ordinance / Income Tax Ordinance 2001 (Section 155)"
    },
    "Can I terminate this contract early, and what notice is required?": {
        "summary": "Under Pakistani contract law, early termination depends strictly on the termination clause agreed in your contract.",
        "key_points": """
1. **Termination for Convenience:** Check if the contract includes an 'at-will' or convenience clause allowing termination without cause. If it specifies '30 days written notice', you can exit cleanly by serving written notice.
2. **The Danger of 'Reasonable Notice':** If the contract only says 'reasonable notice' without defining days, Pakistani courts generally interpret this based on payment cycles (e.g. 1 month notice for monthly rent), but it frequently triggers disputes.
3. **Termination for Material Breach:** If the other party violates a core term (e.g. fails to deliver services or fails to provide quiet possession), you can issue a formal Notice to Cure (typically 14-30 days) before terminating immediately.
4. **Exit Penalties & Forfeiture:** Check whether early termination forfeits your security deposit or requires paying remaining months in the term.
""",
        "sources": "Contract Act 1872 (Sections 39, 73, 75) & Specific Relief Act 1877"
    },
    "Who is responsible for taxes or withholding on this payment?": {
        "summary": "Under Pakistani tax law, tax liability depends on the nature of the transaction and the taxpayer status of the payer and recipient.",
        "key_points": """
1. **General Rule:** Every business is responsible for paying income tax on its net annual earnings.
2. **Withholding Tax (WHT) Obligations:** If the payer is a prescribed person (a Private Limited company, registered firm, or exporter), they are legally obligated under FBR rules to deduct withholding tax at source before remitting payment to the vendor.
3. **Common Withholding Rates:**
   - Supply of Goods: 5% - 6% (ATL)
   - Rendering of Services: 8% - 11% (ATL) for corporate/individual service providers
   - Rental of Property: Scaled rates under Section 155
   - Non-ATL (Filer vs Non-Filer): Withholding rates double for non-filers!
4. **Contract Best Practice:** Always specify in your agreement whether fees are **'inclusive of all applicable taxes'** or **'exclusive of applicable provincial sales taxes'**.
""",
        "sources": "FBR Income Tax Ordinance 2001 (Sections 152, 153, 155) & Provincial Sales Tax on Services Acts"
    },
    "What records should my business maintain for tax purposes?": {
        "summary": "Under Section 174 of the Income Tax Ordinance 2001, every taxpayer is legally required to maintain complete and accurate financial records.",
        "key_points": """
1. **Sales & Revenue:** Serially numbered sales invoices/receipts, bank deposit slips, credit card settlement sheets, export realization forms (proceeds).
2. **Business Expenses:** Original vendor bills, payment receipts, utility bills (electricity, internet), lease agreements, and rent receipts.
3. **Banking Records:** Dedicated business bank account statements, reconciliation statements, and cheque counterfoils.
4. **Payroll & Staff Records:** Employee salary sheets, CNIC copies, and Computerized Payment Receipts (CPRs) for deducted employee withholding tax.
5. **Retention Period:** Records must be retained for a **minimum of 6 years** from the end of the relevant tax year.
""",
        "sources": "Income Tax Ordinance 2001, Section 174 & Income Tax Rules 2002 (Rule 29)"
    },
    "What registrations or compliance steps apply to my business?": {
        "summary": "Compliance in Pakistan follows a 4-tier structure: Identity, Federal Tax, Provincial Sales Tax, and Entity Formation.",
        "key_points": """
1. **Tier 1 (Federal Tax - FBR):** Register on FBR Iris for a National Tax Number (NTN). Mandatory for all businesses to open bank accounts and file annual returns.
2. **Tier 2 (Entity Formation):**
   - Sole Proprietorship: Register business name with FBR on Iris portal.
   - Partnership / AOP: Register partnership deed with Registrar of Firms (Form C).
   - Company: Incorporate with SECP (Single Member Company or Private Limited).
3. **Tier 3 (Provincial Sales Tax on Services):** If offering services (software, design, consulting, marketing), register with your provincial authority (PRA in Punjab, SRB in Sindh, KPRA in KPK).
4. **Tier 4 (Sectoral/Chamber):** IT businesses should register with Pakistan Software Export Board (PSEB) for export tax rebates (0.25% final tax). Retailers and traders should register with their local Chamber of Commerce.
""",
        "sources": "FBR Iris Guidelines / SECP Companies Act 2017 / PSEB Policy Guidelines"
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
4. Conclude with specific official legal/regulatory citations.
5. Emphasize that this is educational guidance, not formal attorney advice.
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
