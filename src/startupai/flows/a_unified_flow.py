"""
Unified Entry Flow for CrewAI AMP deployment.

CRITICAL: This file is named 'a_unified_flow.py' to ensure it is discovered
FIRST by CrewAI AMP's alphabetical flow discovery. This is the ONLY flow
that AMP should instantiate and run.

The flow routes to the appropriate sub-flow based on the 'flow_type' input:
- "founder_validation" (default): Full business idea validation
- "consultant_onboarding": Consultant practice analysis

Architecture:
    /kickoff {flow_type: "founder_validation", ...}
        |
        v
    StartupAIUnifiedFlow.dispatch()
        |
        +--[founder_validation]--> FounderValidationFlow.kickoff()
        |
        +--[consultant_onboarding]--> ConsultantOnboardingFlow.kickoff()
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
from crewai.flow.flow import Flow, start, listen, router
from crewai.flow.persistence import persist
import traceback
import os


class FlowType(str, Enum):
    """Supported flow types for routing"""
    FOUNDER_VALIDATION = "founder_validation"
    CONSULTANT_ONBOARDING = "consultant_onboarding"


class UnifiedFlowState(BaseModel):
    """
    Unified state schema covering ALL inputs for all flow types.
    
    CrewAI AMP uses this schema to generate the /inputs endpoint.
    All fields from both FounderValidation and ConsultantOnboarding
    are included to support both flow types.
    """
    # === FLOW ROUTING ===
    flow_type: str = Field(
        default="founder_validation",
        description="Type of flow to run: 'founder_validation' or 'consultant_onboarding'"
    )
    
    # === FOUNDER VALIDATION INPUTS ===
    entrepreneur_input: str = Field(
        default="",
        description="Business idea description for founder validation"
    )
    project_id: Optional[str] = Field(
        default=None,
        description="UUID of project in product app"
    )
    
    # === SHARED INPUTS ===
    user_id: Optional[str] = Field(
        default=None,
        description="UUID of user in product app"
    )
    session_id: Optional[str] = Field(
        default=None,
        description="Onboarding session ID"
    )
    kickoff_id: Optional[str] = Field(
        default=None,
        description="CrewAI kickoff ID for status tracking"
    )
    
    # === CONSULTANT ONBOARDING INPUTS ===
    practice_data: Dict[str, Any] = Field(
        default_factory=dict,
        description="Consultant practice data (company_name, practice_size, industries, etc.)"
    )
    conversation_summary: str = Field(
        default="",
        description="Summary of onboarding conversation"
    )
    
    # === OUTPUT FIELDS ===
    result: Dict[str, Any] = Field(
        default_factory=dict,
        description="Result from the executed sub-flow"
    )
    error: Optional[str] = Field(
        default=None,
        description="Error message if flow failed"
    )
    status: str = Field(
        default="pending",
        description="Flow status: pending, running, success, failed"
    )
    completed_at: Optional[str] = Field(
        default=None,
        description="ISO timestamp when flow completed"
    )


class AMPEntryFlow(Flow[UnifiedFlowState]):
    """
    Primary entry point flow for CrewAI AMP deployment.

    CRITICAL: This class is named 'AMPEntryFlow' to ensure it's discovered
    FIRST alphabetically before other flows (ConsultantOnboarding, Founder...).

    CrewAI AMP auto-discovers Flow subclasses and picks one as primary.
    By naming this class with 'AMP' prefix, we ensure it comes first.

    This flow routes to sub-flows based on the 'flow_type' input parameter:
    - "founder_validation" (default): Full business idea validation
    - "consultant_onboarding": Consultant practice analysis
    """
    
    @persist()
    @start()
    def dispatch(self):
        """
        Entry point: Dispatch to appropriate sub-flow based on flow_type.
        
        This method:
        1. Validates the flow_type input
        2. Returns the flow_type as a routing label
        3. Triggers the corresponding @listen handler
        """
        flow_type = self.state.flow_type
        self.state.status = "running"
        
        print(f"\n{'='*80}")
        print("STARTUPAI UNIFIED FLOW - DISPATCHER")
        print(f"{'='*80}")
        print(f"[DISPATCH] Flow Type: {flow_type}")
        print(f"[DISPATCH] Timestamp: {datetime.now().isoformat()}")
        print(f"[DISPATCH] Kickoff ID: {self.state.kickoff_id}")
        
        # Log key inputs for debugging
        if flow_type == "founder_validation":
            input_len = len(self.state.entrepreneur_input or "")
            print(f"[DISPATCH] Entrepreneur Input: {input_len} chars")
            print(f"[DISPATCH] Project ID: {self.state.project_id}")
        elif flow_type == "consultant_onboarding":
            print(f"[DISPATCH] Practice Data Keys: {list(self.state.practice_data.keys())}")
        
        print(f"{'='*80}\n")
        
        # Validate flow_type
        valid_types = [ft.value for ft in FlowType]
        if flow_type not in valid_types:
            error_msg = f"Invalid flow_type: '{flow_type}'. Valid types: {valid_types}"
            print(f"[ERROR] {error_msg}")
            self.state.error = error_msg
            self.state.status = "failed"
            return "error"
        
        # Return flow_type as routing label
        print(f"[DISPATCH] Routing to: {flow_type}")
        return flow_type
    
    @listen("founder_validation")
    def run_founder_validation(self):
        """
        Execute the founder validation flow.
        
        Imports and runs FounderValidationFlow with the provided inputs.
        Stores the result in self.state.result.
        """
        print("\n>>> Executing FOUNDER VALIDATION flow")
        
        # Validate required inputs
        if not self.state.entrepreneur_input:
            self.state.error = "Missing required input: entrepreneur_input"
            self.state.status = "failed"
            print(f"[ERROR] {self.state.error}")
            return
        
        try:
            # Import sub-flow (late import to avoid circular deps)
            from startupai.flows._founder_validation_flow import (
                create_founder_validation_flow
            )
            
            # Create and run the sub-flow
            flow = create_founder_validation_flow(
                entrepreneur_input=self.state.entrepreneur_input,
                project_id=self.state.project_id,
                user_id=self.state.user_id,
                session_id=self.state.session_id,
                kickoff_id=self.state.kickoff_id,
            )
            
            print("[FOUNDER] Starting validation flow kickoff...")
            result = flow.kickoff()
            
            # Store result
            if isinstance(result, dict):
                self.state.result = result
            else:
                self.state.result = {"raw": str(result)}
            
            self.state.status = "success"
            self.state.completed_at = datetime.now().isoformat()
            
            print(f"\n{'='*80}")
            print("[FOUNDER] Validation completed successfully!")
            print(f"[FOUNDER] Result keys: {list(self.state.result.keys())}")
            print(f"{'='*80}\n")
            
        except Exception as e:
            self.state.error = f"Founder validation failed: {str(e)}"
            self.state.status = "failed"
            print(f"[ERROR] {self.state.error}")
            traceback.print_exc()
    
    @listen("consultant_onboarding")
    def run_consultant_onboarding(self):
        """
        Execute the consultant onboarding flow.
        
        Imports and runs ConsultantOnboardingFlow with the provided inputs.
        Stores the result in self.state.result.
        """
        print("\n>>> Executing CONSULTANT ONBOARDING flow")
        
        # Validate required inputs
        if not self.state.user_id:
            self.state.error = "Missing required input: user_id"
            self.state.status = "failed"
            print(f"[ERROR] {self.state.error}")
            return
        
        if not self.state.session_id:
            self.state.error = "Missing required input: session_id"
            self.state.status = "failed"
            print(f"[ERROR] {self.state.error}")
            return
        
        try:
            # Import sub-flow (late import to avoid circular deps)
            from startupai.flows._consultant_onboarding_flow import (
                create_consultant_onboarding_flow
            )
            
            # Create and run the sub-flow
            flow = create_consultant_onboarding_flow(
                user_id=self.state.user_id,
                session_id=self.state.session_id,
                practice_data=self.state.practice_data,
                conversation_summary=self.state.conversation_summary,
            )
            
            print("[CONSULTANT] Starting onboarding flow kickoff...")
            result = flow.kickoff()
            
            # Store result
            if isinstance(result, dict):
                self.state.result = result
            else:
                self.state.result = {"raw": str(result)}
            
            self.state.status = "success"
            self.state.completed_at = datetime.now().isoformat()
            
            print(f"\n{'='*80}")
            print("[CONSULTANT] Onboarding completed successfully!")
            print(f"[CONSULTANT] Result keys: {list(self.state.result.keys())}")
            print(f"{'='*80}\n")
            
        except Exception as e:
            self.state.error = f"Consultant onboarding failed: {str(e)}"
            self.state.status = "failed"
            print(f"[ERROR] {self.state.error}")
            traceback.print_exc()
    
    @listen("error")
    def handle_error(self):
        """Handle routing/validation errors."""
        print(f"\n[ERROR HANDLER] Flow error: {self.state.error}")
        self.state.status = "failed"
        self.state.completed_at = datetime.now().isoformat()


# =============================================================================
# FACTORY FUNCTIONS
# =============================================================================

def create_unified_flow(
    flow_type: str = "founder_validation",
    **kwargs
) -> AMPEntryFlow:
    """
    Create a unified flow instance.

    Args:
        flow_type: "founder_validation" or "consultant_onboarding"
        **kwargs: Flow-specific inputs

    Returns:
        Configured AMPEntryFlow ready to run
    """
    return AMPEntryFlow(
        flow_type=flow_type,
        **kwargs
    )


# Backward compatibility alias
StartupAIUnifiedFlow = AMPEntryFlow


# =============================================================================
# MAIN.PY COMPATIBILITY
# =============================================================================
# These functions match the expected interface for main.py

def kickoff(inputs: dict = None):
    """
    Main entry point for CrewAI AMP deployment.

    This function is called when the flow is triggered via the AMP API
    or via `crewai run`.
    """
    if inputs is None:
        inputs = {}

    flow_type = inputs.pop("flow_type", "founder_validation")

    flow = AMPEntryFlow(
        flow_type=flow_type,
        **inputs
    )

    return flow.kickoff()


def plot(filename: str = "startupai_unified_flow"):
    """Generate flow visualization."""
    flow = AMPEntryFlow()
    flow.plot(filename)
    print(f"Flow visualization saved to {filename}.html")
