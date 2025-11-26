"""
Methodology Check Tool for StartupAI.

Validates strategic artifacts against Strategyzer methodologies:
- Value Proposition Canvas (VPC) structure and completeness
- Business Model Canvas (BMC) consistency
- Assumption mapping quality

This ensures that crews produce methodologically sound outputs
before proceeding to the next validation phase.
"""

import json
from typing import List, Optional, Dict, Any, Set
from datetime import datetime
from enum import Enum

from crewai.tools import BaseTool
from pydantic import Field, BaseModel


# =======================================================================================
# MODELS
# =======================================================================================

class CheckSeverity(str, Enum):
    """Severity levels for methodology checks."""
    CRITICAL = "critical"      # Methodology violation - cannot proceed
    WARNING = "warning"        # Should improve before proceeding
    SUGGESTION = "suggestion"  # Best practice recommendation


class MethodologyType(str, Enum):
    """Types of methodology artifacts to check."""
    VPC = "vpc"                          # Value Proposition Canvas
    BMC = "bmc"                          # Business Model Canvas
    CUSTOMER_PROFILE = "customer_profile"  # Customer segment profile
    VALUE_MAP = "value_map"              # Value map (product side of VPC)
    ASSUMPTION_MAP = "assumption_map"    # Assumption mapping


class MethodologyIssue(BaseModel):
    """A single methodology issue found."""
    severity: CheckSeverity
    component: str           # Which part of the canvas
    message: str
    suggestion: Optional[str] = None


class MethodologyCheckResult(BaseModel):
    """Result from methodology validation."""
    methodology_type: MethodologyType
    is_valid: bool
    completeness_score: float  # 0.0 to 1.0
    quality_score: float       # 0.0 to 1.0

    # Issue counts
    critical_count: int = 0
    warning_count: int = 0
    suggestion_count: int = 0

    # Detailed issues
    issues: List[MethodologyIssue] = []

    # Component completeness
    components_present: List[str] = []
    components_missing: List[str] = []

    # Summary
    summary: str = ""
    ready_for_next_phase: bool = False

    # Metadata
    checked_at: str = Field(default_factory=lambda: datetime.now().isoformat())


# =======================================================================================
# VPC COMPONENT DEFINITIONS
# =======================================================================================

VPC_CUSTOMER_PROFILE_COMPONENTS = {
    "customer_jobs": {
        "required": True,
        "min_items": 1,
        "description": "Tasks customers are trying to accomplish",
        "sub_types": ["functional_jobs", "social_jobs", "emotional_jobs"]
    },
    "pains": {
        "required": True,
        "min_items": 1,
        "description": "Negative outcomes, obstacles, or risks customers want to avoid",
        "qualities": ["intensity", "frequency"]
    },
    "gains": {
        "required": True,
        "min_items": 1,
        "description": "Outcomes and benefits customers want",
        "qualities": ["relevance", "importance"]
    }
}

VPC_VALUE_MAP_COMPONENTS = {
    "products_services": {
        "required": True,
        "min_items": 1,
        "description": "What you offer to help customers"
    },
    "pain_relievers": {
        "required": True,
        "min_items": 1,
        "description": "How your offering alleviates customer pains",
        "must_map_to": "pains"
    },
    "gain_creators": {
        "required": True,
        "min_items": 1,
        "description": "How your offering creates customer gains",
        "must_map_to": "gains"
    }
}

BMC_COMPONENTS = {
    "customer_segments": {"required": True, "min_items": 1},
    "value_propositions": {"required": True, "min_items": 1},
    "channels": {"required": True, "min_items": 1},
    "customer_relationships": {"required": True, "min_items": 1},
    "revenue_streams": {"required": True, "min_items": 1},
    "key_resources": {"required": True, "min_items": 1},
    "key_activities": {"required": True, "min_items": 1},
    "key_partnerships": {"required": False, "min_items": 0},
    "cost_structure": {"required": True, "min_items": 1},
}


# =======================================================================================
# METHODOLOGY CHECK TOOL
# =======================================================================================

