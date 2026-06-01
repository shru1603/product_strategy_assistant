from typing import Annotated, Dict, List, TypedDict
from langgraph.graph.message import add_messages


class ProductStrategyState(TypedDict):
    messages: Annotated[list, add_messages]
    session_id: str
    uploaded_files: List[str]
    raw_data_summary: Dict
    customer_insights: Dict
    sales_analysis: Dict
    market_opportunities: Dict
    feature_priorities: Dict
    strategy: Dict
    report_status: Dict
