from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.language_models.fake_chat_models import FakeListChatModel
import os

# Use real Claude if API key exists, otherwise use mock
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

if ANTHROPIC_API_KEY and ANTHROPIC_API_KEY != "skip_for_now":
    llm = ChatAnthropic(
        model="claude-sonnet-4-6",
        temperature=0,
        api_key=ANTHROPIC_API_KEY
    )
else:
    # Mock LLM for dev — returns a realistic fake summary
    llm = FakeListChatModel(responses=[
        "This transaction has been flagged as high risk due to an unusually large transfer amount "
        "combined with activity from an unrecognized device and location. The use of a high-risk "
        "merchant category further elevates suspicion — immediate review is recommended."
    ])

prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are a senior fraud analyst assistant. Given a transaction's details, risk score, "
     "risk level, and detected fraud signals, write a concise 2-3 sentence investigation summary "
     "that a human analyst can act on immediately. Be specific about which signals are most "
     "concerning and why. Explain signals in plain English, not as raw variable names. "
     "Always end with a recommended action."),
    ("human",
     "Transaction Details:\n"
     "- Amount: {amount}\n"
     "- Merchant: {merchant}\n"
     "- Merchant Category: {merchant_category}\n"
     "- Location: {location}\n"
     "- Transaction Type: {transaction_type}\n"
     "- Risk Score: {score} / 150\n"
     "- Risk Level: {risk_level}\n"
     "- Fraud Signals Detected: {signals}\n\n"
     "Write the fraud investigation summary.")
])

chain = prompt | llm | StrOutputParser()

async def generate_fraud_summary(
    transaction_data: dict,
    score: int,
    risk_level: str,
    signals: list
) -> str:
    # Only generate summary for HIGH and CRITICAL transactions
    if risk_level not in ["HIGH", "CRITICAL"]:
        return None

    try:
        result = await chain.ainvoke({
            "amount": transaction_data.get("amount"),
            "merchant": transaction_data.get("merchant") or "Unknown",
            "merchant_category": transaction_data.get("merchant_category") or "Unknown",
            "location": transaction_data.get("location") or "Unknown",
            "transaction_type": transaction_data.get("transaction_type"),
            "score": score,
            "risk_level": risk_level,
            "signals": ", ".join(signals) if signals else "none"
        })
        return result
    except Exception as e:
        # Never let LLM failure break the core fraud scoring
        return f"Summary generation failed: {str(e)}"