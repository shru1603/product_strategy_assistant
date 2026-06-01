from pathlib import Path
from langchain_core.messages import AIMessage
from utils.pdf_generator import generate_report_pdf
from config import REPORTS_DIR


def report_agent(state: dict) -> dict:
    session_id = state.get("session_id", "default")
    Path(REPORTS_DIR).mkdir(exist_ok=True)

    output_path = str(Path(REPORTS_DIR) / f"product_strategy_{session_id}.pdf")

    report_data = {
        "raw_data_summary":    state.get("raw_data_summary", {}),
        "customer_insights":   state.get("customer_insights", {}),
        "sales_analysis":      state.get("sales_analysis", {}),
        "market_opportunities":state.get("market_opportunities", {}),
        "feature_priorities":  state.get("feature_priorities", {}),
        "strategy":            state.get("strategy", {}),
    }

    message = generate_report_pdf(report_data, output_path)

    status = {
        "status":    "generated" if "generated" in message.lower() else "failed",
        "file_path": output_path,
        "message":   message,
    }

    return {
        "messages":     [AIMessage(content=message)],
        "report_status": status,
    }
