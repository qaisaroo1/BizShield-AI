import re
from typing import Dict, List, Tuple


class PrivacyShield:
    """
    Privacy Shield - Automatic Data Anonymizer for Legal Documents.
    Redacts personal and confidential business data before sending text
    to the AI engine, ensuring zero client confidentiality leaks.
    """

    def __init__(self):
        # Regex patterns for Pakistani & International confidential data
        self.cnic_pattern = re.compile(r"\b\d{5}-\d{7}-\d\b|\b\d{13}\b")
        self.phone_pattern = re.compile(r"(\+92[\s-]?3\d{2}[\s-]?\d{7})|(\b03\d{2}[\s-]?\d{7}\b)|(\b\d{3}[-.]?\d{3}[-.]?\d{4}\b)")
        self.email_pattern = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")
        self.iban_pattern = re.compile(r"\bPK\d{2}[A-Za-z]{4}\d{16}\b", re.IGNORECASE)
        self.bank_acc_pattern = re.compile(r"\b(Account\s*(No|Number|#)?\s*[:.-]?\s*\d{8,20})\b", re.IGNORECASE)
        self.date_signatures = re.compile(r"(Signature\s*[:.-]?\s*[\w\s]{2,30})", re.IGNORECASE)

    def extract_party_names(self, text: str) -> List[Tuple[str, str]]:
        """
        Detects primary contract parties from standard introductory clauses.
        Returns a list of (entity_name, generic_role) tuples.
        """
        detected_parties = []

        patterns = [
            (r"(?:Landlord|Lessor)\s*[:.-]\s*([A-Za-z0-9\s&.,'-]+?)(?:\n|$|,)", "[LANDLORD / PARTY A]"),
            (r"(?:Tenant|Lessee)\s*[:.-]\s*([A-Za-z0-9\s&.,'-]+?)(?:\n|$|,)", "[TENANT / PARTY B]"),
            (r"(?:Client|Buyer|Customer)\s*[:.-]\s*([A-Za-z0-9\s&.,'-]+?)(?:\n|$|,)", "[CLIENT / PARTY A]"),
            (r"(?:Vendor|Supplier|Contractor|Service Provider)\s*[:.-]\s*([A-Za-z0-9\s&.,'-]+?)(?:\n|$|,)", "[VENDOR / PARTY B]"),
            (r"(?:First Party|Party 1)\s*[:.-]\s*([A-Za-z0-9\s&.,'-]+?)(?:\n|$|,)", "[PARTY A]"),
            (r"(?:Second Party|Party 2)\s*[:.-]\s*([A-Za-z0-9\s&.,'-]+?)(?:\n|$|,)", "[PARTY B]"),
        ]

        for pat, role in patterns:
            match = re.search(pat, text, re.IGNORECASE)
            if match:
                raw_name = match.group(1).strip()
                if len(raw_name) >= 3 and raw_name.lower() not in ["the", "an", "this", "either", "any"]:
                    # Avoid duplicate or overlapping names
                    if not any(raw_name in existing[0] for existing in detected_parties):
                        detected_parties.append((raw_name, role))

        return detected_parties

    def anonymize(
        self,
        contract_text: str,
        mask_money: bool = False,
        custom_redactions: List[str] = None
    ) -> Tuple[str, Dict[str, int]]:
        """
        Replaces sensitive identifiers with privacy tags.
        Returns:
            - sanitized_text: Contract text with confidential items replaced.
            - redaction_counts: Breakdown of shielded data categories.
        """
        redacted = contract_text
        counts: Dict[str, int] = {
            "CNIC / National IDs": 0,
            "Phone Numbers": 0,
            "Email Addresses": 0,
            "Bank Accounts / IBANs": 0,
            "Party & Corporate Names": 0,
            "Specific Signatures / Dates": 0,
        }

        # 1. Redact Party Names
        party_entities = self.extract_party_names(contract_text)
        for name, role in party_entities:
            matches = len(re.findall(re.escape(name), redacted, re.IGNORECASE))
            if matches > 0:
                counts["Party & Corporate Names"] += matches
                redacted = re.sub(re.escape(name), role, redacted, flags=re.IGNORECASE)

        # 2. Custom User-specified Redactions
        if custom_redactions:
            for item in custom_redactions:
                item = item.strip()
                if item and len(item) > 2:
                    matches = len(re.findall(re.escape(item), redacted, re.IGNORECASE))
                    if matches > 0:
                        counts["Party & Corporate Names"] += matches
                        redacted = re.sub(re.escape(item), "[CONFIDENTIAL]", redacted, flags=re.IGNORECASE)

        # 3. Redact CNIC
        cnics = self.cnic_pattern.findall(redacted)
        if cnics:
            counts["CNIC / National IDs"] += len(cnics)
            redacted = self.cnic_pattern.sub("[REDACTED_CNIC]", redacted)

        # 4. Redact Phone Numbers
        phones = [m[0] or m[1] or m[2] for m in self.phone_pattern.findall(redacted) if any(m)]
        if phones:
            counts["Phone Numbers"] += len(phones)
            redacted = self.phone_pattern.sub("[REDACTED_PHONE]", redacted)

        # 5. Redact Email Addresses
        emails = self.email_pattern.findall(redacted)
        if emails:
            counts["Email Addresses"] += len(emails)
            redacted = self.email_pattern.sub("[REDACTED_EMAIL]", redacted)

        # 6. Redact IBAN & Bank Accounts
        ibans = self.iban_pattern.findall(redacted)
        if ibans:
            counts["Bank Accounts / IBANs"] += len(ibans)
            redacted = self.iban_pattern.sub("[REDACTED_IBAN]", redacted)

        bank_accs = self.bank_acc_pattern.findall(redacted)
        if bank_accs:
            counts["Bank Accounts / IBANs"] += len(bank_accs)
            redacted = self.bank_acc_pattern.sub("[REDACTED_ACCOUNT]", redacted)

        # 7. Optional monetary masking
        if mask_money:
            money_pattern = re.compile(r"\b(PKR|Rs\.?)\s*[\d,]+(\.\d{2})?\b", re.IGNORECASE)
            moneys = money_pattern.findall(redacted)
            if moneys:
                counts["Monetary Figures"] = len(moneys)
                redacted = money_pattern.sub("[CONFIDENTIAL_AMOUNT]", redacted)

        return redacted, counts
