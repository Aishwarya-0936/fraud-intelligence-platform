import pytest
from app.agents.pattern_detector import check_structuring, check_card_testing, check_money_mule, pattern_detector_node


def test_structuring_detected_with_multiple_threshold_amounts():
    profile = {"recent_transactions": [
        {"amount": 45000}, {"amount": 50000}, {"amount": 60000}
    ]}
    assert check_structuring(profile, 55000) is True


def test_structuring_not_detected_with_normal_amounts():
    profile = {"recent_transactions": [{"amount": 500}, {"amount": 1000}]}
    assert check_structuring(profile, 800) is False


def test_card_testing_detected_with_multiple_small_transactions():
    profile = {"recent_transactions": [
        {"amount": 100}, {"amount": 200}, {"amount": 150}
    ]}
    assert check_card_testing(profile) is True


def test_money_mule_detected_with_deposit_then_transfer():
    transaction = {"transaction_type": "transfer", "destination_account": "acc_x", "amount": 40000}
    profile = {"recent_transactions": [{"transaction_type": "deposit", "amount": 60000}]}
    assert check_money_mule(transaction, profile) is True


@pytest.mark.asyncio
async def test_pattern_detector_node_combines_signals():
    state = {
        "transaction": {"transaction_type": "transfer", "destination_account": "acc_x", "amount": 40000},
        "user_profile": {
            "recent_transactions": [
                {"amount": 45000}, {"amount": 50000},
                {"transaction_type": "deposit", "amount": 60000}
            ]
        }
    }
    result = await pattern_detector_node(state)
    assert result["pattern_score"] >= 0
    assert isinstance(result["pattern_signals"], list)