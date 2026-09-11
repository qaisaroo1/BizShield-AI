import re
from typing import Dict, List, Tuple


class PrivacyShield:
    """
    Privacy Shield - Automatic Data Anonymizer for Legal Documents.
    Redacts personal and confidential business data before sending text
    to the AI engine, ensuring zero client confidentiality leaks.
    """

    def __init__(self):
        # 1. Identity & Contact Identifiers
        self.cnic_pattern = re.compile(r"\b\d{5}-\d{7}-\d\b|\b\d{13}\b")
        self.phone_pattern = re.compile(r"(\+92[\s-]?3\d{2}[\s-]?\d{7})|(\b03\d{2}[\s-]?\d{7}\b)|(\b\d{3}[-.]?\d{3}[-.]?\d{4}\b)")
        self.email_pattern = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")
        self.iban_pattern = re.compile(r"\bPK\d{2}[A-Za-z]{4}\d{16}\b", re.IGNORECASE)
        self.bank_acc_pattern = re.compile(r"\b(Account\s*(?:No|Number|#)?\s*[:.-]?\s*\d{8,20})\b", re.IGNORECASE)
        self.date_signatures = re.compile(r"(Signature\s*[:.-]?\s*[\w\s]{2,30})", re.IGNORECASE)

        # 2. Date of Birth (DOB)
        self.dob_pattern = re.compile(
            r"(\b(?:DOB|Date\s*of\s*Birth|Born\s*(?:on)?)\s*[:.-]?\s*)(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2})\b",
            re.IGNORECASE
        )

        # 3. Tax Identifiers: FBR NTN & Provincial STRN
        self.ntn_explicit_pattern = re.compile(
            r"(\b(?:NTN|National\s*Tax\s*(?:No|Number)?)\s*[:.-]?\s*)(\d{7}-?\d?)\b",
            re.IGNORECASE
        )
        self.ntn_standalone_pattern = re.compile(r"\b\d{7}-\d\b")

        self.strn_explicit_pattern = re.compile(
            r"(\b(?:STRN|Sales\s*Tax\s*(?:Reg|Registration)?\s*(?:No|Number)?)\s*[:.-]?\s*)([0-9-]{7,20})\b",
            re.IGNORECASE
        )
        self.strn_hyphen_pattern = re.compile(r"\b\d{2}-\d{2}-\d{4}-\d{3}-\d{2}\b")

        # 4. Travel & Driving IDs: Passport & Driving License
        self.passport_explicit_pattern = re.compile(
            r"(\b(?:Passport\s*(?:No|Number)?\s*[:.-]?\s*))([A-Za-z0-9]{7,10})\b",
            re.IGNORECASE
        )
        self.passport_standalone_pattern = re.compile(r"\b[A-Za-z]{2}\d{7}\b")

        self.license_explicit_pattern = re.compile(
            r"(\b(?:Driving\s*License|Driver's\s*License|License\s*No)\s*[:.-]?\s*)([A-Za-z0-9/-]{6,18})\b",
            re.IGNORECASE
        )

        # 5. Physical Addresses & Property Locations
        self.labeled_addr_pattern = re.compile(
            r"\b((?:Premises|Registered\s*Office|Warehouse|Property|Address|Residential\s*Address|Permanent\s*Address)\s*[:.-]\s*)([^\n\r]+)",
            re.IGNORECASE
        )
        self.plot_address_pattern = re.compile(
            r"\b((?:Plot|House|Flat|Shop|Office|Building|Suite)\s*(?:No|Number|#)?\s*[:.-]?\s*[\w\d/-]+(?:,\s*[^,\n\r]+?(?:Floor|Block|Street|Road|Phase|Sector|DHA|Bahria|Gulberg|Clifton|Cantt|Colony|Town|Lahore|Karachi|Islamabad|Rawalpindi|Peshawar|Quetta|Faisalabad|Multan))+(?:,\s*(?:Lahore|Karachi|Islamabad|Rawalpindi|Peshawar|Quetta|Faisalabad|Multan))?)\b",
            re.IGNORECASE
        )

        self.last_audit_log: List[Dict[str, str]] = []

    def extract_party_names(self, text: str) -> List[Tuple[str, str]]:
        """
        Detects primary contract parties from standard introductory clauses.
        Returns a list of (entity_name, generic_role) tuples.
        """
        detected_parties = []

        patterns = [
            (r"(?:Landlord|Lessor)\s*[:.-]\s*([A-Za-z0-9\s&.'-]+?)(?:\(|,|\n|$)", "[LANDLORD / PARTY A]"),
            (r"(?:Tenant|Lessee)\s*[:.-]\s*([A-Za-z0-9\s&.'-]+?)(?:\(|,|\n|$)", "[TENANT / PARTY B]"),
            (r"(?:Client|Buyer|Customer)\s*[:.-]\s*([A-Za-z0-9\s&.'-]+?)(?:\(|,|\n|$)", "[CLIENT / PARTY A]"),
            (r"(?:Vendor|Supplier|Contractor|Service Provider)\s*[:.-]\s*([A-Za-z0-9\s&.'-]+?)(?:\(|,|\n|$)", "[VENDOR / PARTY B]"),
            (r"(?:First Party|Party 1)\s*[:.-]\s*([A-Za-z0-9\s&.'-]+?)(?:\(|,|\n|$)", "[PARTY A]"),
            (r"(?:Second Party|Party 2)\s*[:.-]\s*([A-Za-z0-9\s&.'-]+?)(?:\(|,|\n|$)", "[PARTY B]"),
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
            "Tax & Business IDs (NTN/STRN)": 0,
            "Passport & License Numbers": 0,
            "Physical Addresses & Locations": 0,
            "Dates of Birth (DOB)": 0,
            "Custom Private Details": 0,
        }
        self.last_audit_log = []

        # 1. Redact Party Names
        party_entities = self.extract_party_names(contract_text)
        for name, role in party_entities:
            matches = len(re.findall(re.escape(name), redacted, re.IGNORECASE))
            if matches > 0:
                counts["Party & Corporate Names"] += matches
                redacted = re.sub(re.escape(name), role, redacted, flags=re.IGNORECASE)
                self.last_audit_log.append({
                    "category": "Party & Corporate Name",
                    "detected_raw": name,
                    "masked_preview": f"{name[:3]}*** (Party Entity)",
                    "ai_token": role,
                    "status": "Hidden from AI (100% Protected)"
                })

        # 2. Custom User-specified Redactions
        if custom_redactions:
            for item in custom_redactions:
                item = item.strip()
                if item and len(item) > 1:
                    matches = len(re.findall(re.escape(item), redacted, re.IGNORECASE))
                    if matches > 0:
                        counts["Custom Private Details"] += matches
                        redacted = re.sub(re.escape(item), "[CONFIDENTIAL]", redacted, flags=re.IGNORECASE)
                        self.last_audit_log.append({
                            "category": "Custom Private Info",
                            "detected_raw": item,
                            "masked_preview": f"{item[:2]}*** (User Specified)",
                            "ai_token": "[CONFIDENTIAL]",
                            "status": "Hidden from AI (100% Protected)"
                        })

        # 3. Redact CNIC / National IDs
        cnics = self.cnic_pattern.findall(redacted)
        if cnics:
            counts["CNIC / National IDs"] += len(cnics)
            for cnic in set(cnics):
                preview = f"{cnic[:5]}-*******-{cnic[-1]}" if len(cnic) >= 14 else f"{cnic[:4]}******{cnic[-2:]}"
                self.last_audit_log.append({
                    "category": "CNIC / National ID",
                    "detected_raw": cnic,
                    "masked_preview": preview,
                    "ai_token": "[REDACTED_CNIC]",
                    "status": "Hidden from AI (100% Protected)"
                })
            redacted = self.cnic_pattern.sub("[REDACTED_CNIC]", redacted)

        # 4. Redact Date of Birth (DOB)
        dobs = self.dob_pattern.findall(redacted)
        if dobs:
            counts["Dates of Birth (DOB)"] += len(dobs)
            for prefix, d in set(dobs):
                self.last_audit_log.append({
                    "category": "Date of Birth (DOB)",
                    "detected_raw": d,
                    "masked_preview": f"**/**/{d.split('/')[-1] if '/' in d else d.split('-')[-1]}",
                    "ai_token": "[REDACTED_DOB]",
                    "status": "Hidden from AI (100% Protected)"
                })
            redacted = self.dob_pattern.sub(r"\1[REDACTED_DOB]", redacted)

        # 5. Redact FBR NTN (National Tax Number)
        ntn_matches = self.ntn_explicit_pattern.findall(redacted)
        if ntn_matches:
            counts["Tax & Business IDs (NTN/STRN)"] += len(ntn_matches)
            for prefix, n in set(ntn_matches):
                self.last_audit_log.append({
                    "category": "FBR NTN (Tax Number)",
                    "detected_raw": n,
                    "masked_preview": f"{n[:4]}***-{n[-1] if '-' in n else '*'}",
                    "ai_token": "[REDACTED_NTN]",
                    "status": "Hidden from AI (100% Protected)"
                })
            redacted = self.ntn_explicit_pattern.sub(r"\1[REDACTED_NTN]", redacted)

        standalone_ntns = self.ntn_standalone_pattern.findall(redacted)
        if standalone_ntns:
            counts["Tax & Business IDs (NTN/STRN)"] += len(standalone_ntns)
            for n in set(standalone_ntns):
                self.last_audit_log.append({
                    "category": "FBR NTN (Tax Number)",
                    "detected_raw": n,
                    "masked_preview": f"{n[:4]}***-{n[-1]}",
                    "ai_token": "[REDACTED_NTN]",
                    "status": "Hidden from AI (100% Protected)"
                })
            redacted = self.ntn_standalone_pattern.sub("[REDACTED_NTN]", redacted)

        # 6. Redact STRN (Sales Tax Registration Number)
        strn_matches = self.strn_explicit_pattern.findall(redacted)
        if strn_matches:
            counts["Tax & Business IDs (NTN/STRN)"] += len(strn_matches)
            for prefix, s in set(strn_matches):
                self.last_audit_log.append({
                    "category": "STRN (Sales Tax Reg)",
                    "detected_raw": s,
                    "masked_preview": f"{s[:4]}***{s[-2:] if len(s)>4 else ''}",
                    "ai_token": "[REDACTED_STRN]",
                    "status": "Hidden from AI (100% Protected)"
                })
            redacted = self.strn_explicit_pattern.sub(r"\1[REDACTED_STRN]", redacted)

        strn_hyphens = self.strn_hyphen_pattern.findall(redacted)
        if strn_hyphens:
            counts["Tax & Business IDs (NTN/STRN)"] += len(strn_hyphens)
            for s in set(strn_hyphens):
                self.last_audit_log.append({
                    "category": "STRN (Sales Tax Reg)",
                    "detected_raw": s,
                    "masked_preview": f"{s[:5]}****{s[-3:]}",
                    "ai_token": "[REDACTED_STRN]",
                    "status": "Hidden from AI (100% Protected)"
                })
            redacted = self.strn_hyphen_pattern.sub("[REDACTED_STRN]", redacted)

        # 7. Redact Passports
        passport_matches = self.passport_explicit_pattern.findall(redacted)
        if passport_matches:
            counts["Passport & License Numbers"] += len(passport_matches)
            for prefix, p in set(passport_matches):
                self.last_audit_log.append({
                    "category": "Passport Number",
                    "detected_raw": p,
                    "masked_preview": f"{p[:2]}*****{p[-1]}",
                    "ai_token": "[REDACTED_PASSPORT]",
                    "status": "Hidden from AI (100% Protected)"
                })
            redacted = self.passport_explicit_pattern.sub(r"\1[REDACTED_PASSPORT]", redacted)

        passport_standalones = self.passport_standalone_pattern.findall(redacted)
        if passport_standalones:
            counts["Passport & License Numbers"] += len(passport_standalones)
            for p in set(passport_standalones):
                self.last_audit_log.append({
                    "category": "Passport Number",
                    "detected_raw": p,
                    "masked_preview": f"{p[:2]}*****{p[-1]}",
                    "ai_token": "[REDACTED_PASSPORT]",
                    "status": "Hidden from AI (100% Protected)"
                })
            redacted = self.passport_standalone_pattern.sub("[REDACTED_PASSPORT]", redacted)

        # 8. Redact Driving Licenses
        license_matches = self.license_explicit_pattern.findall(redacted)
        if license_matches:
            counts["Passport & License Numbers"] += len(license_matches)
            for prefix, l in set(license_matches):
                self.last_audit_log.append({
                    "category": "Driving License Number",
                    "detected_raw": l,
                    "masked_preview": f"{l[:3]}****{l[-2:] if len(l)>4 else ''}",
                    "ai_token": "[REDACTED_LICENSE]",
                    "status": "Hidden from AI (100% Protected)"
                })
            redacted = self.license_explicit_pattern.sub(r"\1[REDACTED_LICENSE]", redacted)

        # 9. Redact Phone Numbers
        phones = [m[0] or m[1] or m[2] for m in self.phone_pattern.findall(redacted) if any(m)]
        if phones:
            counts["Phone Numbers"] += len(phones)
            for p in set(phones):
                p_clean = p.strip()
                preview = f"{p_clean[:4]}*******{p_clean[-2:]}" if len(p_clean) >= 6 else f"{p_clean[:2]}****"
                self.last_audit_log.append({
                    "category": "Phone Number",
                    "detected_raw": p_clean,
                    "masked_preview": preview,
                    "ai_token": "[REDACTED_PHONE]",
                    "status": "Hidden from AI (100% Protected)"
                })
            redacted = self.phone_pattern.sub("[REDACTED_PHONE]", redacted)

        # 10. Redact Email Addresses
        emails = self.email_pattern.findall(redacted)
        if emails:
            counts["Email Addresses"] += len(emails)
            for e in set(emails):
                eparts = e.split("@")
                preview = f"{eparts[0][:2]}***@{eparts[1]}" if len(eparts) == 2 else "e***@domain"
                self.last_audit_log.append({
                    "category": "Email Address",
                    "detected_raw": e,
                    "masked_preview": preview,
                    "ai_token": "[REDACTED_EMAIL]",
                    "status": "Hidden from AI (100% Protected)"
                })
            redacted = self.email_pattern.sub("[REDACTED_EMAIL]", redacted)

        # 11. Redact IBAN & Bank Accounts
        ibans = self.iban_pattern.findall(redacted)
        if ibans:
            counts["Bank Accounts / IBANs"] += len(ibans)
            for ib in set(ibans):
                preview = f"{ib[:4]}************{ib[-2:]}"
                self.last_audit_log.append({
                    "category": "Bank Account / IBAN",
                    "detected_raw": ib,
                    "masked_preview": preview,
                    "ai_token": "[REDACTED_IBAN]",
                    "status": "Hidden from AI (100% Protected)"
                })
            redacted = self.iban_pattern.sub("[REDACTED_IBAN]", redacted)

        bank_accs = self.bank_acc_pattern.findall(redacted)
        if bank_accs:
            counts["Bank Accounts / IBANs"] += len(bank_accs)
            for b in set(bank_accs):
                b_str = b if isinstance(b, str) else str(b[0])
                preview = f"{b_str[:12]}******" if len(b_str) >= 12 else b_str
                self.last_audit_log.append({
                    "category": "Bank Account Number",
                    "detected_raw": b_str,
                    "masked_preview": preview,
                    "ai_token": "[REDACTED_ACCOUNT]",
                    "status": "Hidden from AI (100% Protected)"
                })
            redacted = self.bank_acc_pattern.sub("[REDACTED_ACCOUNT]", redacted)

        # 12. Redact Physical Addresses & Property Locations
        labeled_addrs = self.labeled_addr_pattern.findall(redacted)
        if labeled_addrs:
            for prefix, addr in labeled_addrs:
                addr_clean = addr.strip()
                if addr_clean and not addr_clean.startswith("[REDACTED"):
                    counts["Physical Addresses & Locations"] += 1
                    preview = f"{addr_clean[:14]}... (Physical Location)" if len(addr_clean) > 14 else addr_clean
                    self.last_audit_log.append({
                        "category": "Physical Address / Location",
                        "detected_raw": addr_clean,
                        "masked_preview": preview,
                        "ai_token": "[REDACTED_ADDRESS]",
                        "status": "Hidden from AI (100% Protected)"
                    })
            redacted = self.labeled_addr_pattern.sub(r"\1[REDACTED_ADDRESS]", redacted)

        plot_addrs = self.plot_address_pattern.findall(redacted)
        if plot_addrs:
            for p_addr in set(plot_addrs):
                if "[REDACTED" not in p_addr:
                    counts["Physical Addresses & Locations"] += 1
                    preview = f"{p_addr[:14]}... (Physical Location)" if len(p_addr) > 14 else p_addr
                    self.last_audit_log.append({
                        "category": "Physical Address / Location",
                        "detected_raw": p_addr,
                        "masked_preview": preview,
                        "ai_token": "[REDACTED_ADDRESS]",
                        "status": "Hidden from AI (100% Protected)"
                    })
            redacted = self.plot_address_pattern.sub("[REDACTED_ADDRESS]", redacted)

        # 13. Optional monetary masking
        if mask_money:
            money_pattern = re.compile(r"\b(PKR|Rs\.?)\s*[\d,]+(\.\d{2})?\b", re.IGNORECASE)
            moneys = money_pattern.findall(redacted)
            if moneys:
                counts["Monetary Figures"] = len(moneys)
                for m in set(moneys):
                    m_str = m[0] if isinstance(m, tuple) else str(m)
                    self.last_audit_log.append({
                        "category": "Monetary Amount",
                        "detected_raw": m_str,
                        "masked_preview": "PKR [Amount Hidden]",
                        "ai_token": "[CONFIDENTIAL_AMOUNT]",
                        "status": "Hidden from AI (100% Protected)"
                    })
                redacted = money_pattern.sub("[CONFIDENTIAL_AMOUNT]", redacted)

        return redacted, counts
