"""
Tests for Area 3, 6, and 7 Improvements.

Area 3: Policy Versioning (PolicyBandit, ExperimentConfigResolver)
Area 6: Budget Guardrails (BudgetGuardrails, DecisionLog)
Area 7: Business Model Viability (UnitEconomicsModels, BusinessModelClassifier)
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

# Add src to path
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from startupai.flows.state_schemas import (
    StartupValidationState,
    Phase,
    PolicyVersion,
    BusinessModelType,
    EnforcementMode,
    BudgetStatus,
    ViabilityMetrics,
)


# ==============================================================================
# AREA 3: Policy Versioning Tests
# ==============================================================================

class TestPolicyBandit:
    """Tests for PolicyBandit class."""

    def test_default_config_loaded(self):
        """Test that default config is loaded when file missing."""
        from startupai.tools.policy_bandit import PolicyBandit

        bandit = PolicyBandit(config_path="/nonexistent/path.yaml")
        assert bandit.config is not None
        assert 'global' in bandit.config
        assert bandit.config['global']['default_policy'] == 'yaml_baseline'

    def test_select_policy_returns_baseline_when_disabled(self):
        """Test that baseline is returned when bandit is disabled."""
        from startupai.tools.policy_bandit import PolicyBandit

        bandit = PolicyBandit()
        bandit.config['global']['bandit_enabled'] = False

        result = bandit.select_policy('ad_creative')

        assert result.is_usable
        assert result.data.selected_policy == PolicyVersion.YAML_BASELINE
        assert 'disabled' in result.data.selection_reason.lower()

    @patch('startupai.tools.policy_bandit.get_supabase_client')
    def test_select_policy_exploration_mode(self, mock_supabase):
        """Test exploration mode when insufficient samples."""
        from startupai.tools.policy_bandit import PolicyBandit

        mock_client = MagicMock()
        mock_client.rpc.return_value.execute.return_value = Mock(data=[])
        mock_supabase.return_value = mock_client

        bandit = PolicyBandit()
        result = bandit.select_policy('ad_creative')

        assert result.is_usable
        assert result.data.exploration_used is True

    def test_convenience_function_select_experiment_policy(self):
        """Test select_experiment_policy convenience function."""
        from startupai.tools.policy_bandit import select_experiment_policy

        with patch('startupai.tools.policy_bandit.PolicyBandit') as MockBandit:
            mock_instance = MockBandit.return_value
            mock_result = Mock()
            mock_result.is_usable = True
            mock_result.data = Mock(
                selected_policy=PolicyVersion.YAML_BASELINE,
                selection_reason="Test reason"
            )
            mock_instance.select_policy.return_value = mock_result

            policy, reason = select_experiment_policy('ad_creative')

            assert policy == PolicyVersion.YAML_BASELINE
            assert reason == "Test reason"


class TestExperimentConfigResolver:
    """Tests for ExperimentConfigResolver class."""

    def test_resolve_baseline_config(self):
        """Test baseline config resolution."""
        from startupai.tools.experiment_config_resolver import ExperimentConfigResolver

        resolver = ExperimentConfigResolver()
        config = resolver._resolve_baseline('ad_creative')

        assert config.experiment_type == 'ad_creative'
        assert config.config_source == 'yaml_baseline'
        assert len(config.hook_types) > 0
        assert len(config.tones) > 0

    def test_resolve_unknown_type_falls_back(self):
        """Test that unknown experiment type uses fallback."""
        from startupai.tools.experiment_config_resolver import ExperimentConfigResolver

        resolver = ExperimentConfigResolver()
        config = resolver._resolve_baseline('unknown_type')

        # Should fall back to ad_creative defaults
        assert config.experiment_type == 'unknown_type'

    @patch('startupai.tools.experiment_config_resolver.select_experiment_policy')
    @patch('startupai.tools.experiment_config_resolver.log_policy_selection')
    def test_resolve_with_forced_policy(self, mock_log, mock_select):
        """Test resolution with forced policy."""
        from startupai.tools.experiment_config_resolver import ExperimentConfigResolver
        from startupai.flows.state_schemas import StartupValidationState

        resolver = ExperimentConfigResolver()
        state = StartupValidationState(
            project_id="test_001",
            entrepreneur_input="Test",
        )

        result = resolver.resolve(
            'ad_creative',
            state,
            force_policy=PolicyVersion.RETRIEVAL_V1
        )

        assert result.is_usable
        assert result.data.config.policy_version == PolicyVersion.RETRIEVAL_V1
        # Bandit should not be called when forcing policy
        mock_select.assert_not_called()


# ==============================================================================
# AREA 6: Budget Guardrails Tests
# ==============================================================================

class TestBudgetGuardrails:
    """Tests for BudgetGuardrails class."""

    def test_default_config_loaded(self):
        """Test that default config is loaded."""
        from startupai.tools.budget_guardrails import BudgetGuardrails

        guardrails = BudgetGuardrails(config_path="/nonexistent/path.yaml")
        assert guardrails.config is not None
        assert 'thresholds' in guardrails.config

    @patch('startupai.tools.budget_guardrails.get_supabase_client')
    def test_check_budget_ok(self, mock_supabase):
        """Test budget check when within limits."""
        from startupai.tools.budget_guardrails import BudgetGuardrails

        mock_client = MagicMock()
        mock_client.rpc.return_value.execute.return_value = Mock(data=None)
        mock_supabase.return_value = mock_client

        guardrails = BudgetGuardrails()
        guardrails.config['global']['log_all_decisions'] = False

        result = guardrails.check_budget(
            project_id="test_001",
            current_spend_usd=50.0,
            budget_limit_usd=500.0,
        )

        assert result.is_usable
        assert result.data.allowed is True
        assert result.data.budget_status == BudgetStatus.OK

    @patch('startupai.tools.budget_guardrails.get_supabase_client')
    def test_check_budget_warning_threshold(self, mock_supabase):
        """Test budget check at warning threshold."""
        from startupai.tools.budget_guardrails import BudgetGuardrails

        mock_client = MagicMock()
        mock_supabase.return_value = mock_client

        guardrails = BudgetGuardrails()
        guardrails.config['global']['log_all_decisions'] = False

        result = guardrails.check_budget(
            project_id="test_001",
            current_spend_usd=450.0,
            budget_limit_usd=500.0,
        )

        assert result.is_usable
        assert result.data.allowed is True  # Warning doesn't block
        assert result.data.budget_status == BudgetStatus.WARNING
        assert result.data.threshold_triggered == 'warning'

    @patch('startupai.tools.budget_guardrails.get_supabase_client')
    def test_check_budget_kill_switch_hard_mode(self, mock_supabase):
        """Test kill switch in hard mode blocks."""
        from startupai.tools.budget_guardrails import BudgetGuardrails

        mock_client = MagicMock()
        mock_supabase.return_value = mock_client

        guardrails = BudgetGuardrails()
        guardrails.config['global']['log_all_decisions'] = False

        result = guardrails.check_budget(
            project_id="test_001",
            current_spend_usd=650.0,
            budget_limit_usd=500.0,
            enforcement_mode=EnforcementMode.HARD,
        )

        assert result.is_usable
        assert result.data.allowed is False  # Hard mode blocks
        assert result.data.budget_status == BudgetStatus.EXCEEDED

    @patch('startupai.tools.budget_guardrails.get_supabase_client')
    def test_check_budget_kill_switch_soft_mode(self, mock_supabase):
        """Test kill switch in soft mode allows with warning."""
        from startupai.tools.budget_guardrails import BudgetGuardrails

        mock_client = MagicMock()
        mock_supabase.return_value = mock_client

        guardrails = BudgetGuardrails()
        guardrails.config['global']['log_all_decisions'] = False

        result = guardrails.check_budget(
            project_id="test_001",
            current_spend_usd=650.0,
            budget_limit_usd=500.0,
            enforcement_mode=EnforcementMode.SOFT,
        )

        assert result.is_usable
        assert result.data.allowed is True  # Soft mode allows
        assert result.data.budget_status == BudgetStatus.EXCEEDED

    @patch('startupai.tools.budget_guardrails.get_supabase_client')
    def test_check_budget_critical_always_blocks(self, mock_supabase):
        """Test critical threshold always blocks regardless of mode."""
        from startupai.tools.budget_guardrails import BudgetGuardrails

        mock_client = MagicMock()
        mock_supabase.return_value = mock_client

        guardrails = BudgetGuardrails()
        guardrails.config['global']['log_all_decisions'] = False

        result = guardrails.check_budget(
            project_id="test_001",
            current_spend_usd=800.0,  # 160% of budget
            budget_limit_usd=500.0,
            enforcement_mode=EnforcementMode.SOFT,
        )

        assert result.is_usable
        assert result.data.allowed is False  # Critical always blocks
        assert result.data.budget_status == BudgetStatus.KILL_TRIGGERED


class TestDecisionLog:
    """Tests for DecisionLog persistence."""

    @patch('startupai.persistence.decision_log.get_supabase_client')
    def test_log_decision_success(self, mock_supabase):
        """Test successful decision logging."""
        from startupai.persistence.decision_log import (
            DecisionLogger, DecisionRecord, DecisionType, ActorType
        )

        mock_client = MagicMock()
        mock_client.rpc.return_value.execute.return_value = Mock(
            data='test-uuid-123'
        )
        mock_supabase.return_value = mock_client

        logger = DecisionLogger()
        record = DecisionRecord(
            project_id="test_001",
            decision_type=DecisionType.BUDGET_CHECK,
            decision_point="test_point",
            decision="approved",
            actor_type=ActorType.SYSTEM,
        )

        result = logger.log_decision(record)

        assert result.is_success
        mock_client.rpc.assert_called_once()

    def test_log_human_approval_convenience(self):
        """Test log_human_approval convenience function."""
        from startupai.persistence.decision_log import log_human_approval

        with patch('startupai.persistence.decision_log.DecisionLogger') as MockLogger:
            mock_instance = MockLogger.return_value
            mock_result = Mock()
            mock_result.is_success = True
            mock_result.data = 'test-uuid'
            mock_instance.log_decision.return_value = mock_result

            result = log_human_approval(
                project_id="test_001",
                decision_point="test",
                approved=True,
                rationale="Test reason",
                actor_id="user_123",
            )

            assert result.is_success


# ==============================================================================
# AREA 7: Business Model Viability Tests
# ==============================================================================

class TestBusinessModelClassifier:
    """Tests for BusinessModelClassifier."""

    def test_classify_saas_b2b_smb(self):
        """Test classification of SaaS B2B SMB."""
        from startupai.tools.business_model_classifier import BusinessModelClassifier

        classifier = BusinessModelClassifier()
        result = classifier.classify(
            business_description="SaaS platform for small businesses with monthly subscription"
        )

        assert result.is_usable
        assert result.data.classified_type in [
            BusinessModelType.SAAS_B2B_SMB,
            BusinessModelType.SAAS_B2B_MIDMARKET,
        ]

    def test_classify_ecommerce_marketplace(self):
        """Test classification of e-commerce marketplace."""
        from startupai.tools.business_model_classifier import BusinessModelClassifier

        classifier = BusinessModelClassifier()
        result = classifier.classify(
            business_description="Two-sided marketplace connecting buyers and sellers with commission on GMV"
        )

        assert result.is_usable
        assert result.data.classified_type == BusinessModelType.ECOMMERCE_MARKETPLACE

    def test_classify_fintech_b2c(self):
        """Test classification of fintech B2C."""
        from startupai.tools.business_model_classifier import BusinessModelClassifier

        classifier = BusinessModelClassifier()
        result = classifier.classify(
            business_description="Consumer fintech app for personal payments and lending"
        )

        assert result.is_usable
        assert result.data.classified_type == BusinessModelType.FINTECH_B2C

    def test_classify_with_explicit_revenue_model(self):
        """Test classification with explicit revenue model."""
        from startupai.tools.business_model_classifier import BusinessModelClassifier

        classifier = BusinessModelClassifier()
        result = classifier.classify(
            business_description="Software tool",
            revenue_model="Monthly subscription per seat",
            target_customers="Enterprise companies",
        )

        assert result.is_usable
        assert result.data.classified_type == BusinessModelType.SAAS_B2B_ENTERPRISE


class TestUnitEconomicsModels:
    """Tests for UnitEconomicsModel hierarchy."""

    def test_saas_b2b_smb_cac_calculation(self):
        """Test CAC calculation for SaaS B2B SMB."""
        from startupai.tools.unit_economics_models import (
            SaaSB2BSMBModel, UnitEconomicsInput
        )

        model = SaaSB2BSMBModel()
        inputs = UnitEconomicsInput(
            marketing_spend_usd=10000,
            new_customers=100,
        )

        cac, breakdown = model.calculate_cac(inputs)

        assert cac > 0
        assert 'marketing' in breakdown
        assert 'sales' in breakdown

    def test_saas_b2b_smb_ltv_calculation(self):
        """Test LTV calculation for SaaS B2B SMB."""
        from startupai.tools.unit_economics_models import (
            SaaSB2BSMBModel, UnitEconomicsInput
        )

        model = SaaSB2BSMBModel()
        inputs = UnitEconomicsInput(
            monthly_recurring_revenue=100,
            monthly_churn_pct=5.0,
            cost_of_goods_sold_pct=30,
        )

        ltv, breakdown = model.calculate_ltv(inputs)

        assert ltv > 0
        assert 'monthly_contribution' in breakdown
        assert 'lifespan_months' in breakdown

    def test_calculate_metrics_success(self):
        """Test full metrics calculation."""
        from startupai.tools.unit_economics_models import (
            SaaSB2BSMBModel, UnitEconomicsInput
        )

        model = SaaSB2BSMBModel()
        inputs = UnitEconomicsInput(
            marketing_spend_usd=10000,
            new_customers=100,
            monthly_recurring_revenue=100,
            monthly_churn_pct=5.0,
            cost_of_goods_sold_pct=30,
        )

        result = model.calculate_metrics(inputs)

        assert result.is_usable
        assert result.data.cac_usd > 0
        assert result.data.ltv_usd > 0
        assert result.data.ltv_cac_ratio > 0
        assert result.data.business_model_type == BusinessModelType.SAAS_B2B_SMB

    def test_viability_assessment_profitable(self):
        """Test viability assessment for profitable metrics."""
        from startupai.tools.unit_economics_models import SaaSB2BSMBModel

        model = SaaSB2BSMBModel()
        metrics = ViabilityMetrics(
            cac_usd=100,
            ltv_usd=500,
            ltv_cac_ratio=5.0,
            gross_margin_pct=70,
        )

        signal = model.assess_viability(metrics)
        assert signal == 'profitable'

    def test_viability_assessment_underwater(self):
        """Test viability assessment for underwater metrics."""
        from startupai.tools.unit_economics_models import SaaSB2BSMBModel

        model = SaaSB2BSMBModel()
        metrics = ViabilityMetrics(
            cac_usd=500,
            ltv_usd=100,
            ltv_cac_ratio=0.2,
            gross_margin_pct=70,
        )

        signal = model.assess_viability(metrics)
        assert signal == 'underwater'

    def test_model_registry_contains_all_types(self):
        """Test that model registry has all business model types."""
        from startupai.tools.unit_economics_models import MODEL_REGISTRY

        # Check all key model types are registered
        assert BusinessModelType.SAAS_B2B_SMB in MODEL_REGISTRY
        assert BusinessModelType.SAAS_B2B_ENTERPRISE in MODEL_REGISTRY
        assert BusinessModelType.ECOMMERCE_DTC in MODEL_REGISTRY
        assert BusinessModelType.ECOMMERCE_MARKETPLACE in MODEL_REGISTRY
        assert BusinessModelType.FINTECH_B2B in MODEL_REGISTRY
        assert BusinessModelType.CONSULTING in MODEL_REGISTRY

    def test_get_model_for_type(self):
        """Test factory function returns correct model."""
        from startupai.tools.unit_economics_models import (
            get_model_for_type, EcommerceMarketplaceModel
        )

        model = get_model_for_type(BusinessModelType.ECOMMERCE_MARKETPLACE)
        assert isinstance(model, EcommerceMarketplaceModel)


# ==============================================================================
# INTEGRATION TESTS
# ==============================================================================

class TestAreaIntegration:
    """Integration tests across Area improvements."""

    def test_state_fields_exist(self):
        """Test that new state fields are present."""
        state = StartupValidationState(
            project_id="test_001",
            entrepreneur_input="Test",
        )

        # Area 3 fields
        assert hasattr(state, 'current_policy_version')
        assert hasattr(state, 'experiment_config_source')
        assert hasattr(state, 'policy_selection_reason')

        # Area 6 fields
        assert hasattr(state, 'daily_spend_usd')
        assert hasattr(state, 'campaign_spend_usd')
        assert hasattr(state, 'budget_status')
        assert hasattr(state, 'budget_escalation_triggered')
        assert hasattr(state, 'budget_kill_triggered')

        # Area 7 fields
        assert hasattr(state, 'business_model_type')
        assert hasattr(state, 'business_model_inferred_from')

    def test_viability_metrics_extended(self):
        """Test that ViabilityMetrics has new breakdown fields."""
        metrics = ViabilityMetrics(
            cac_usd=100,
            ltv_usd=300,
            cac_breakdown={'marketing': 80, 'sales': 20},
            ltv_breakdown={'monthly_contribution': 50, 'lifespan_months': 6},
            business_model_type=BusinessModelType.SAAS_B2B_SMB,
        )

        assert metrics.cac_breakdown == {'marketing': 80, 'sales': 20}
        assert metrics.business_model_type == BusinessModelType.SAAS_B2B_SMB
