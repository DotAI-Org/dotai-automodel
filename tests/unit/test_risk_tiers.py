import pytest

from app.stages.s8_inference import _get_risk_tier
from app.models.schemas import RiskTier


class TestGetRiskTier:
    def test_high_at_071(self):
        assert _get_risk_tier(0.71) == RiskTier.high

    def test_medium_at_050(self):
        assert _get_risk_tier(0.50) == RiskTier.medium

    def test_low_at_030(self):
        assert _get_risk_tier(0.30) == RiskTier.low

    def test_boundary_070_is_medium(self):
        # > 0.7 for High, so 0.7 is Medium
        assert _get_risk_tier(0.70) == RiskTier.medium

    def test_boundary_040_is_low(self):
        # > 0.4 for Medium, so 0.4 is Low
        assert _get_risk_tier(0.40) == RiskTier.low

    def test_zero_is_low(self):
        assert _get_risk_tier(0.0) == RiskTier.low

    def test_one_is_high(self):
        assert _get_risk_tier(1.0) == RiskTier.high