class MethodologyCheckTool(BaseTool):
    """
    Validate strategic artifacts against Strategyzer methodologies.

    Checks Value Proposition Canvas, Business Model Canvas, and related
    artifacts for structural completeness and methodological soundness.

    Use this tool to:
    - Validate VPC customer profiles and value maps
    - Check BMC completeness and consistency
    - Ensure assumptions are properly mapped to canvas elements
    """

    name: str = "methodology_check"
    description: str = """
    Validate strategic artifacts against Strategyzer methodologies (VPC, BMC).

    Input should be a JSON object containing:
    - methodology_type: "vpc", "bmc", "customer_profile", "value_map", or "assumption_map"
    - artifact: The artifact data to validate (structure depends on type)
    - context: Optional context (e.g., related artifacts for cross-validation)

    For VPC validation, artifact should contain:
    - customer_profile: {customer_jobs: [], pains: [], gains: []}
    - value_map: {products_services: [], pain_relievers: [], gain_creators: []}

    For BMC validation, artifact should contain the 9 building blocks.

    Returns:
    - is_valid: Whether artifact meets minimum requirements
    - completeness_score: How complete the artifact is (0.0-1.0)
    - quality_score: Quality assessment (0.0-1.0)
    - issues: List of issues found
    - ready_for_next_phase: Whether to proceed with validation
    """

    # Configuration
    strict_mode: bool = Field(
        default=False,
        description="If True, warnings also block phase progression"
    )
    min_completeness: float = Field(
        default=0.7,
        description="Minimum completeness score to be valid"
    )

    def _run(self, input_data: str) -> str:
        """
        Validate a methodology artifact.

        Args:
            input_data: JSON string with artifact details

        Returns:
            Formatted validation result
        """
        try:
            # Parse input
            try:
                data = json.loads(input_data)
            except json.JSONDecodeError:
                return self._format_error("Invalid JSON input")

            methodology_type = data.get("methodology_type", "").lower()
            artifact = data.get("artifact", {})
            context = data.get("context", {})

            # Validate methodology type
            try:
                mtype = MethodologyType(methodology_type)
            except ValueError:
                return self._format_error(f"Unknown methodology type: {methodology_type}")

            # Route to appropriate validator
            if mtype == MethodologyType.VPC:
                result = self._validate_vpc(artifact, context)
            elif mtype == MethodologyType.BMC:
                result = self._validate_bmc(artifact, context)
            elif mtype == MethodologyType.CUSTOMER_PROFILE:
                result = self._validate_customer_profile(artifact, context)
            elif mtype == MethodologyType.VALUE_MAP:
                result = self._validate_value_map(artifact, context)
            elif mtype == MethodologyType.ASSUMPTION_MAP:
                result = self._validate_assumption_map(artifact, context)
            else:
                return self._format_error(f"Validator not implemented for: {mtype}")

            return self._format_output(result)

        except Exception as e:
            return self._format_error(f"Validation failed: {str(e)}")

    async def _arun(self, input_data: str) -> str:
        """Async version - delegates to sync."""
        return self._run(input_data)

    def _validate_vpc(
        self,
        artifact: Dict[str, Any],
        context: Dict[str, Any]
    ) -> MethodologyCheckResult:
        """Validate a complete Value Proposition Canvas."""
        issues: List[MethodologyIssue] = []
        components_present: List[str] = []
        components_missing: List[str] = []

        customer_profile = artifact.get("customer_profile", {})
        value_map = artifact.get("value_map", {})

        # Validate customer profile
        cp_result = self._validate_customer_profile(customer_profile, context)
        issues.extend(cp_result.issues)
        components_present.extend([f"customer_profile.{c}" for c in cp_result.components_present])
        components_missing.extend([f"customer_profile.{c}" for c in cp_result.components_missing])

        # Validate value map
        vm_result = self._validate_value_map(value_map, {"customer_profile": customer_profile})
        issues.extend(vm_result.issues)
        components_present.extend([f"value_map.{c}" for c in vm_result.components_present])
        components_missing.extend([f"value_map.{c}" for c in vm_result.components_missing])

        # Cross-validation: Check fit between profile and map
        fit_issues = self._check_vpc_fit(customer_profile, value_map)
        issues.extend(fit_issues)

        # Calculate scores
        completeness = self._calculate_completeness(components_present, components_missing)
        quality = self._calculate_quality(issues)

        # Determine validity
        critical_count = sum(1 for i in issues if i.severity == CheckSeverity.CRITICAL)
        warning_count = sum(1 for i in issues if i.severity == CheckSeverity.WARNING)
        suggestion_count = sum(1 for i in issues if i.severity == CheckSeverity.SUGGESTION)

        is_valid = critical_count == 0 and completeness >= self.min_completeness
        ready = is_valid and (not self.strict_mode or warning_count == 0)

        return MethodologyCheckResult(
            methodology_type=MethodologyType.VPC,
            is_valid=is_valid,
            completeness_score=completeness,
            quality_score=quality,
            critical_count=critical_count,
            warning_count=warning_count,
            suggestion_count=suggestion_count,
            issues=issues,
            components_present=components_present,
            components_missing=components_missing,
            summary=self._generate_summary("VPC", is_valid, completeness, quality, critical_count, warning_count),
            ready_for_next_phase=ready,
        )

    def _validate_customer_profile(
        self,
        artifact: Dict[str, Any],
        context: Dict[str, Any]
    ) -> MethodologyCheckResult:
        """Validate a VPC Customer Profile."""
        issues: List[MethodologyIssue] = []
        components_present: List[str] = []
        components_missing: List[str] = []

        for component, spec in VPC_CUSTOMER_PROFILE_COMPONENTS.items():
            items = artifact.get(component, [])

            if not items:
                if spec["required"]:
                    components_missing.append(component)
                    issues.append(MethodologyIssue(
                        severity=CheckSeverity.CRITICAL,
                        component=component,
                        message=f"Missing required component: {component}",
                        suggestion=spec["description"]
                    ))
            else:
                components_present.append(component)

                # Check minimum items
                if len(items) < spec.get("min_items", 1):
                    issues.append(MethodologyIssue(
                        severity=CheckSeverity.WARNING,
                        component=component,
                        message=f"Only {len(items)} {component} found (minimum {spec['min_items']})",
                        suggestion=f"Add more {component} for thorough analysis"
                    ))

                # Check for job types if applicable
                if component == "customer_jobs" and "sub_types" in spec:
                    job_types_found = self._check_job_types(items, spec["sub_types"])
                    if len(job_types_found) < 2:
                        issues.append(MethodologyIssue(
                            severity=CheckSeverity.SUGGESTION,
                            component=component,
                            message="Consider adding different job types",
                            suggestion="Include functional, social, and emotional jobs for completeness"
                        ))

        completeness = self._calculate_completeness(components_present, components_missing)
        quality = self._calculate_quality(issues)
        critical_count = sum(1 for i in issues if i.severity == CheckSeverity.CRITICAL)
        warning_count = sum(1 for i in issues if i.severity == CheckSeverity.WARNING)
        suggestion_count = sum(1 for i in issues if i.severity == CheckSeverity.SUGGESTION)

        return MethodologyCheckResult(
            methodology_type=MethodologyType.CUSTOMER_PROFILE,
            is_valid=critical_count == 0 and completeness >= self.min_completeness,
            completeness_score=completeness,
            quality_score=quality,
            critical_count=critical_count,
            warning_count=warning_count,
            suggestion_count=suggestion_count,
            issues=issues,
            components_present=components_present,
            components_missing=components_missing,
            summary=self._generate_summary("Customer Profile", critical_count == 0, completeness, quality, critical_count, warning_count),
            ready_for_next_phase=critical_count == 0,
        )

    def _validate_value_map(
        self,
        artifact: Dict[str, Any],
        context: Dict[str, Any]
    ) -> MethodologyCheckResult:
        """Validate a VPC Value Map."""
        issues: List[MethodologyIssue] = []
        components_present: List[str] = []
        components_missing: List[str] = []

        customer_profile = context.get("customer_profile", {})

        for component, spec in VPC_VALUE_MAP_COMPONENTS.items():
            items = artifact.get(component, [])

            if not items:
                if spec["required"]:
                    components_missing.append(component)
                    issues.append(MethodologyIssue(
                        severity=CheckSeverity.CRITICAL,
                        component=component,
                        message=f"Missing required component: {component}",
                        suggestion=spec["description"]
                    ))
            else:
                components_present.append(component)

                # Check mapping to customer profile
                if "must_map_to" in spec and customer_profile:
                    target_component = spec["must_map_to"]
                    target_items = customer_profile.get(target_component, [])

                    if target_items and len(items) < len(target_items) * 0.5:
                        issues.append(MethodologyIssue(
                            severity=CheckSeverity.WARNING,
                            component=component,
                            message=f"Few {component} relative to customer {target_component}",
                            suggestion=f"Ensure each key {target_component[:-1]} has a corresponding {component[:-1]}"
                        ))

        completeness = self._calculate_completeness(components_present, components_missing)
        quality = self._calculate_quality(issues)
        critical_count = sum(1 for i in issues if i.severity == CheckSeverity.CRITICAL)
        warning_count = sum(1 for i in issues if i.severity == CheckSeverity.WARNING)
        suggestion_count = sum(1 for i in issues if i.severity == CheckSeverity.SUGGESTION)

        return MethodologyCheckResult(
            methodology_type=MethodologyType.VALUE_MAP,
            is_valid=critical_count == 0 and completeness >= self.min_completeness,
            completeness_score=completeness,
            quality_score=quality,
            critical_count=critical_count,
            warning_count=warning_count,
            suggestion_count=suggestion_count,
            issues=issues,
            components_present=components_present,
            components_missing=components_missing,
            summary=self._generate_summary("Value Map", critical_count == 0, completeness, quality, critical_count, warning_count),
            ready_for_next_phase=critical_count == 0,
        )

    def _validate_bmc(
        self,
        artifact: Dict[str, Any],
        context: Dict[str, Any]
    ) -> MethodologyCheckResult:
        """Validate a Business Model Canvas."""
        issues: List[MethodologyIssue] = []
        components_present: List[str] = []
        components_missing: List[str] = []

        for component, spec in BMC_COMPONENTS.items():
            items = artifact.get(component, [])

            if not items:
                if spec["required"]:
                    components_missing.append(component)
                    issues.append(MethodologyIssue(
                        severity=CheckSeverity.CRITICAL,
                        component=component,
                        message=f"Missing required BMC block: {component.replace('_', ' ').title()}",
                        suggestion=f"Add at least {spec['min_items']} item(s)"
                    ))
            else:
                components_present.append(component)

                if isinstance(items, list) and len(items) < spec.get("min_items", 1):
                    issues.append(MethodologyIssue(
                        severity=CheckSeverity.WARNING,
                        component=component,
                        message=f"Only {len(items)} item(s) in {component.replace('_', ' ')}",
                        suggestion="Consider expanding this section"
                    ))

        # Cross-validation checks
        if "value_propositions" in components_present and "customer_segments" in components_present:
            vp_count = len(artifact.get("value_propositions", []))
            cs_count = len(artifact.get("customer_segments", []))
            if vp_count < cs_count:
                issues.append(MethodologyIssue(
                    severity=CheckSeverity.SUGGESTION,
                    component="value_propositions",
                    message="Fewer value propositions than customer segments",
                    suggestion="Consider tailoring value propositions per segment"
                ))

        completeness = self._calculate_completeness(components_present, components_missing)
        quality = self._calculate_quality(issues)
        critical_count = sum(1 for i in issues if i.severity == CheckSeverity.CRITICAL)
        warning_count = sum(1 for i in issues if i.severity == CheckSeverity.WARNING)
        suggestion_count = sum(1 for i in issues if i.severity == CheckSeverity.SUGGESTION)

        return MethodologyCheckResult(
            methodology_type=MethodologyType.BMC,
            is_valid=critical_count == 0 and completeness >= self.min_completeness,
            completeness_score=completeness,
            quality_score=quality,
            critical_count=critical_count,
            warning_count=warning_count,
            suggestion_count=suggestion_count,
            issues=issues,
            components_present=components_present,
            components_missing=components_missing,
            summary=self._generate_summary("BMC", critical_count == 0, completeness, quality, critical_count, warning_count),
            ready_for_next_phase=critical_count == 0,
        )

    def _validate_assumption_map(
        self,
        artifact: Dict[str, Any],
        context: Dict[str, Any]
    ) -> MethodologyCheckResult:
        """Validate an assumption mapping."""
        issues: List[MethodologyIssue] = []
        components_present: List[str] = []
        components_missing: List[str] = []

        assumptions = artifact.get("assumptions", [])

        if not assumptions:
            components_missing.append("assumptions")
            issues.append(MethodologyIssue(
                severity=CheckSeverity.CRITICAL,
                component="assumptions",
                message="No assumptions defined",
                suggestion="List key assumptions that must be true for the business to succeed"
            ))
        else:
            components_present.append("assumptions")

            # Check assumption structure
            for i, assumption in enumerate(assumptions):
                if isinstance(assumption, dict):
                    if not assumption.get("hypothesis"):
                        issues.append(MethodologyIssue(
                            severity=CheckSeverity.WARNING,
                            component=f"assumption_{i}",
                            message="Assumption missing hypothesis statement",
                            suggestion="State what you believe to be true"
                        ))
                    if not assumption.get("risk_level"):
                        issues.append(MethodologyIssue(
                            severity=CheckSeverity.SUGGESTION,
                            component=f"assumption_{i}",
                            message="Assumption missing risk level",
                            suggestion="Rate as critical, important, or nice-to-validate"
                        ))

            # Check for prioritization
            if len(assumptions) > 3:
                has_priority = any(
                    isinstance(a, dict) and a.get("priority")
                    for a in assumptions
                )
                if not has_priority:
                    issues.append(MethodologyIssue(
                        severity=CheckSeverity.WARNING,
                        component="assumptions",
                        message="Multiple assumptions without prioritization",
                        suggestion="Prioritize assumptions by risk and impact"
                    ))

        completeness = 1.0 if assumptions else 0.0
        quality = self._calculate_quality(issues)
        critical_count = sum(1 for i in issues if i.severity == CheckSeverity.CRITICAL)
        warning_count = sum(1 for i in issues if i.severity == CheckSeverity.WARNING)
        suggestion_count = sum(1 for i in issues if i.severity == CheckSeverity.SUGGESTION)

        return MethodologyCheckResult(
            methodology_type=MethodologyType.ASSUMPTION_MAP,
            is_valid=critical_count == 0,
            completeness_score=completeness,
            quality_score=quality,
            critical_count=critical_count,
            warning_count=warning_count,
            suggestion_count=suggestion_count,
            issues=issues,
            components_present=components_present,
            components_missing=components_missing,
            summary=self._generate_summary("Assumption Map", critical_count == 0, completeness, quality, critical_count, warning_count),
            ready_for_next_phase=critical_count == 0,
        )

    def _check_vpc_fit(
        self,
        customer_profile: Dict[str, Any],
        value_map: Dict[str, Any]
    ) -> List[MethodologyIssue]:
        """Check the fit between customer profile and value map."""
        issues: List[MethodologyIssue] = []

        pains = customer_profile.get("pains", [])
        gains = customer_profile.get("gains", [])
        pain_relievers = value_map.get("pain_relievers", [])
        gain_creators = value_map.get("gain_creators", [])

        # Check pain relief coverage
        if pains and pain_relievers:
            relief_ratio = len(pain_relievers) / len(pains)
            if relief_ratio < 0.5:
                issues.append(MethodologyIssue(
                    severity=CheckSeverity.WARNING,
                    component="fit.pain_relief",
                    message=f"Only {len(pain_relievers)}/{len(pains)} pains have relievers",
                    suggestion="Ensure key customer pains are addressed"
                ))

        # Check gain creation coverage
        if gains and gain_creators:
            creation_ratio = len(gain_creators) / len(gains)
            if creation_ratio < 0.5:
                issues.append(MethodologyIssue(
                    severity=CheckSeverity.WARNING,
                    component="fit.gain_creation",
                    message=f"Only {len(gain_creators)}/{len(gains)} gains have creators",
                    suggestion="Ensure key customer gains are delivered"
                ))

        return issues

    def _check_job_types(self, jobs: List[Any], expected_types: List[str]) -> Set[str]:
        """Check which job types are represented."""
        types_found = set()

        for job in jobs:
            if isinstance(job, dict):
                job_type = job.get("type", "").lower()
                if job_type in expected_types:
                    types_found.add(job_type)
            elif isinstance(job, str):
                # Try to infer type from content
                job_lower = job.lower()
                if any(word in job_lower for word in ["feel", "appear", "seem", "emotion"]):
                    types_found.add("emotional_jobs")
                elif any(word in job_lower for word in ["look", "status", "impress", "social"]):
                    types_found.add("social_jobs")
                else:
                    types_found.add("functional_jobs")

        return types_found

    def _calculate_completeness(
        self,
        present: List[str],
        missing: List[str]
    ) -> float:
        """Calculate completeness score."""
        total = len(present) + len(missing)
        if total == 0:
            return 0.0
        return len(present) / total

    def _calculate_quality(self, issues: List[MethodologyIssue]) -> float:
        """Calculate quality score based on issues."""
        if not issues:
            return 1.0

        # Weight by severity
        penalty = 0.0
        for issue in issues:
            if issue.severity == CheckSeverity.CRITICAL:
                penalty += 0.3
            elif issue.severity == CheckSeverity.WARNING:
                penalty += 0.1
            else:
                penalty += 0.02

        return max(0.0, 1.0 - penalty)

    def _generate_summary(
        self,
        artifact_name: str,
        is_valid: bool,
        completeness: float,
        quality: float,
        critical: int,
        warning: int
    ) -> str:
        """Generate human-readable summary."""
        status = "VALID" if is_valid else "INVALID"
        comp_pct = int(completeness * 100)
        qual_pct = int(quality * 100)

        if is_valid and quality >= 0.8:
            return f"✅ {artifact_name} is {status}: {comp_pct}% complete, {qual_pct}% quality"
        elif is_valid:
            return f"⚠️ {artifact_name} is {status} but needs improvement: {warning} warning(s)"
        else:
            return f"❌ {artifact_name} is {status}: {critical} critical issue(s) must be fixed"

    def _format_output(self, result: MethodologyCheckResult) -> str:
        """Format validation result for agent consumption."""
        lines = [
            "## Methodology Check Complete",
            "",
            f"**Type:** {result.methodology_type.value.upper()}",
            f"**Status:** {result.summary}",
            "",
            f"- Completeness: {int(result.completeness_score * 100)}%",
            f"- Quality: {int(result.quality_score * 100)}%",
            f"- Ready for Next Phase: {'Yes' if result.ready_for_next_phase else 'No'}",
            "",
            f"**Issues:** {result.critical_count} critical, {result.warning_count} warnings, {result.suggestion_count} suggestions",
            "",
        ]

        if result.components_missing:
            lines.append("### Missing Components")
            for comp in result.components_missing:
                lines.append(f"- ❌ {comp}")
            lines.append("")

        if result.issues:
            lines.append("### Issues Found")
            lines.append("")

            for severity in [CheckSeverity.CRITICAL, CheckSeverity.WARNING, CheckSeverity.SUGGESTION]:
                severity_issues = [i for i in result.issues if i.severity == severity]
                if severity_issues:
                    icon = "🔴" if severity == CheckSeverity.CRITICAL else "🟡" if severity == CheckSeverity.WARNING else "🔵"
                    lines.append(f"#### {icon} {severity.value.title()}s")
                    for issue in severity_issues:
                        lines.append(f"- **[{issue.component}]** {issue.message}")
                        if issue.suggestion:
                            lines.append(f"  - 💡 {issue.suggestion}")
                    lines.append("")

        return "\n".join(lines)

    def _format_error(self, message: str) -> str:
        """Format error message."""
        return f"## Methodology Check Failed\n\n❌ {message}"


# =======================================================================================
# CONVENIENCE FUNCTIONS
# =======================================================================================

def check_vpc(
    customer_profile: Dict[str, Any],
    value_map: Dict[str, Any]
) -> str:
    """
    Convenience function to validate a Value Proposition Canvas.

    Args:
        customer_profile: Customer profile with jobs, pains, gains
        value_map: Value map with products, pain relievers, gain creators

    Returns:
        Formatted validation result
    """
    tool = MethodologyCheckTool()
    return tool._run(json.dumps({
        "methodology_type": "vpc",
        "artifact": {
            "customer_profile": customer_profile,
            "value_map": value_map
        }
    }))


def check_bmc(bmc: Dict[str, Any]) -> str:
    """
    Convenience function to validate a Business Model Canvas.

    Args:
        bmc: Dict with the 9 BMC building blocks

    Returns:
        Formatted validation result
    """
    tool = MethodologyCheckTool()
    return tool._run(json.dumps({
        "methodology_type": "bmc",
        "artifact": bmc
    }))
