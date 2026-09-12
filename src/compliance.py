from typing import List, Dict, Any


class ComplianceTask:
    def __init__(
        self,
        task_id: str,
        title: str,
        category: str,
        authority: str,
        priority: str,
        description: str,
        official_source: str,
        timeline: str
    ):
        self.task_id = task_id
        self.title = title
        self.category = category
        self.authority = authority
        self.priority = priority  # "Mandatory", "High", "Recommended"
        self.description = description
        self.official_source = official_source
        self.timeline = timeline

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "title": self.title,
            "category": self.category,
            "authority": self.authority,
            "priority": self.priority,
            "description": self.description,
            "official_source": self.official_source,
            "timeline": self.timeline
        }


class SmartComplianceEngine:
    """
    Smart Compliance Engine:
    Generates actionable registration, tax, and reporting roadmaps
    based on verified Pakistani corporate and tax regulations (SECP & FBR).
    """

    def generate_checklist(
        self,
        entity_type: str = "Sole Proprietorship / Freelancer",
        industry: str = "IT & Digital Services / Freelancing",
        has_employees: bool = False,
        is_exporter: bool = False
    ) -> List[Dict[str, Any]]:
        tasks = []

        # 1. Federal Tax Registration (Universal)
        tasks.append(ComplianceTask(
            task_id="fbr_ntn",
            title="Register for National Tax Number (NTN)",
            category="Tax Registration",
            authority="Federal Board of Revenue (FBR)",
            priority="Mandatory",
            description="Register your business on the FBR Iris portal (iris.fbr.gov.pk) to obtain your NTN. Required for opening a business bank account and legitimate commercial invoicing.",
            official_source="Income Tax Ordinance 2001, Section 181",
            timeline="1 to 2 Days (Instant via CNIC)"
        ).to_dict())

        # 2. Entity-Specific Registrations
        if "Sole Proprietor" in entity_type or "Freelancer" in entity_type:
            tasks.append(ComplianceTask(
                task_id="sole_prop_bank",
                title="Business Bank Account & Letterhead",
                category="Banking & Identity",
                authority="Commercial Bank / SBP Guidelines",
                priority="Mandatory",
                description="Print official business letterhead, make a company stamp, and open a designated Sole Proprietor or Freelancer Foreign Currency / PKR account. Avoid mixing personal and business funds.",
                official_source="State Bank of Pakistan (SBP) AML/KYC Regulations",
                timeline="3 to 5 Days"
            ).to_dict())
        elif "Pvt Ltd" in entity_type or "SMC" in entity_type:
            tasks.append(ComplianceTask(
                task_id="secp_incorporation",
                title="SECP Digital Incorporation & Certificate",
                category="Corporate Registration",
                authority="Securities & Exchange Commission of Pakistan (SECP)",
                priority="Mandatory",
                description="Reserve company name via SECP eServices, submit Memorandum and Articles of Association (MOA/AOA), and obtain Certificate of Incorporation.",
                official_source="Companies Act 2017, Part II & III",
                timeline="3 to 7 Days"
            ).to_dict())
            tasks.append(ComplianceTask(
                task_id="secp_form_29",
                title="File Annual Corporate Returns (Form 29 / A)",
                category="Corporate Compliance",
                authority="SECP",
                priority="Mandatory",
                description="File annual return regarding directorship, registered office address, and shareholding structure within 30 days of Annual General Meeting (AGM).",
                official_source="Companies Act 2017, Section 130 & 197",
                timeline="Annual (Post-AGM)"
            ).to_dict())
        elif "Partnership" in entity_type or "AOP" in entity_type:
            tasks.append(ComplianceTask(
                task_id="partnership_deed",
                title="Register Partnership Deed with Registrar of Firms",
                category="Legal Formation",
                authority="Registrar of Firms (District Govt)",
                priority="Mandatory",
                description="Draft partnership deed outlining profit-sharing ratios and register with District Registrar of Firms to obtain Form C.",
                official_source="Partnership Act 1932, Section 58",
                timeline="1 to 2 Weeks"
            ).to_dict())

        # 3. Sector & Export-Specific: IT & Software Exports
        if is_exporter:
            tasks.append(ComplianceTask(
                task_id="pseb_reg",
                title="Register with Pakistan Software Export Board (PSEB)",
                category="Export Concessions & Licensing",
                authority="PSEB / Ministry of IT & Telecom",
                priority="High",
                description="Register as an IT exporter or tech freelancer with PSEB to qualify for concessionary export tax regimes under Section 154A of the Income Tax Ordinance 2001, subject to realization of export remittances through formal banking channels, tax return filing, and applicable Finance Act rules.",
                official_source="Income Tax Ordinance 2001, Section 154A & PSEB Export Guidelines",
                timeline="1 to 2 Weeks"
            ).to_dict())

        # 4. Provincial Sales Tax on Services
        tasks.append(ComplianceTask(
            task_id="provincial_sales_tax",
            title="Provincial Sales Tax Registration (PRA / SRB / KPRA)",
            category="Indirect Taxation",
            authority="Provincial Revenue Authority (e.g. PRA in Punjab, SRB in Sindh)",
            priority="High",
            description="If providing taxable services (such as IT-enabled services, software maintenance, consulting, or technical support), register with your relevant provincial revenue board (PRA, SRB, KPRA, or BRA). Applicable sales tax rates vary by province and specific service classification under prevailing provincial schedules.",
            official_source="Provincial Sales Tax on Services Acts (Punjab, Sindh, KP, Balochistan)",
            timeline="Within 30 Days of starting business"
        ).to_dict())

        # 5. Employer Responsibilities
        if has_employees:
            tasks.append(ComplianceTask(
                task_id="fbr_wht_salary",
                title="Deduct and Deposit Employee Withholding Tax",
                category="Payroll & Withholding Tax",
                authority="FBR",
                priority="Mandatory",
                description="Deduct income tax at source from employee salaries exceeding the annual threshold (PKR 600,000) and deposit monthly via CPR into the government treasury.",
                official_source="Income Tax Ordinance 2001, Section 149",
                timeline="Monthly (by the 15th of each month)"
            ).to_dict())
            tasks.append(ComplianceTask(
                task_id="eobi_pesi",
                title="EOBI & Provincial Social Security (PESSI/SESSI)",
                category="Labor Compliance",
                authority="Employees' Old-Age Benefits Institution (EOBI)",
                priority="Recommended",
                description="Register business with EOBI if employing 5 or more persons to secure employee pension and social security benefits.",
                official_source="EOBI Act 1976 / PESSI Ordinance 1965",
                timeline="Within 30 days of hiring 5th employee"
            ).to_dict())

        # 6. Annual Return & Record Keeping
        tasks.append(ComplianceTask(
            task_id="fbr_annual_return",
            title="Annual Income Tax Return & Wealth Statement",
            category="Annual Tax Filing",
            authority="FBR",
            priority="Mandatory",
            description="File your annual income tax return on the FBR Iris portal by the statutory deadline (September 30 for individuals/AOPs, December 31 for corporate companies) to maintain Active Taxpayer (ATL) status.",
            official_source="Income Tax Ordinance 2001, Section 114 & 118",
            timeline="Annual (September 30 / December 31)"
        ).to_dict())

        tasks.append(ComplianceTask(
            task_id="bookkeeping_records",
            title="Mandatory Bookkeeping & Record Retention",
            category="Record Keeping",
            authority="FBR & Companies Act",
            priority="Mandatory",
            description="Maintain complete books of accounts, sales invoices, purchase receipts, utility bills, and bank statements for a minimum period of 6 years.",
            official_source="Income Tax Ordinance 2001, Section 174",
            timeline="Ongoing (Retain for 6 Years)"
        ).to_dict())

        return tasks
