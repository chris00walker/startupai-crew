#!/usr/bin/env python
"""
CrewAI AMP Entry Point for StartupAI Flows.

This is the PRIMARY entry point for CrewAI AMP deployment.
Following the standard CrewAI template pattern, this file must be at the project root.

The StartupAIFlow class defined here is the ONLY Flow that CrewAI AMP should discover
and use. It routes to sub-flows internally based on the 'flow_type' input:
- "founder_validation" (default): Full business idea validation
- "consultant_onboarding": Consultant practice analysis and recommendations
"""

from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
from crewai.flow.flow import Flow, start, listen
from dotenv import load_dotenv
import os
import traceback


class FlowType(str, Enum):
    """Supported flow types for routing."""
    FOUNDER_VALIDATION = "founder_validation"
    CONSULTANT_ONBOARDING = "consultant_onboarding"


class StartupAIFlowState(BaseModel):
    """
    Unified state schema for all StartupAI flows.
    
    CrewAI AMP uses this schema to generate the /inputs endpoint.
    All fields support both founder_validation and consultant_onboarding flows.
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


class StartupAIFlow(Flow[StartupAIFlowState]):
    """
    Primary entry point flow for CrewAI AMP deployment.
    
    This is the ONLY Flow class that should be discovered by CrewAI AMP.
    It routes to sub-flows internally based on the 'flow_type' input.
    """
    
    @start()
    def dispatch(self):
        """
        Entry point: Route to appropriate sub-flow based on flow_type.
        """
        # Load environment variables
        load_dotenv()
        
        flow_type = self.state.flow_type
        self.state.status = "running"
        
        print(f"\n{'='*80}")
        print("STARTUPAI FLOW - ENTRY POINT")
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
            return
        
        # Verify OpenAI API key is set
        if not os.getenv("OPENAI_API_KEY"):
            self.state.error = "OPENAI_API_KEY not found in environment variables"
            self.state.status = "failed"
            print(f"[ERROR] {self.state.error}")
            return
        
        # Route to appropriate sub-flow
        print(f"[DISPATCH] Routing to: {flow_type}")
        return flow_type
    
    @listen("founder_validation")
    def run_founder_validation(self):
        """Execute the founder validation flow."""
        print("\n>>> Executing FOUNDER VALIDATION flow")
        
        # Validate required inputs
        if not self.state.entrepreneur_input:
            self.state.error = "Missing required input: entrepreneur_input"
            self.state.status = "failed"
            print(f"[ERROR] {self.state.error}")
            return
        
        try:
            # Import sub-flow (late import to avoid circular deps)
            from startupai.flows.founder_validation_flow import (
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
        """Execute the consultant onboarding flow."""
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
            from startupai.flows.consultant_onboarding_flow import (
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


def kickoff(inputs: dict = None):
    """
    Main entry point for CrewAI AMP deployment.
    
    This function follows the standard CrewAI template pattern.
    """
    if inputs is None:
        inputs = {}
    
    flow = StartupAIFlow(**inputs)
    result = flow.kickoff()
    
    # Return the full state as result for AMP
    return {
        "result": flow.state.result,
        "status": flow.state.status,
        "error": flow.state.error,
        "completed_at": flow.state.completed_at,
        "flow_type": flow.state.flow_type,
    }


def plot():
    """Generate flow visualization."""
    flow = StartupAIFlow()
    flow.plot("startupai_flow")
    print("Flow visualization saved to startupai_flow.html")


if __name__ == "__main__":
    # Test with founder validation by default
    test_inputs = {
        "flow_type": "founder_validation",
        "entrepreneur_input": """
        Test idea: AI-powered meal planning app that helps busy professionals 
        eat healthier by generating personalized meal plans based on their 
        dietary preferences, schedule, and local grocery availability.
        """,
        "project_id": "test-project-789",
        "user_id": "test-user-123",
    }
    
    print("\nTesting StartupAI Flow...")
    result = kickoff(test_inputs)
    print(f"\nResult: {result}")
