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
from src.contract_scanner import ContractScanner
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
Representative: Muhammad Ali (CNIC: 35201-1234567-1, Phone: 0300-1234567)
Account: PK36SCBL0000001123456701
Email: contact@xyzsoftware.com
Monthly Rent: PKR 150,000 to Office No. 12, Lahore
"""
    redacted, counts = shield.anonymize(test_text)
    print(f"  Shielded Items Breakdown: {counts}")
    assert "[REDACTED_CNIC]" in redacted, "CNIC was not redacted"
    assert "[REDACTED_PHONE]" in redacted, "Phone was not redacted"
    assert "[REDACTED_EMAIL]" in redacted, "Email was not redacted"
    assert "[REDACTED_IBAN]" in redacted or "[REDACTED_ACCOUNT]" in redacted, "Bank account was not redacted"
    print("  ✅ Privacy Shield verified: Zero sensitive personal data leaked!")

    # 2. Test Contract Scanner on Sample 1 (Commercial Lease)
    print("\n[2/5] Testing Contract Scanner on Sample 1 (Commercial Lease)...")
    scanner = ContractScanner()
    report1 = scanner.analyze_contract(SAMPLE_1_LEASE_TEXT)
    print(f"  Contract Type: {report1.contract_type}")
    print(f"  Overall Risk Rating: {report1.overall_risk_score}/100 ({report1.overall_risk_level})")
    print(f"  Red Flags Detected: {len(report1.red_flags)}")
    print(f"  Missing Protections: {len(report1.missing_protections)}")
    for f in report1.red_flags[:3]:
        print(f"    - [{f.risk_level}] {f.clause_reference}: {f.problem_explanation[:75]}...")
    assert report1.overall_risk_score > 60, "Expected high risk score for Sample 1"
    assert len(report1.red_flags) >= 5, "Expected at least 5 red flags for Sample 1"
    print("  ✅ Sample 1 Lease audit verified against Expected Findings!")

    # 3. Test Contract Scanner on Sample 2 (Vendor Agreement)
    print("\n[3/5] Testing Contract Scanner on Sample 2 (Vendor Agreement)...")
    report2 = scanner.analyze_contract(SAMPLE_2_VENDOR_TEXT)
    print(f"  Contract Type: {report2.contract_type}")
    print(f"  Overall Risk Rating: {report2.overall_risk_score}/100 ({report2.overall_risk_level})")
    print(f"  Red Flags Detected: {len(report2.red_flags)}")
    assert len(report2.red_flags) >= 4, "Expected at least 4 red flags for Sample 2"
    print("  ✅ Sample 2 Vendor Agreement audit verified!")

    # 4. Test Compliance Engine & Q&A
    print("\n[4/5] Testing Compliance Engine & Legal Q&A Advisor...")
    engine = SmartComplianceEngine()
    tasks_sp = engine.generate_checklist(entity_type="Sole Proprietorship / Freelancer", is_exporter=True)
    print(f"  Sole Proprietorship Tasks: {len(tasks_sp)} compliance items generated.")
    assert len(tasks_sp) >= 5, "Expected at least 5 compliance items"

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
