import sys
from pathlib import Path

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add parent directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.privacy_shield import PrivacyShield
from src.contract_scanner import ContractScanner, generate_negotiation_script
from src.compliance import SmartComplianceEngine
from src.qa_advisor import LegalAdvisorAgent
from src.samples import (
    SAMPLE_1_LEASE_TEXT,
    SAMPLE_2_VENDOR_TEXT,
    SAMPLE_QA_QUESTIONS
)


from src.rag_store import LegalRAGStore


def run_tests():
    print("=" * 60)
    print("🛡️  Testing BizShield AI Core Multi-Module Architecture")
    print("=" * 60)

    # 1. Test Privacy Shield
    print("\n[1/5] Testing Privacy Shield (Auto-Anonymizer)...")
    shield = PrivacyShield()
    test_text = """
Landlord: ABC Properties
Tenant: XYZ Software Solutions
Representative: Muhammad Ali (CNIC: 35201-1234567-1, Phone: 0300-1234567, NTN: 1234567-8)
Authorized Signatory: Fatima Noor (Passport No: PA1234567, DOB: 14/05/1991)
Driver: Ahmad Khan (Driving License No: LHR-987654)
STRN: 12-34-5678-901-23
Account: PK36SCBL0000001123456701
Email: contact@xyzsoftware.com
Premises: Office No. 12, Lahore
Monthly Rent: PKR 150,000
"""
    redacted, counts = shield.anonymize(test_text)
    print(f"  Shielded Items Breakdown: {counts}")
    assert "[REDACTED_CNIC]" in redacted, "CNIC was not redacted"
    assert "[REDACTED_PHONE]" in redacted, "Phone was not redacted"
    assert "[REDACTED_EMAIL]" in redacted, "Email was not redacted"
    assert "[REDACTED_IBAN]" in redacted or "[REDACTED_ACCOUNT]" in redacted, "Bank account was not redacted"
    assert "[REDACTED_NTN]" in redacted, "NTN was not redacted"
    assert "[REDACTED_STRN]" in redacted, "STRN was not redacted"
    assert "[REDACTED_PASSPORT]" in redacted, "Passport was not redacted"
    assert "[REDACTED_LICENSE]" in redacted, "Driving license was not redacted"
    assert "[REDACTED_DOB]" in redacted, "DOB was not redacted"
    assert "[REDACTED_ADDRESS]" in redacted, "Address was not redacted"

    # Test user-specified custom redactions
    custom_text = "The confidential project codename is Project Falcon and secret partner is Tariq Aziz."
    redacted_custom, counts_custom = shield.anonymize(custom_text, custom_redactions=["Project Falcon", "Tariq Aziz"])
    assert "[CONFIDENTIAL]" in redacted_custom, "Custom word was not redacted"
    assert counts_custom["Custom Private Details"] == 2, "Custom count mismatch"

    # Verify that normal contract clauses and divider lines are NOT over-redacted
    red_lease, lease_counts = shield.anonymize(SAMPLE_1_LEASE_TEXT)
    assert "4. Payment" in red_lease, "Clause '4. Payment' was incorrectly redacted as an address"
    assert "________________________________________" in red_lease, "Separator line was incorrectly redacted"
    assert lease_counts["Physical Addresses & Locations"] == 1, "Expected exactly 1 address in Sample 1"
    print("  ✅ Privacy Shield verified: Automatic PII, Precise Address Masking (zero clause over-redaction), and Custom Redactions working 100%!")

    # 2. Test Contract Scanner on Sample 1 (Commercial Lease)
    print("\n[2/5] Testing Contract Scanner on Sample 1 (Commercial Lease)...")
    scanner = ContractScanner()
    report1 = scanner.analyze_contract(SAMPLE_1_LEASE_TEXT)
    print(f"  Contract Type: {report1.contract_type}")
    print(f"  Overall Risk Rating: {report1.overall_risk_score}/100 ({report1.overall_risk_level})")
    print(f"  Red Flags Detected: {len(report1.red_flags)}")
    print(f"  Missing Protections: {len(report1.missing_protections)}")
    print(f"  Dynamic Legal Sources: {len(report1.relevant_sources)} attached")
    assert report1.overall_risk_score > 60, "Expected high risk score for Sample 1"
    assert len(report1.red_flags) >= 5, "Expected at least 5 red flags for Sample 1"
    assert len(report1.relevant_sources) >= 3, "Expected at least 3 dynamic statutory sources for lease"
    assert report1.disclaimer and "Disclaimer" in report1.disclaimer, "Disclaimer missing or empty"

    # Verify that every finding has its specific statutory citation (not generic FBR/SECP)
    for rf in report1.red_flags:
        assert rf.legal_basis and len(rf.legal_basis) > 5, f"Finding {rf.clause_reference} missing legal basis citation"
        print(f"    - {rf.clause_reference}: Legal Basis -> {rf.legal_basis}")
    assert any("Income Tax Ordinance" in rf.legal_basis for rf in report1.red_flags), "Tax finding must cite Income Tax Ordinance"
    assert any("Rented Premises" in rf.legal_basis for rf in report1.red_flags), "Lease finding must cite Rented Premises legislation"

    # Test negotiation script generation and deduplication
    script1 = generate_negotiation_script(report1)
    assert "completely ready to sign" not in script1.lower(), "'completely ready to sign' found in negotiation script"
    tax_numbered_points = [
        p for p in script1.split("\n\n")
        if any(p.strip().startswith(f"{i}.") for i in range(1, 10)) and ("tax" in p.lower() or "withholding" in p.lower())
    ]
    assert len(tax_numbered_points) <= 1, f"Expected at most 1 tax point in script, got {len(tax_numbered_points)}: {tax_numbered_points}"
    print(f"  Negotiation Script Points: {len(tax_numbered_points)} tax point (no duplicates!), collaborative closing verified.")
    print("  ✅ Sample 1 Lease audit verified against Expected Findings, Dynamic Sources & Disclaimer!")

    # 3. Test Contract Scanner on Sample 2 (Vendor Agreement)
    print("\n[3/5] Testing Contract Scanner on Sample 2 (Vendor Agreement)...")
    report2 = scanner.analyze_contract(SAMPLE_2_VENDOR_TEXT)
    print(f"  Contract Type: {report2.contract_type}")
    print(f"  Overall Risk Rating: {report2.overall_risk_score}/100 ({report2.overall_risk_level})")
    print(f"  Red Flags Detected: {len(report2.red_flags)}")
    print(f"  Dynamic Legal Sources: {len(report2.relevant_sources)} attached")
    assert len(report2.red_flags) >= 4, "Expected at least 4 red flags for Sample 2"
    assert len(report2.relevant_sources) >= 3, "Expected at least 3 dynamic statutory sources for vendor agreement"
    assert report2.disclaimer and "Disclaimer" in report2.disclaimer, "Disclaimer missing or empty"

    for rf in report2.red_flags:
        assert rf.legal_basis and len(rf.legal_basis) > 5, f"Finding {rf.clause_reference} missing legal basis citation"
    assert any("Copyright Ordinance" in rf.legal_basis for rf in report2.red_flags), "IP finding must cite Copyright Ordinance"

    script2 = generate_negotiation_script(report2)
    assert "completely ready to sign" not in script2.lower(), "'completely ready to sign' found in vendor script"
    print("  ✅ Sample 2 Vendor Agreement audit verified with Dynamic Sources, Clause-Level Citations & Disclaimer!")

    # 4. Test Compliance Engine & Q&A
    print("\n[4/5] Testing Compliance Engine & Legal Q&A Advisor...")
    engine = SmartComplianceEngine()
    tasks_sp = engine.generate_checklist(entity_type="Sole Proprietorship / Freelancer", is_exporter=True)
    tasks_sp_no_exp = engine.generate_checklist(entity_type="Sole Proprietorship / Freelancer", is_exporter=False)
    print(f"  Sole Proprietorship Tasks: {len(tasks_sp)} items (Exporter) vs {len(tasks_sp_no_exp)} items (Non-Exporter).")
    assert len(tasks_sp) == 6, f"Expected 6 tasks for exporter, got {len(tasks_sp)}"
    assert len(tasks_sp_no_exp) == 5, f"Expected 5 tasks for non-exporter, got {len(tasks_sp_no_exp)}"
    assert any(t["task_id"] == "pseb_reg" for t in tasks_sp), "PSEB should be present for exporters"
    assert not any(t["task_id"] == "pseb_reg" for t in tasks_sp_no_exp), "PSEB should NOT be present for non-exporters"

    advisor = LegalAdvisorAgent()
    sample_q = SAMPLE_QA_QUESTIONS[0]
    qa_resp = advisor.answer_question(sample_q)
    print(f"  Sample Query: '{sample_q}'")
    print(f"  Advisor Answer Preview: {qa_resp['answer'][:120]}...")
    assert len(qa_resp['answer']) > 50, "Answer was too short"
    assert "retrieved_chunks" in qa_resp, "RAG chunks missing from advisor response"
    print(f"  RAG Citations Retrieved: {len(qa_resp['retrieved_chunks'])} statutory sources")
    print("  ✅ Compliance engine and Q&A advisor verified successfully!")

    # 5. Test Legal RAG Vector Store
    print("\n[5/5] Testing Legal RAG Vector Store (Gemini Embeddings)...")
    rag = LegalRAGStore()
    results = rag.search("income tax withholding on commercial rent", top_k=2)
    print(f"  RAG Total Chunks: {len(rag.chunks)}")
    print(f"  Top RAG Match: '{results[0]['title']}' (Statute: {results[0]['statute']}, Score: {results[0]['similarity_score']})")
    assert len(results) > 0, "RAG search returned no results"
    print("  ✅ Semantic RAG vector retrieval verified successfully!")

    print("\n" + "=" * 60)
    print("🎉 ALL 5 BIZSHIELD AI CORE MODULES PASSED VERIFICATION!")
    print("=" * 60)


if __name__ == "__main__":
    run_tests()
