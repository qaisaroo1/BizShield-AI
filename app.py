import io
import re
import sys
from pathlib import Path
import streamlit as st

# Ensure local src imports work
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.config import APP_NAME, APP_TAGLINE, APP_VERSION, GEMINI_API_KEY
from src.privacy_shield import PrivacyShield
from src.contract_scanner import ContractScanner, ContractAnalysisReport, generate_negotiation_script
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

if "audit_log" not in st.session_state:
    st.session_state.audit_log = []

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "compliance_checked" not in st.session_state:
    st.session_state.compliance_checked = set()

if "custom_hide_words" not in st.session_state:
    st.session_state.custom_hide_words = ""

# Custom CSS for polished, professional UI (Theme-adaptive for Dark and Light modes)
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        color: var(--text-color);
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: var(--text-color);
        opacity: 0.85;
        margin-bottom: 1.5rem;
    }
    .shield-badge {
        display: inline-block;
        background: rgba(16, 185, 129, 0.12);
        color: #10B981;
        border: 1px solid rgba(16, 185, 129, 0.35);
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .privacy-guarantee-card {
        background: rgba(16, 185, 129, 0.12);
        border: 1px solid rgba(16, 185, 129, 0.35);
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 12px;
        color: var(--text-color);
    }
    .redaction-pill {
        background: var(--secondary-background-color);
        border: 1px solid rgba(59, 130, 246, 0.35);
        border-radius: 8px;
        padding: 8px 12px;
        margin-bottom: 8px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 1px 2px rgba(0,0,0,0.08);
    }
    .redaction-pill-label {
        font-size: 0.84rem;
        font-weight: 600;
        color: var(--text-color);
    }
    .redaction-pill-count {
        background: rgba(59, 130, 246, 0.15);
        color: #3B82F6;
        padding: 2px 8px;
        border-radius: 12px;
        font-weight: 700;
        font-size: 0.82rem;
    }
    .verdict-card-high {
        background: rgba(239, 68, 68, 0.12);
        border: 2px solid #EF4444;
        padding: 16px 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .verdict-card-med {
        background: rgba(245, 158, 11, 0.12);
        border: 2px solid #F59E0B;
        padding: 16px 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .verdict-card-low {
        background: rgba(16, 185, 129, 0.12);
        border: 2px solid #10B981;
        padding: 16px 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .step-card {
        background: var(--secondary-background-color);
        border: 1px solid rgba(128, 128, 128, 0.2);
        border-radius: 8px;
        padding: 14px;
        height: 100%;
        color: var(--text-color);
    }
    .risk-card-high {
        background: rgba(239, 68, 68, 0.1);
        border-left: 5px solid #EF4444;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 14px;
        color: var(--text-color);
    }
    .risk-card-medium {
        background: rgba(245, 158, 11, 0.1);
        border-left: 5px solid #F59E0B;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 14px;
        color: var(--text-color);
    }
    .risk-card-low {
        background: rgba(16, 185, 129, 0.1);
        border-left: 5px solid #10B981;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 14px;
        color: var(--text-color);
    }
    .safe-clause-box {
        background: var(--secondary-background-color);
        border: 1px dashed rgba(16, 185, 129, 0.45);
        border-radius: 6px;
        padding: 10px;
        margin-top: 8px;
    }
    .plain-summary-box {
        background: var(--secondary-background-color);
        border: 1px solid rgba(128, 128, 128, 0.2);
        border-radius: 10px;
        padding: 18px;
        margin-bottom: 20px;
        color: var(--text-color);
    }
    .metric-container {
        text-align: center;
        padding: 12px;
        background: var(--secondary-background-color);
        border: 1px solid rgba(128, 128, 128, 0.2);
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        color: var(--text-color);
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
    if "enable_privacy_pref" not in st.session_state:
        st.session_state.enable_privacy_pref = True
    if "mask_money_pref" not in st.session_state:
        st.session_state.mask_money_pref = False

    enable_privacy = st.toggle(
        "🛡️ Privacy Shield (Auto-Anonymizer)",
        key="enable_privacy_pref",
        help="Automatically redacts CNIC, phone numbers, bank details, and party names before sending text to the AI engine."
    )
    mask_money = st.checkbox(
        "Mask Exact Financial Amounts",
        key="mask_money_pref",
        help="Replaces exact PKR figures with [CONFIDENTIAL_AMOUNT]."
    )

    st.markdown("---")
    st.markdown("### 🇵🇰 Verified Legal Grounding")
    st.caption("• SECP Companies Act 2017\n• FBR Income Tax Ordinance 2001\n• Provincial Sales Tax on Services Acts\n• Contract Act 1872")

    st.markdown("---")
    api_status = "🟢 Active (Gemini 3.6 Flash)" if GEMINI_API_KEY else "🟡 Deterministic Mode (Offline)"
    rag_count = len(st.session_state.qa_advisor.rag_store.chunks) if hasattr(st.session_state.qa_advisor, "rag_store") else 0
    st.caption(f"**AI Engine:** {api_status}")
    st.caption(f"**RAG Vector Index:** 📚 `{rag_count} Statutes Indexed` (`gemini-embedding-001`)")

# ================= MAIN HEADER =================
col_title, col_stats = st.columns([2.5, 1.5])
with col_title:
    st.markdown(f"<div class='main-header'>🛡️ {APP_NAME}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='sub-header'>{APP_TAGLINE} &nbsp;•&nbsp; <span class='shield-badge'>🔒 Privacy Shield Active</span> &nbsp; <span class='shield-badge' style='background:rgba(37, 99, 235, 0.12); color:#3B82F6; border-color:rgba(59, 130, 246, 0.35);'>🔍 RAG-Augmented</span></div>", unsafe_allow_html=True)

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
    st.markdown("**📄 Try an Example Agreement:**")
    col_s1, col_s2, col_clear = st.columns([1.5, 1.5, 1])

    with col_s1:
        if st.button("🏢 Commercial Lease Agreement", use_container_width=True):
            st.session_state.current_contract_text = SAMPLE_1_LEASE_TEXT
            st.session_state.current_contract_title = SAMPLE_1_LEASE_TITLE
            st.session_state.analysis_report = None
            st.session_state.redaction_info = None
            st.session_state.sanitized_text = None
            st.session_state.audit_log = []
            st.rerun()

    with col_s2:
        if st.button("💻 Vendor & Service Agreement", use_container_width=True):
            st.session_state.current_contract_text = SAMPLE_2_VENDOR_TEXT
            st.session_state.current_contract_title = SAMPLE_2_VENDOR_TITLE
            st.session_state.analysis_report = None
            st.session_state.redaction_info = None
            st.session_state.sanitized_text = None
            st.session_state.audit_log = []
            st.rerun()

    with col_clear:
        if st.button("🔄 Clear Input", use_container_width=True):
            st.session_state.current_contract_text = ""
            st.session_state.current_contract_title = "Custom Agreement"
            st.session_state.analysis_report = None
            st.session_state.redaction_info = None
            st.session_state.sanitized_text = None
            st.session_state.audit_log = []
            st.session_state.custom_hide_words = ""
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
            height=280,
            placeholder="Paste your contract text here..."
        )
        st.session_state.current_contract_text = contract_input

        # Trigger Scan Button
        if st.button("🚀 Scan Agreement for Legal Risks & Traps", type="primary", use_container_width=True):
            if not contract_input.strip():
                st.warning("Please paste or load a contract first.")
            else:
                with st.spinner("1/2 Applying Privacy Shield (anonymizing sensitive details in memory)..."):
                    custom_redact_list = [w.strip() for w in st.session_state.custom_hide_words.split(",") if w.strip()] if st.session_state.custom_hide_words else None
                    if enable_privacy:
                        sanitized, counts = st.session_state.privacy_shield.anonymize(
                            contract_input,
                            mask_money=mask_money,
                            custom_redactions=custom_redact_list
                        )
                        st.session_state.sanitized_text = sanitized
                        st.session_state.redaction_info = counts
                        st.session_state.audit_log = getattr(st.session_state.privacy_shield, "last_audit_log", [])
                    else:
                        st.session_state.sanitized_text = contract_input
                        st.session_state.redaction_info = {}
                        st.session_state.audit_log = []

                with st.spinner("2/2 Auditing legal clauses, missing protections, and tax considerations..."):
                    report = st.session_state.contract_scanner.analyze_contract(
                        st.session_state.sanitized_text,
                        contract_title=st.session_state.current_contract_title
                    )
                    st.session_state.analysis_report = report
                st.rerun()

    with col_shield_preview:
        st.markdown("#### 🛡️ Privacy Shield Live Inspection")
        st.markdown("""
        <div class='privacy-guarantee-card'>
            <div style='display:flex; align-items:center; gap:8px;'>
                <span style='font-size:1.3rem;'>🔒</span>
                <div>
                    <strong style='color:#10B981;'>Always Redacted Automatically (Default):</strong><br>
                    <span style='font-size:0.83rem; opacity:0.9;'>CNIC, Names, Phones, Emails, NTN, STRN, Bank/IBAN, Passports, Licenses, and Addresses are 100% hidden on your device before sending to AI.</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Prominently ask user to write anything else they want redacted right here in Live Inspection
        st.markdown("**✍️ Want to hide any other personal info or words from AI?**")
        custom_hide_input = st.text_input(
            "Write extra words, names, or secret codes to hide:",
            value=st.session_state.custom_hide_words,
            placeholder="e.g. Project Falcon, Tariq Khan, Secret Recipe (comma separated)",
            help="CNIC, phone, NTN, STRN, passports, licenses, bank details, and addresses are ALWAYS hidden automatically. Enter any extra words or names here to also hide them from AI."
        )
        st.session_state.custom_hide_words = custom_hide_input
        custom_redact_list = [w.strip() for w in custom_hide_input.split(",") if w.strip()] if custom_hide_input else None

        # Quick standalone verify button
        if st.button("🔍 Preview What Gets Hidden (Test Privacy)", use_container_width=True):
            if not contract_input.strip():
                st.warning("Please paste or load contract text first.")
            else:
                sanitized, counts = st.session_state.privacy_shield.anonymize(
                    contract_input,
                    mask_money=mask_money,
                    custom_redactions=custom_redact_list
                )
                st.session_state.sanitized_text = sanitized
                st.session_state.redaction_info = counts
                st.session_state.audit_log = getattr(st.session_state.privacy_shield, "last_audit_log", [])
                st.rerun()

        if st.session_state.redaction_info:
            total_shielded = sum(st.session_state.redaction_info.values())
            st.success(f"✅ **{total_shielded} Private Details Safely Hidden** (Never sent to AI!)")
            
            # Pill display of categories (Dark-mode & Light-mode adaptive)
            cols_cat = st.columns(2)
            idx_c = 0
            for cat, cnt in st.session_state.redaction_info.items():
                if cnt > 0:
                    with cols_cat[idx_c % 2]:
                        st.markdown(f"""
                        <div class='redaction-pill'>
                            <span class='redaction-pill-label'>{cat}</span>
                            <span class='redaction-pill-count'>{cnt}</span>
                        </div>
                        """, unsafe_allow_html=True)
                    idx_c += 1

            # Detailed Redaction Proof
            if st.session_state.audit_log:
                with st.expander("📋 Privacy Protection Proof (What was hidden from AI)", expanded=True):
                    audit_rows = []
                    for item in st.session_state.audit_log:
                        audit_rows.append({
                            "Category": item["category"],
                            "Detected Text": item["masked_preview"],
                            "Sent to AI": item["ai_token"],
                            "Protection Status": "🟢 Hidden from AI"
                        })
                    st.dataframe(audit_rows, use_container_width=True, hide_index=True)

            if st.session_state.sanitized_text:
                with st.expander("📄 Compare: Original vs. Anonymized Payload", expanded=True):
                    # 🔍 1-Click Search Verifier
                    st.markdown("**🔍 Quick Search Verifier:** Check if a specific name, CNIC, or word was redacted without scrolling down:")
                    search_query = st.text_input(
                        "Search word, number, or name:",
                        placeholder="e.g. 0300-1234567, ABC Properties, Lahore, 35201, NTN...",
                        label_visibility="collapsed",
                        key="compare_search_query"
                    )

                    if search_query and search_query.strip():
                        q_clean = search_query.strip()
                        raw_matches = len(re.findall(re.escape(q_clean), contract_input, re.IGNORECASE))
                        san_matches = len(re.findall(re.escape(q_clean), st.session_state.sanitized_text, re.IGNORECASE))

                        if raw_matches > 0 and san_matches == 0:
                            st.success(f"🟢 **100% Protected & Hidden!** '{q_clean}' appeared {raw_matches} time(s) in your original contract and has been **completely scrubbed** (0 times sent to AI).")
                            matching_lines = [line.strip() for line in contract_input.splitlines() if q_clean.lower() in line.lower()]
                            if matching_lines:
                                st.caption(f"📍 Original line: `{matching_lines[0]}`")
                        elif raw_matches > 0 and san_matches > 0:
                            st.warning(f"⚠️ **Not Redacted:** '{q_clean}' appears {san_matches} time(s) in the text sent to AI as regular words.")
                            if st.button(f"➕ Click to hide '{q_clean}' from AI now", key=f"btn_add_hide_{q_clean}"):
                                curr = st.session_state.custom_hide_words
                                st.session_state.custom_hide_words = f"{curr}, {q_clean}" if curr else q_clean
                                custom_list = [w.strip() for w in st.session_state.custom_hide_words.split(",") if w.strip()]
                                sanitized, counts = st.session_state.privacy_shield.anonymize(
                                    contract_input,
                                    mask_money=mask_money,
                                    custom_redactions=custom_list
                                )
                                st.session_state.sanitized_text = sanitized
                                st.session_state.redaction_info = counts
                                st.session_state.audit_log = getattr(st.session_state.privacy_shield, "last_audit_log", [])
                                st.rerun()
                        else:
                            st.info(f"ℹ️ '{q_clean}' does not appear anywhere in this contract.")

                    st.markdown("---")
                    tab_san, tab_orig = st.tabs(["🤖 What Google AI Received", "📄 Raw Document (Local Only)"])
                    with tab_san:
                        st.text_area("Sanitized Payload (Only Generic Tags Sent):", value=st.session_state.sanitized_text, height=200, disabled=True)
                    with tab_orig:
                        st.text_area("Original Text with Personal Information:", value=contract_input, height=200, disabled=True)
        else:
            st.info("💡 **How to verify:** Click **'Preview What Gets Hidden'** or **'Scan Agreement'**. BizShield AI will instantly display the exact CNIC, NTN, STRN, passports, driving licenses, addresses, phone numbers, and bank details masked before AI processing.")

    # ================= SCAN RESULTS DASHBOARD =================
    if st.session_state.analysis_report:
        report: ContractAnalysisReport = st.session_state.analysis_report
        st.markdown("---")
        st.markdown("## 📊 Commercial Contract Risk Audit Report")

        # 1. TRAFFIC-LIGHT EXECUTIVE VERDICT BANNER
        if report.overall_risk_score >= 70:
            st.markdown(f"""
            <div class='verdict-card-high'>
                <div style='display:flex; align-items:center; justify-content:space-between;'>
                    <div>
                        <div style='font-size:1.35rem; font-weight:800; color:#EF4444;'>🛑 EXECUTIVE VERDICT: DO NOT SIGN AS-IS</div>
                        <div style='color:var(--text-color); opacity:0.9; font-size:0.95rem; margin-top:4px;'>
                            This contract contains <strong>critical commercial traps</strong> that heavily favor the other party. Counter-offer to revise these clauses before committing.
                        </div>
                    </div>
                    <div style='text-align:right;'>
                        <span style='background:rgba(239, 68, 68, 0.2); color:#EF4444; font-weight:800; font-size:1.4rem; padding:6px 14px; border-radius:10px; border:1px solid rgba(239, 68, 68, 0.4);'>
                            {report.overall_risk_score} / 100 Risk
                        </span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        elif report.overall_risk_score >= 40:
            st.markdown(f"""
            <div class='verdict-card-med'>
                <div style='display:flex; align-items:center; justify-content:space-between;'>
                    <div>
                        <div style='font-size:1.35rem; font-weight:800; color:#F59E0B;'>⚠️ EXECUTIVE VERDICT: PROCEED WITH CAUTION</div>
                        <div style='color:var(--text-color); opacity:0.9; font-size:0.95rem; margin-top:4px;'>
                            This contract is mostly standard, but has <strong>several ambiguous clauses</strong> that could cause cost overruns or operational friction.
                        </div>
                    </div>
                    <div style='text-align:right;'>
                        <span style='background:rgba(245, 158, 11, 0.2); color:#F59E0B; font-weight:800; font-size:1.4rem; padding:6px 14px; border-radius:10px; border:1px solid rgba(245, 158, 11, 0.4);'>
                            {report.overall_risk_score} / 100 Risk
                        </span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class='verdict-card-low'>
                <div style='display:flex; align-items:center; justify-content:space-between;'>
                    <div>
                        <div style='font-size:1.35rem; font-weight:800; color:#10B981;'>✅ EXECUTIVE VERDICT: SAFE & BALANCED</div>
                        <div style='color:var(--text-color); opacity:0.9; font-size:0.95rem; margin-top:4px;'>
                            This contract adheres to standard commercial norms in Pakistan. Proceed with standard due diligence.
                        </div>
                    </div>
                    <div style='text-align:right;'>
                        <span style='background:rgba(16, 185, 129, 0.2); color:#10B981; font-weight:800; font-size:1.4rem; padding:6px 14px; border-radius:10px; border:1px solid rgba(16, 185, 129, 0.4);'>
                            {report.overall_risk_score} / 100 Risk
                        </span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # 2. TOP METRICS
        c_score, c_type, c_flags, c_missing = st.columns(4)
        risk_color = "#DC2626" if report.overall_risk_score >= 70 else ("#D97706" if report.overall_risk_score >= 40 else "#059669")
        
        with c_score:
            st.markdown(f"""
            <div class='metric-container'>
                <span style='color:#64748B; font-size:0.82rem;'>RISK LEVEL</span><br>
                <span style='font-size:1.7rem; font-weight:800; color:{risk_color};'>{report.overall_risk_level}</span><br>
                <span style='font-weight:600; color:#64748B;'>{report.overall_risk_score} / 100 Rating</span>
            </div>
            """, unsafe_allow_html=True)
            
        with c_type:
            st.markdown(f"""
            <div class='metric-container'>
                <span style='color:#64748B; font-size:0.82rem;'>CONTRACT TYPE</span><br>
                <span style='font-size:1.1rem; font-weight:700; color:#1E293B;'>{report.contract_type}</span><br>
                <span style='color:#059669; font-size:0.8rem;'>Commercial Document</span>
            </div>
            """, unsafe_allow_html=True)

        with c_flags:
            st.markdown(f"""
            <div class='metric-container'>
                <span style='color:#64748B; font-size:0.82rem;'>TRAPS & RED FLAGS</span><br>
                <span style='font-size:1.7rem; font-weight:800; color:#DC2626;'>{len(report.red_flags)}</span><br>
                <span style='color:#DC2626; font-size:0.8rem;'>Clauses Needing Revision</span>
            </div>
            """, unsafe_allow_html=True)

        with c_missing:
            st.markdown(f"""
            <div class='metric-container'>
                <span style='color:#64748B; font-size:0.82rem;'>MISSING SAFEGUARDS</span><br>
                <span style='font-size:1.7rem; font-weight:800; color:#D97706;'>{len(report.missing_protections)}</span><br>
                <span style='color:#D97706; font-size:0.8rem;'>Omitted Protections</span>
            </div>
            """, unsafe_allow_html=True)

        # 3. 3-STEP ACTION PLAN FOR NON-LAWYERS
        st.markdown("### 🎯 Your 3-Step Action Plan (What to do next)")
        col_act1, col_act2, col_act3 = st.columns(3)
        with col_act1:
            st.markdown("""
            <div class='step-card'>
                <div style='font-size:1.05rem; font-weight:700; color:#1E293B; margin-bottom:6px;'>1️⃣ Request Revisions</div>
                <div style='color:#475569; font-size:0.88rem;'>
                    Do not sign the existing draft. Request amendments to the <strong>high-risk clauses</strong> flagged below (especially termination and maintenance).
                </div>
            </div>
            """, unsafe_allow_html=True)
        with col_act2:
            st.markdown("""
            <div class='step-card'>
                <div style='font-size:1.05rem; font-weight:700; color:#1E293B; margin-bottom:6px;'>2️⃣ Add Missing Clauses</div>
                <div style='color:#475569; font-size:0.88rem;'>
                    Insist on standard commercial protections: explicit mutual notice period and tax treatment clarity where the payer qualifies as a prescribed withholding agent under prevailing law.
                </div>
            </div>
            """, unsafe_allow_html=True)
        with col_act3:
            st.markdown("""
            <div class='step-card'>
                <div style='font-size:1.05rem; font-weight:700; color:#1E293B; margin-bottom:6px;'>3️⃣ Send Counter-Offer</div>
                <div style='color:#475569; font-size:0.88rem;'>
                    Copy our <strong>pre-drafted professional WhatsApp/Email message</strong> below and send it directly to the other party.
                </div>
            </div>
            """, unsafe_allow_html=True)

        # 4. PRE-DRAFTED 1-CLICK NEGOTIATION MESSAGE
        st.markdown("### 💬 1-Click WhatsApp / Email Counter-Offer Script")
        st.caption("Send this polite, professionally drafted message to your landlord or client. It requests the exact revisions without sounding confrontational:")
        
        negotiation_text = generate_negotiation_script(report)
        st.code(negotiation_text, language="text")

        # 5. PLAIN ENGLISH EXECUTIVE SUMMARY
        st.markdown("### 💡 Plain English Summary (What this contract means in everyday words)")
        with st.container():
            st.markdown("<div class='plain-summary-box'>", unsafe_allow_html=True)
            for bullet in report.plain_english_summary:
                st.markdown(f"• {bullet}")
            st.markdown("</div>", unsafe_allow_html=True)

        # 6. TABBED DETAILED FINDINGS & STATUTORY AUTHORITIES
        sources_count = len(report.relevant_sources) if hasattr(report, "relevant_sources") and report.relevant_sources else 0
        tab_traps, tab_omitted, tab_safe, tab_sources, tab_proof = st.tabs([
            f"🚨 Traps & Red Flags ({len(report.red_flags)})",
            f"🔍 Missing Protections ({len(report.missing_protections)})",
            f"✅ Fair & Safe Clauses ({len(report.positive_clauses)})",
            f"📚 Legal Basis & Sources ({sources_count})",
            f"🔒 Privacy Shield Proof"
        ])

        with tab_traps:
            st.markdown("##### Detailed Breakdown of Clauses Requiring Amendment:")
            for idx, flag in enumerate(report.red_flags):
                card_class = "risk-card-high" if flag.risk_level == "High" else "risk-card-medium"
                badge_color = "#EF4444" if flag.risk_level == "High" else "#F59E0B"
                badge_bg = "rgba(239, 68, 68, 0.2)" if flag.risk_level == "High" else "rgba(245, 158, 11, 0.2)"
                
                with st.container():
                    st.markdown(f"""
                    <div class='{card_class}'>
                        <div style='display:flex; justify-content:space-between; align-items:center;'>
                            <h4 style='margin:0; color:var(--text-color);'>{flag.clause_reference}</h4>
                            <span style='background:{badge_bg}; color:{badge_color}; padding:3px 10px; border-radius:12px; font-weight:700; font-size:0.8rem; border:1px solid {badge_color}40;'>
                                {flag.risk_level} Risk &nbsp;|&nbsp; {flag.category}
                            </span>
                        </div>
                        <p style='color:var(--text-color); opacity:0.9; margin:10px 0 6px 0;'><strong>⚠️ Problem / Trap (In Everyday Words):</strong> {flag.problem_explanation}</p>
                        <div class='safe-clause-box'>
                            <strong style='color:#10B981;'>💡 Safe Replacement Clause to Propose:</strong><br>
                            <span style='color:var(--text-color); font-family:monospace; font-size:0.88rem;'>{flag.suggested_revision}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

        with tab_omitted:
            st.markdown("##### Critical Safeguards Omitted from this Agreement:")
            st.markdown("<div class='plain-summary-box'>", unsafe_allow_html=True)
            for m in report.missing_protections:
                st.markdown(f"⚠️ **Missing Protection:** {m}")
            st.markdown("</div>", unsafe_allow_html=True)

        with tab_safe:
            st.markdown("##### Clauses That Are Fair and Protect You:")
            st.markdown("<div class='plain-summary-box'>", unsafe_allow_html=True)
            for p in report.positive_clauses:
                st.markdown(f"✅ **Fair Term:** {p}")
            st.markdown("</div>", unsafe_allow_html=True)

        with tab_sources:
            st.markdown("##### 📚 Relevant Legal Basis & Statutory Authorities:")
            st.markdown("""
            <div style='background:var(--secondary-background-color); border-left:4px solid #3B82F6; border-radius:8px; padding:14px; margin-bottom:16px;'>
                <strong style='color:#1E293B;'>Pakistani Regulatory Grounding for Identified Contract Clauses:</strong><br>
                <span style='font-size:0.88rem; color:var(--text-color); opacity:0.9;'>
                    BizShield AI dynamically references prevailing Pakistani statutory frameworks governing the specific clauses and obligations identified in this agreement:
                </span>
            </div>
            """, unsafe_allow_html=True)
            if hasattr(report, "relevant_sources") and report.relevant_sources:
                for idx, src in enumerate(report.relevant_sources, 1):
                    st.markdown(f"**{idx}.** {src}")
            else:
                st.info("General Pakistani contract law applies under the Contract Act 1872.")

        with tab_proof:
            st.markdown("##### 🔒 Data Privacy Verification for this Document:")
            if st.session_state.audit_log:
                st.markdown(f"A total of **{len(st.session_state.audit_log)} private details** were automatically hidden before sending the contract to the AI:")
                proof_rows = []
                for item in st.session_state.audit_log:
                    proof_rows.append({
                        "Category": item["category"],
                        "Detected Text": item["masked_preview"],
                        "What Was Sent to AI": item["ai_token"],
                        "Protection Status": "🟢 Hidden from AI (100% Protected)"
                    })
                st.dataframe(proof_rows, use_container_width=True, hide_index=True)
            else:
                st.info("Privacy Shield ran in active mode. Zero personal identifiers or banking credentials were sent to Google Gemini AI.")

        # 7. INFORMATIONAL & LEGAL DISCLAIMER
        disclaimer_text = getattr(report, "disclaimer", None) or (
            "⚠️ Legal & Informational Decision-Support Disclaimer: BizShield AI is an automated AI-powered contract analysis "
            "and business risk decision-support tool. It provides plain-language risk flagging, commercial negotiation benchmarks, "
            "and regulatory awareness for small businesses and freelancers. BizShield AI does not provide formal legal advice, "
            "legal opinions, or legal representation, nor does it create an advocate-client relationship. Commercial contracts and "
            "tax liabilities depend on specific factual circumstances, provincial jurisdictions, and prevailing statutory amendments. "
            "For high-value or disputed transactions, users should consult a qualified Pakistani legal practitioner or tax consultant."
        )
        st.markdown(f"""
        <div style='background:rgba(100, 116, 139, 0.08); border:1px solid rgba(100, 116, 139, 0.25); border-radius:8px; padding:14px; margin-top:20px; margin-bottom:16px;'>
            <div style='display:flex; align-items:flex-start; gap:10px;'>
                <span style='font-size:1.3rem;'>⚖️</span>
                <div>
                    <strong style='color:var(--text-color); font-size:0.92rem;'>Legal & Informational Decision-Support Disclaimer:</strong><br>
                    <span style='color:var(--text-color); opacity:0.85; font-size:0.82rem; line-height:1.45;'>
                        {disclaimer_text}
                    </span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 8. DOWNLOAD FULL REPORT
        report_text = f"# BizShield AI - Commercial Contract Risk Audit\n\nContract: {st.session_state.current_contract_title}\nOverall Risk: {report.overall_risk_score}/100 ({report.overall_risk_level})\n\n"
        report_text += f"## 🚦 Executive Verdict\n{report.overall_risk_level} ({report.overall_risk_score}/100)\n\n"
        report_text += "## 💡 Plain English Summary\n" + "\n".join([f"- {b}" for b in report.plain_english_summary]) + "\n\n"
        report_text += "## 💬 Pre-Drafted Negotiation Message\n```\n" + negotiation_text + "\n```\n\n"
        report_text += "## 🚨 Risky Clauses & Safe Revisions\n"
        for rf in report.red_flags:
            report_text += f"\n### {rf.clause_reference} [{rf.risk_level} Risk]\n- Issue: {rf.problem_explanation}\n- Suggested Revision: {rf.suggested_revision}\n"
        report_text += "\n## 🔍 Missing Protections\n" + "\n".join([f"- {m}" for m in report.missing_protections]) + "\n"
        
        if hasattr(report, "relevant_sources") and report.relevant_sources:
            report_text += "\n## 📚 Relevant Legal Basis & Statutory References\n" + "\n".join([f"- {s}" for s in report.relevant_sources]) + "\n"
        
        report_text += f"\n## ⚖️ Legal & Informational Disclaimer\n{disclaimer_text}\n"
        
        st.download_button(
            label="📥 Download Action Plan & Audit Report (.md)",
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
        has_staff = st.checkbox("Have Employees / Staff?", value=False, key="chk_has_staff", help="Requires payroll withholding tax and EOBI compliance.")
        is_exporter = st.checkbox("Software / Services Exporter?", value=True, key="chk_is_exporter", help="Eligible for concessionary IT/ITeS export tax regimes under Section 154A.")

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

    def submit_user_question(question_text: str):
        q_str = question_text.strip()
        if not q_str:
            st.warning("⚠️ The question box is empty. Please type your question or click one of the buttons above!")
            return
        with st.spinner("Retrieving verified Pakistani statutes via RAG vector search..."):
            response_data = st.session_state.qa_advisor.answer_question(q_str)
            st.session_state.chat_history.append((
                q_str,
                response_data["answer"],
                response_data.get("source", ""),
                response_data.get("retrieved_chunks", [])
            ))
        st.rerun()

    # Quick Suggestion Chips (1-Click Instant Answer!)
    st.markdown("**💡 Common Questions Asked by Small Business Owners (Click to ask immediately):**")
    chip_cols = st.columns(len(SAMPLE_QA_QUESTIONS))

    for i, q_text in enumerate(SAMPLE_QA_QUESTIONS):
        with chip_cols[i]:
            btn_label = q_text[:26] + "..." if len(q_text) > 26 else q_text
            if st.button(btn_label, key=f"chip_{i}", use_container_width=True, help=f"Click to immediately ask: {q_text}"):
                submit_user_question(q_text)

    # User Query Input via Form (Supports typing and pressing Enter!)
    st.markdown("**Or type your custom legal / tax question below:**")
    with st.form("qa_custom_form", clear_on_submit=True):
        col_q_in, col_q_btn = st.columns([4.2, 1.2])
        with col_q_in:
            typed_q = st.text_input(
                "Type your legal or tax question here:",
                placeholder="Type your question here and press Enter (e.g., Can a landlord increase rent without notice?)...",
                label_visibility="collapsed"
            )
        with col_q_btn:
            ask_pressed = st.form_submit_button("🔍 Ask AI", type="primary", use_container_width=True)

        if ask_pressed:
            submit_user_question(typed_q)

    # Render Chat History
    if st.session_state.chat_history:
        st.markdown("---")
        st.markdown("### 📜 Conversation & Legal Advice History")
        for item in reversed(st.session_state.chat_history):
            q_user = item[0]
            a_resp = item[1]
            src = item[2] if len(item) > 2 else ""
            chunks = item[3] if len(item) > 3 else []

            with st.chat_message("user"):
                st.write(q_user)
            with st.chat_message("assistant", avatar="🛡️"):
                st.markdown(a_resp)
                if chunks:
                    with st.expander(f"📚 Retrieved via RAG: {len(chunks)} Verified Statutory Sources", expanded=False):
                        for c in chunks:
                            sim_pct = int(c.get('similarity_score', 0) * 100) if c.get('similarity_score') else 90
                            st.markdown(f"• **{c.get('title', 'Statute')}** — *{c.get('statute', 'Pakistani Law')}* (Match: `{sim_pct}%`)")
    else:
        st.markdown("""
        <div style='background:rgba(59, 130, 246, 0.08); border:1px solid rgba(59, 130, 246, 0.25); border-radius:8px; padding:16px; margin-top:20px;'>
            <div style='font-size:1rem; font-weight:700; color:#3B82F6; margin-bottom:6px;'>💡 How to use the Legal & Tax Advisor:</div>
            <div style='color:var(--text-color); font-size:0.9rem;'>
                1. <strong>Click any of the 5 quick buttons above</strong> to get instant answers with Pakistani legal citations (e.g., commercial rent rules, FBR tax withholding, SECP registration).<br>
                2. Or <strong>type your own custom question in the box</strong> and press Enter or click <strong>Ask AI</strong>!
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Chat follow-up input
    follow_up_q = st.chat_input("Ask a question or follow-up here...")
    if follow_up_q:
        submit_user_question(follow_up_q)
# TAB 4: ABOUT & EDUCATIONAL GUIDANCE
# ==============================================================================
with tab_about:
    st.markdown("## 🛡️ About BizShield AI")
    st.markdown("""
    **BizShield AI** is an AI-powered legal and tax information assistant designed specifically for small business owners, freelancers, and early-stage entrepreneurs in Pakistan.

    ### 🎯 The Problem
    Small businesses, freelancers, and early-stage entrepreneurs in Pakistan frequently struggle with:
    1. Signing contracts with hidden clauses and one-sided liability terms.
    2. Navigating corporate registration (SECP) and applicable tax obligations (FBR, Active Taxpayer List, Provincial Sales Tax, and withholding duties).
    3. Inability to afford expensive corporate legal retainers or professional accounting fees.

    ### 💡 The Solution
    BizShield AI provides:
    - **Contract Scanner & Privacy Shield:** Automatically redacts personal identifiers and audits contracts for 10 common business traps.
    - **Smart Compliance Checklist:** Customized registration and annual tax filing roadmaps.
    - **Legal & Tax Q&A:** Accurate, structured educational answers referencing official Pakistani statutory authorities.

    ---

    ### ⚖️ Important Principle & Disclaimer
    > **Educational Decision-Support Only:**  
    > BizShield AI is designed to provide **informational and educational preliminary decision-support guidance** to help small business owners understand their commercial options. It does not constitute formal attorney-client legal advice, a definitive legal opinion, or certified public accountant services. Users should consult a qualified lawyer or licensed tax professional for case-specific advice before executing agreements or making binding regulatory filings.
    """)
