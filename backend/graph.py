from langgraph.graph import StateGraph, START, END
from state import ProductStrategyState
from nodes.ingest_node import ingest_node
from agents.customer_agent import customer_agent
from agents.sales_agent import sales_agent
from agents.market_agent import market_agent
from agents.feature_agent import feature_agent
from agents.strategy_agent import strategy_agent
from agents.report_agent import report_agent


def create_graph():
    builder = StateGraph(ProductStrategyState)

    builder.add_node("ingest",            ingest_node)
    builder.add_node("customer_feedback", customer_agent)
    builder.add_node("sales_performance", sales_agent)
    builder.add_node("market_opportunity",market_agent)
    builder.add_node("feature_priority",  feature_agent)
    builder.add_node("strategy_node",     strategy_agent)
    builder.add_node("report",            report_agent)

    builder.add_edge(START,             "ingest")
    builder.add_edge("ingest",          "customer_feedback")
    builder.add_edge("customer_feedback","sales_performance")
    builder.add_edge("sales_performance","market_opportunity")
    builder.add_edge("market_opportunity","feature_priority")
    builder.add_edge("feature_priority", "strategy_node")
    builder.add_edge("strategy_node",    "report")
    builder.add_edge("report",           END)

    return builder.compile()


graph = create_graph()
