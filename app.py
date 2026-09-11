import io
import sys
from pathlib import Path
import streamlit as st

# Ensure local src imports work
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.config import APP_NAME, APP_TAGLINE, APP_VERSION, GEMINI_API_KEY
from src.privacy_shield import PrivacyShield
from src.contract_scanner import ContractScanner, ContractAnalysisReport
from src.compliance import SmartComplianceEngine
from src.qa_advisor import LegalAdvisorAgent, PRESET_ANSWERS
from src.samples import (
    SAMPLE_1_LEASE_TITLE, SAMPLE_1_LEASE_TEXT,
    SAMPLE_2_VENDOR_TITLE, SAMPLE_2_VENDOR_TEXT,
    SAMPLE_QA_QUESTIONS
)

# Page configuration
st.set_page_config(
    page_title=f"{APP_NAME} — Legal & Tax Assistant",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Core Services in session state
if "privacy_shield" not in st.session_state:
    st.session_state.privacy_shield = PrivacyShield()

if "contract_scanner" not in st.session_state:
    st.session_state.contract_scanner = ContractScanner()

if "compliance_engine" not in st.session_state:
    st.session_state.compliance_engine = SmartComplianceEngine()

if "qa_advisor" not in st.session_state:
    st.session_state.qa_advisor = LegalAdvisorAgent()

if "current_contract_text" not in st.session_state:
    st.session_state.current_contract_text = SAMPLE_1_LEASE_TEXT

if "current_contract_title" not in st.session_state:
    st.session_state.current_contract_title = SAMPLE_1_LEASE_TITLE

if "analysis_report" not in st.session_state:
    st.session_state.analysis_report = None

if "redaction_info" not in st.session_state:
    st.session_state.redaction_info = None

if "sanitized_text" not in st.session_state:
    st.session_state.sanitized_text = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "compliance_checked" not in st.session_state:
    st.session_state.compliance_checked = set()

# Custom CSS for polished, professional UI
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        color: #0F172A;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #475569;
        margin-bottom: 1.5rem;
    }
    .shield-badge {
        display: inline-block;
        background: #ECFDF5;
        color: #065F46;
        border: 1px solid #A7F3D0;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .risk-card-high {
        background: #FEF2F2;
        border-left: 5px solid #EF4444;
        padding: 16px;
        border-radius: 8px;
        margin-bottom: 14px;
    }
    .risk-card-medium {
        background: #FFFBEB;
        border-left: 5px solid #F59E0B;
        padding: 16px;
        border-radius: 8px;
        margin-bottom: 14px;
    }
    .risk-card-low {
        background: #F0FDF4;
        border-left: 5px solid #10B981;
        padding: 16px;
        border-radius: 8px;
        margin-bottom: 14px;
    }
    .plain-summary-box {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 18px;
        margin-bottom: 20px;
    }
    .metric-container {
        text-align: center;
        padding: 12px;
        background: white;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

# ================= SIDEBAR =================
with st.sidebar:
    st.image("https://img.icons8.com/color/96/shield.png", width=64)
    st.markdown(f"## **{APP_NAME}**")
    st.caption(f"{APP_TAGLINE} &nbsp;|&nbsp; `{APP_VERSION}`")
    st.markdown("---")

    st.markdown("### ⚙️ Privacy & AI Settings")
    enable_privacy = st.toggle("🛡️ Privacy Shield (Auto-Anonymizer)", value=True, help="Automatically redacts CNIC, phone numbers, bank details, and party names before sending text to the AI engine.")
    mask_money = st.checkbox("Mask Exact Financial Amounts", value=False, help="Replaces exact PKR figures with [CONFIDENTIAL_AMOUNT].")

    st.markdown("---")
    st.markdown("### 🇵🇰 Verified Legal Grounding")
    st.caption("• SECP Companies Act 2017\n• FBR Income Tax Ordinance 2001\n• Provincial Sales Tax on Services Acts\n• Contract Act 1872")

    st.markdown("---")
    api_status = "🟢 Active (Gemini 3.6 Flash)" if GEMINI_API_KEY else "🟡 Deterministic Mode (Offline)"
    st.caption(f"**AI Engine:** {api_status}")

# ================= MAIN HEADER =================
col_title, col_stats = st.columns([2.5, 1.5])
with col_title:
    st.markdown(f"<div class='main-header'>🛡️ {APP_NAME}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='sub-header'>{APP_TAGLINE} &nbsp;•&nbsp; <span class='shield-badge'>🔒 Privacy Shield Active</span></div>", unsafe_allow_html=True)

with col_stats:
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<div class='metric-container'><strong>Small Businesses</strong><br><span style='font-size:1.4rem; color:#2563EB;'>SMEs & Freelancers</span></div>", unsafe_allow_html=True)
    with c2:
        st.markdown("<div class='metric-container'><strong>Official Sources</strong><br><span style='font-size:1.4rem; color:#059669;'>SECP & FBR</span></div>", unsafe_allow_html=True)

# Tabs Navigation
tab_scanner, tab_checklist, tab_qa, tab_about = st.tabs([
    "📑 Contract Scanner & Privacy Shield",
    "✅ Smart Compliance Checklist",
    "💬 Legal & Tax Q&A Advisor",
    "ℹ️ About & Educational Guidance"
])

# ==============================================================================
# TAB 1: CONTRACT SCANNER & PRIVACY SHIELD
# ==============================================================================
with tab_scanner:
    st.markdown("### 📑 AI Commercial Contract Scanner with Privacy Shield")
    st.markdown("Upload any business agreement or choose a sample. The **Privacy Shield** will automatically redact confidential personal/company details, and the AI will highlight unfair clauses, missing protections, and payment traps in simple English.")

    # 1-Click Sample Selectors
    st.markdown("**⚡ Quick Test with Hackathon Samples:**")
    col_s1, col_s2, col_clear = st.columns([1.5, 1.5, 1])

    with col_s1:
        if st.button("🏢 Load Sample 1: Commercial Lease Agreement", use_container_width=True):
            st.session_state.current_contract_text = SAMPLE_1_LEASE_TEXT
            st.session_state.current_contract_title = SAMPLE_1_LEASE_TITLE
            st.session_state.analysis_report = None
            st.session_state.redaction_info = None
            st.rerun()

    with col_s2:
        if st.button("💻 Load Sample 2: Vendor & Service Agreement", use_container_width=True):
            st.session_state.current_contract_text = SAMPLE_2_VENDOR_TEXT
            st.session_state.current_contract_title = SAMPLE_2_VENDOR_TITLE
            st.session_state.analysis_report = None
            st.session_state.redaction_info = None
            st.rerun()

    with col_clear:
        if st.button("🔄 Clear Input", use_container_width=True):
            st.session_state.current_contract_text = ""
            st.session_state.current_contract_title = "Custom Agreement"
            st.session_state.analysis_report = None
            st.session_state.redaction_info = None
            st.rerun()

    st.markdown("---")

    # Document Input Mode
    col_input, col_shield_preview = st.columns([1.1, 0.9], gap="medium")

    with col_input:
        st.markdown(f"**Current Contract:** `{st.session_state.current_contract_title}`")
        
        # File Uploader (PDF, DOCX, TXT)
        uploaded_file = st.file_uploader("Upload Contract (PDF, DOCX, or TXT):", type=["pdf", "docx", "txt"], help="Upload your commercial contract or agreement.")
        if uploaded_file is not None:
            if uploaded_file.name.endswith(".pdf"):
                try:
                    import pypdf
                    reader = pypdf.PdfReader(uploaded_file)
                    extracted_text = ""
                    for page in reader.pages:
                        extracted_text += page.extract_text() or ""
                    st.session_state.current_contract_text = extracted_text
                    st.session_state.current_contract_title = uploaded_file.name
                    st.success(f"Extracted {len(reader.pages)} page(s) from {uploaded_file.name}")
                except Exception as e:
                    st.error(f"Error reading PDF: {e}")
            elif uploaded_file.name.endswith(".docx"):
                try:
                    import zipfile, xml.etree.ElementTree as ET
                    with zipfile.ZipFile(io.BytesIO(uploaded_file.read())) as z:
                        xml_content = z.read('word/document.xml')
                        tree = ET.fromstring(xml_content)
                        paragraphs = []
                        for p in tree.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p'):
                            texts = [node.text for node in p.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t') if node.text]
                            if texts:
                                paragraphs.append("".join(texts))
                        extracted_text = "\n\n".join(paragraphs)
                    st.session_state.current_contract_text = extracted_text
                    st.session_state.current_contract_title = uploaded_file.name
                    st.success(f"Extracted Word Document ({uploaded_file.name}) successfully!")
                except Exception as e:
                    st.error(f"Error reading Word document: {e}")
            else:
                st.session_state.current_contract_text = uploaded_file.read().decode("utf-8", errors="ignore")
                st.session_state.current_contract_title = uploaded_file.name

        # Text Area for editing or direct pasting
        contract_input = st.text_area(
            "Contract Text:",
            value=st.session_state.current_contract_text,
            height=300,
            placeholder="Paste your contract text here..."
        )
        st.session_state.current_contract_text = contract_input

        # Trigger Scan Button
        if st.button("🚀 Scan Agreement for Legal Risks & Traps", type="primary", use_container_width=True):
            if not contract_input.strip():
                st.warning("Please paste or load a contract first.")
            else:
                with st.spinner("1/2 Applying Privacy Shield (anonymizing sensitive details)..."):
                    if enable_privacy:
                        sanitized, counts = st.session_state.privacy_shield.anonymize(contract_input, mask_money=mask_money)
                        st.session_state.sanitized_text = sanitized
                        st.session_state.redaction_info = counts
                    else:
                        st.session_state.sanitized_text = contract_input
                        st.session_state.redaction_info = {}

                with st.spinner("2/2 Auditing legal clauses, missing protections, and tax considerations..."):
                    report = st.session_state.contract_scanner.analyze_contract(
                        st.session_state.sanitized_text,
                        contract_title=st.session_state.current_contract_title
                    )
                    st.session_state.analysis_report = report
                st.rerun()

    with col_shield_preview:
        st.markdown("**🛡️ Privacy Shield Live Inspection:**")
        if st.session_state.redaction_info:
            total_shielded = sum(st.session_state.redaction_info.values())
            st.success(f"✅ **{total_shielded} Confidential Items Anonymized** before analysis!")
            for cat, cnt in st.session_state.redaction_info.items():
                if cnt > 0:
                    st.caption(f"• **{cat}:** `{cnt} item(s) masked`")
        else:
            st.info("When you scan, Privacy Shield automatically detects and masks CNIC, Phone, Bank Account, and Party names before sending text to the AI engine.")

        if st.session_state.sanitized_text:
            with st.expander("🔍 View Anonymized Text Sent to AI", expanded=False):
                st.text_area("Sanitized Version:", value=st.session_state.sanitized_text, height=220, disabled=True)

    # ================= SCAN RESULTS DASHBOARD =================
    if st.session_state.analysis_report:
        report: ContractAnalysisReport = st.session_state.analysis_report
        st.markdown("---")
        st.markdown("## 📊 Comprehensive Contract Audit Report")

        # Top Summary Badges
        c_score, c_type, c_flags, c_missing = st.columns(4)
        
        # Color based on risk
        risk_color = "#DC2626" if report.overall_risk_score >= 70 else ("#D97706" if report.overall_risk_score >= 40 else "#059669")
        
        with c_score:
            st.markdown(f"""
            <div class='metric-container'>
                <span style='color:#64748B; font-size:0.85rem;'>OVERALL RISK RATING</span><br>
                <span style='font-size:1.9rem; font-weight:800; color:{risk_color};'>{report.overall_risk_score} / 100</span><br>
                <span style='font-weight:600; color:{risk_color};'>{report.overall_risk_level}</span>
            </div>
            """, unsafe_allow_html=True)
            
        with c_type:
            st.markdown(f"""
            <div class='metric-container'>
                <span style='color:#64748B; font-size:0.85rem;'>CONTRACT CLASSIFICATION</span><br>
                <span style='font-size:1.1rem; font-weight:700; color:#1E293B;'>{report.contract_type}</span><br>
                <span style='color:#059669; font-size:0.8rem;'>Commercial Standard</span>
            </div>
            """, unsafe_allow_html=True)

        with c_flags:
            st.markdown(f"""
            <div class='metric-container'>
                <span style='color:#64748B; font-size:0.85rem;'>RED FLAGS IDENTIFIED</span><br>
                <span style='font-size:1.9rem; font-weight:800; color:#DC2626;'>{len(report.red_flags)}</span><br>
                <span style='color:#DC2626; font-size:0.8rem;'>High & Medium Traps</span>
            </div>
            """, unsafe_allow_html=True)

        with c_missing:
            st.markdown(f"""
            <div class='metric-container'>
                <span style='color:#64748B; font-size:0.85rem;'>MISSING PROTECTIONS</span><br>
                <span style='font-size:1.9rem; font-weight:800; color:#D97706;'>{len(report.missing_protections)}</span><br>
                <span style='color:#D97706; font-size:0.8rem;'>Omitted Clauses</span>
            </div>
            """, unsafe_allow_html=True)

        # Plain English Executive Summary
        st.markdown("### 💡 Plain English Summary (What this means for you)")
        with st.container():
            st.markdown("<div class='plain-summary-box'>", unsafe_allow_html=True)
            for bullet in report.plain_english_summary:
                st.markdown(f"• {bullet}")
            st.markdown("</div>", unsafe_allow_html=True)

        # Categorized Red Flags
        st.markdown(f"### 🚨 Potentially Risky, Unclear, or Trapping Clauses ({len(report.red_flags)} Found)")
        for idx, flag in enumerate(report.red_flags):
            card_class = "risk-card-high" if flag.risk_level == "High" else "risk-card-medium"
            badge_color = "#991B1B" if flag.risk_level == "High" else "#92400E"
            badge_bg = "#FEE2E2" if flag.risk_level == "High" else "#FEF3C7"
            
            with st.container():
                st.markdown(f"""
                <div class='{card_class}'>
                    <div style='display:flex; justify-content:space-between; align-items:center;'>
                        <h4 style='margin:0; color:#1E293B;'>{flag.clause_reference}</h4>
                        <span style='background:{badge_bg}; color:{badge_color}; padding:2px 10px; border-radius:12px; font-weight:700; font-size:0.8rem;'>
                            {flag.risk_level} Risk &nbsp;|&nbsp; {flag.category}
                        </span>
                    </div>
                    <p style='color:#334155; margin:10px 0 6px 0;'><strong>⚠️ Problem / Trap:</strong> {flag.problem_explanation}</p>
                    <p style='color:#065F46; margin:0;'><strong>💡 Suggested Action / Revision:</strong> {flag.suggested_revision}</p>
                </div>
                """, unsafe_allow_html=True)

        # Missing Protections & Positive Clauses
        col_missing_box, col_positive_box = st.columns(2)
        with col_missing_box:
            st.markdown("### 🔍 Critical Missing Protections")
            st.markdown("<div class='plain-summary-box'>", unsafe_allow_html=True)
            for m in report.missing_protections:
                st.markdown(f"⚠️ **Missing:** {m}")
            st.markdown("</div>", unsafe_allow_html=True)

        with col_positive_box:
            st.markdown("### ✅ Positive / Fair Clauses")
            st.markdown("<div class='plain-summary-box'>", unsafe_allow_html=True)
            for p in report.positive_clauses:
                st.markdown(f"✅ **Fair Term:** {p}")
            st.markdown("</div>", unsafe_allow_html=True)

        # Download Full Report
        report_text = f"# BizShield AI - Contract Risk Audit\n\nContract: {st.session_state.current_contract_title}\nOverall Risk: {report.overall_risk_score}/100 ({report.overall_risk_level})\n\n## Plain English Summary\n" + "\n".join([f"- {b}" for b in report.plain_english_summary]) + "\n\n## Red Flags\n"
        for rf in report.red_flags:
            report_text += f"\n### {rf.clause_reference} [{rf.risk_level} Risk]\n- Issue: {rf.problem_explanation}\n- Suggested Revision: {rf.suggested_revision}\n"
        report_text += "\n## Missing Protections\n" + "\n".join([f"- {m}" for m in report.missing_protections])
        
        st.download_button(
            label="📥 Download Comprehensive Audit Report (.md)",
            data=report_text,
            file_name=f"bizshield_audit_{st.session_state.current_contract_title.replace(' ', '_')}.md",
            mime="text/markdown"
        )


# ==============================================================================
# TAB 2: SMART COMPLIANCE CHECKLIST
# ==============================================================================
with tab_checklist:
    st.markdown("### ✅ Smart Business & Tax Compliance Checklist")
    st.markdown("Select your business structure and profile below. BizShield AI generates an interactive, step-by-step regulatory roadmap covering SECP entity registration, FBR NTN tax compliance, provincial sales tax, and ongoing bookkeeping.")

    col_prof1, col_prof2, col_prof3 = st.columns(3)
    with col_prof1:
        entity_choice = st.selectbox(
            "Business Legal Structure:",
            [
                "Sole Proprietorship / Freelancer",
                "Single Member Company (SMC-Pvt Ltd)",
                "Private Limited Company (Pvt Ltd)",
                "Partnership / Association of Persons (AOP)"
            ],
            index=0
        )

    with col_prof2:
        industry_choice = st.selectbox(
            "Industry / Activity:",
            [
                "IT & Digital Services / Freelancing",
                "Retail & E-Commerce",
                "Consulting & Professional Services",
                "Manufacturing & Trading"
            ],
            index=0
        )

    with col_prof3:
        has_staff = st.checkbox("Have Employees / Staff?", value=False, help="Requires payroll withholding tax and EOBI compliance.")
        is_exporter = st.checkbox("Software / Services Exporter?", value=True, help="Qualifies for 0.25% PSEB concessionary tax rate.")

    # Generate Checklist
    checklist_tasks = st.session_state.compliance_engine.generate_checklist(
        entity_type=entity_choice,
        industry=industry_choice,
        has_employees=has_staff,
        is_exporter=is_exporter
    )

    total_tasks = len(checklist_tasks)
    completed_count = sum(1 for t in checklist_tasks if t["task_id"] in st.session_state.compliance_checked)
    progress_pct = (completed_count / total_tasks) if total_tasks > 0 else 0.0

    st.markdown("---")
    c_p1, c_p2 = st.columns([3, 1])
    with c_p1:
        st.markdown(f"#### 📋 Compliance Roadmap: `{completed_count} of {total_tasks} Tasks Completed`")
        st.progress(progress_pct)
    with c_p2:
        st.markdown(f"<div style='text-align:right; font-size:1.3rem; font-weight:800; color:#059669;'>{int(progress_pct*100)}% Compliant</div>", unsafe_allow_html=True)

    # Render Task Cards
    for task in checklist_tasks:
        tid = task["task_id"]
        is_done = tid in st.session_state.compliance_checked
        
        with st.expander(f"{'✅' if is_done else '⚪'} [{task['priority']}] {task['title']} — ({task['authority']})", expanded=(not is_done)):
            c_check, c_desc = st.columns([0.15, 0.85])
            with c_check:
                checked = st.checkbox("Done", value=is_done, key=f"chk_{tid}")
                if checked and tid not in st.session_state.compliance_checked:
                    st.session_state.compliance_checked.add(tid)
                    st.rerun()
                elif not checked and tid in st.session_state.compliance_checked:
                    st.session_state.compliance_checked.remove(tid)
                    st.rerun()
            with c_desc:
                st.markdown(f"**Description:** {task['description']}")
                st.caption(f"**Timeline:** ⏱️ {task['timeline']} &nbsp;|&nbsp; **Category:** {task['category']}")
                st.markdown(f"**📚 Official Statutory Grounding:** *{task['official_source']}*")


# ==============================================================================
# TAB 3: LEGAL & TAX Q&A ADVISOR
# ==============================================================================
with tab_qa:
    st.markdown("### 💬 Legal & Tax Q&A Advisor")
    st.markdown("Ask any legal, contractual, or tax question affecting small businesses in Pakistan. BizShield AI provides structured, educational guidance grounded in verified official statutes.")

    # Quick Suggestion Chips
    st.markdown("**💡 Common Questions Asked by Small Business Owners (Click to ask):**")
    chip_cols = st.columns(len(SAMPLE_QA_QUESTIONS))
    selected_preset = None

    for i, q_text in enumerate(SAMPLE_QA_QUESTIONS):
        with chip_cols[i]:
            btn_label = q_text[:28] + "..." if len(q_text) > 28 else q_text
            if st.button(btn_label, key=f"chip_{i}", use_container_width=True, help=q_text):
                selected_preset = q_text

    # User Query Input
    query_input = st.text_input(
        "Or type your question here:",
        value=selected_preset or "",
        placeholder="e.g., Can a landlord increase rent without notice during a commercial lease?"
    )

    if st.button("🔍 Ask BizShield AI", type="primary"):
        if query_input.strip():
            with st.spinner("Analyzing verified Pakistani statutory sources (SECP, FBR, Contract Act)..."):
                response_data = st.session_state.qa_advisor.answer_question(query_input.strip())
                st.session_state.chat_history.append((query_input.strip(), response_data["answer"]))
        else:
            st.warning("Please type a question or select one of the suggestion chips.")

    # Render Chat History
    if st.session_state.chat_history:
        st.markdown("---")
        st.markdown("### 📜 Conversation & Legal Advice History")
        for q, ans in reversed(st.session_state.chat_history):
            with st.chat_message("user"):
                st.write(q)
            with st.chat_message("assistant", avatar="🛡️"):
                st.markdown(ans)


# ==============================================================================
# TAB 4: ABOUT & EDUCATIONAL GUIDANCE
# ==============================================================================
with tab_about:
    st.markdown("## 🛡️ About BizShield AI")
    st.markdown("""
    **BizShield AI** is an AI-powered legal and tax assistant designed specifically for small business owners, freelancers, and early-stage entrepreneurs in Pakistan.

    ### 🎯 The Problem
    Over 90% of small businesses and solo entrepreneurs struggle with:
    1. Signing contracts with hidden clauses and dangerous liability traps.
    2. Navigating corporate registration (SECP) and tax obligations (FBR, Active Taxpayer List, Provincial Sales Tax).
    3. Inability to afford expensive corporate law firms or chartered accountant retainers.

    ### 💡 The Solution
    BizShield AI provides:
    - **Contract Scanner & Privacy Shield:** Automatically removes confidential party details and audits contracts for 10 common traps.
    - **Smart Compliance Checklist:** Customized registration and annual tax filing roadmaps.
    - **Legal & Tax Q&A:** Accurate, structured educational answers referencing official Pakistani statutes.

    ---

    ### ⚖️ Important Principle & Disclaimer
    > **Educational Guidance Only:**  
    > BizShield AI is designed to provide **informational and educational guidance** to help small business owners make informed decisions. It does not constitute formal attorney-client legal advice or licensed tax practice. All claims are grounded in verified official sources (SECP Companies Act 2017, FBR Income Tax Ordinance 2001, Contract Act 1872).
    """)
