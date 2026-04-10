"""Report generation service."""
import uuid
import time
from typing import List, Optional
from app.models.schemas import ReportResponse, ActionType, ComplianceIssue
from app.services.llm_service import LLMService
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class ReportService:
    """Service for generating various types of reports."""

    def __init__(self, llm_service: LLMService):
        self.llm = llm_service

    async def generate_summary(
        self, document_contents: List[str], document_ids: List[str], query: Optional[str] = None
    ) -> ReportResponse:
        """Generate a summary report for documents."""
        start_time = time.time()
        combined_content = "\n\n---\n\n".join(document_contents[:5])  # Limit to first 5 docs
        focus = f"\nFocus on: {query}" if query else ""

        prompt = f"""Analyze the following document content and provide a comprehensive summary.
{focus}

Document Content:
{combined_content[:8000]}

Provide:
1. Executive Summary (2-3 paragraphs)
2. Key Points (5-10 bullet points)
3. Main Topics Covered
4. Important Data/Statistics mentioned
5. Recommendations or Action Items

Format your response clearly with section headers."""

        system_prompt = "You are an expert document analyst. Provide clear, concise, and accurate summaries."
        response = await self.llm.generate(prompt, system_prompt)
        lines = response.split("\n")
        key_findings = [line.strip("- ").strip() for line in lines if line.strip().startswith(("-", "•", "*")) and len(line.strip()) > 10][:10]

        return ReportResponse(
            report_id=str(uuid.uuid4()),
            action_type=ActionType.SUMMARIZE,
            title="Document Summary Report",
            summary=response[:500] + "..." if len(response) > 500 else response,
            content=response,
            key_findings=key_findings,
            document_ids=document_ids,
            processing_time_ms=(time.time() - start_time) * 1000,
        )

    async def generate_compliance_report(
        self,
        document_contents: List[str],
        document_ids: List[str],
        policy_contents: Optional[List[str]] = None,
        compliance_areas: Optional[List[str]] = None,
    ) -> ReportResponse:
        """Generate a compliance validation report."""
        start_time = time.time()
        areas_str = ", ".join(compliance_areas) if compliance_areas else "general regulatory compliance"
        policy_section = ""
        if policy_contents:
            policy_section = f"\n\nPolicy Documents:\n" + "\n---\n".join(policy_contents[:3])

        combined_docs = "\n\n---\n\n".join(document_contents[:5])

        prompt = f"""Perform a comprehensive compliance analysis on the following documents.

Compliance Areas to Check: {areas_str}
{policy_section}

Documents to Analyze:
{combined_docs[:6000]}

Provide a detailed compliance report including:
1. Overall Compliance Status (Compliant/Partially Compliant/Non-Compliant)
2. Compliance Issues Found (with severity: HIGH/MEDIUM/LOW)
3. Areas of Good Compliance
4. Specific Violations or Gaps
5. Recommendations for Compliance Improvement
6. Risk Assessment

Be specific about which sections or clauses have compliance issues."""

        system_prompt = """You are a compliance expert with deep knowledge of regulatory frameworks, 
data protection laws, and enterprise compliance requirements. Provide thorough, accurate compliance assessments."""

        response = await self.llm.generate(prompt, system_prompt)
        issues = self._extract_compliance_issues(response)
        lines = response.split("\n")
        recommendations = [
            line.strip("- ").strip()
            for line in lines
            if ("recommend" in line.lower() or "should" in line.lower() or "must" in line.lower())
            and len(line.strip()) > 20
        ][:10]

        return ReportResponse(
            report_id=str(uuid.uuid4()),
            action_type=ActionType.COMPLIANCE_CHECK,
            title="Compliance Validation Report",
            summary=f"Compliance analysis completed for {len(document_ids)} document(s). Areas checked: {areas_str}",
            content=response,
            compliance_issues=issues,
            recommendations=recommendations,
            document_ids=document_ids,
            processing_time_ms=(time.time() - start_time) * 1000,
        )

    def _extract_compliance_issues(self, response: str) -> List[ComplianceIssue]:
        """Extract compliance issues from LLM response."""
        issues = []
        lines = response.split("\n")
        for i, line in enumerate(lines):
            line_lower = line.lower()
            if any(word in line_lower for word in ["violation", "issue", "gap", "non-compliant", "missing"]):
                severity = "MEDIUM"
                if any(word in line_lower for word in ["critical", "high", "severe", "major"]):
                    severity = "HIGH"
                elif any(word in line_lower for word in ["low", "minor", "minimal"]):
                    severity = "LOW"

                if len(line.strip()) > 20:
                    issues.append(
                        ComplianceIssue(
                            area="Compliance",
                            severity=severity,
                            description=line.strip("- •*").strip(),
                            recommendation="Review and address this compliance gap according to applicable regulations.",
                        )
                    )
        return issues[:10]

    async def generate_full_report(
        self, document_contents: List[str], document_ids: List[str], query: Optional[str] = None
    ) -> ReportResponse:
        """Generate a comprehensive analysis report."""
        start_time = time.time()
        combined = "\n\n---\n\n".join(document_contents[:5])
        focus = f"\nAnalysis Focus: {query}" if query else ""

        prompt = f"""Perform a comprehensive analysis of the following enterprise documents.
{focus}

Documents:
{combined[:7000]}

Generate a detailed report including:
1. Executive Summary
2. Document Overview (type, purpose, key stakeholders)
3. Key Findings and Insights
4. Risk Assessment
5. Strategic Recommendations
6. Next Steps and Action Items
7. Appendix (technical details, statistics)

Make the report professional and actionable."""

        system_prompt = """You are a senior business analyst and consultant. 
Generate comprehensive, professional reports that provide actionable insights for enterprise decision-makers."""

        response = await self.llm.generate(prompt, system_prompt)
        lines = response.split("\n")
        key_findings = [
            line.strip("- •*").strip()
            for line in lines
            if line.strip().startswith(("-", "•", "*")) and len(line.strip()) > 15
        ][:10]
        recommendations = [
            line.strip("- •*").strip()
            for line in lines
            if any(word in line.lower() for word in ["recommend", "suggest", "action", "next step"])
            and len(line.strip()) > 20
        ][:10]

        return ReportResponse(
            report_id=str(uuid.uuid4()),
            action_type=ActionType.GENERATE_REPORT,
            title="Enterprise Document Analysis Report",
            summary=response[:500] + "..." if len(response) > 500 else response,
            content=response,
            key_findings=key_findings,
            recommendations=recommendations,
            document_ids=document_ids,
            processing_time_ms=(time.time() - start_time) * 1000,
        )
