from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, AIMessage
from chroma_store import get_product_collection, get_session_collection, query_collection
from config import API_KEY, BASE_URL, CHAT_MODEL, get_http_client


def _get_doc(col, doc_id: str, max_chars: int = 700) -> str:
    try:
        r = col.get(ids=[doc_id])
        return r["documents"][0][:max_chars] if r["documents"] else ""
    except Exception:
        return ""


def strategy_agent(state: dict) -> dict:
    llm = ChatOpenAI(
        model=CHAT_MODEL,
        api_key=API_KEY,
        base_url=BASE_URL,
        http_client=get_http_client(),
        temperature=0.4,
    )

    session_id = state.get("session_id", "default")
    product_col = get_product_collection()
    session_col = get_session_collection()
    raw = state.get("raw_data_summary", {})

    customer_ctx  = _get_doc(session_col, f"{session_id}_customer")
    sales_ctx     = _get_doc(session_col, f"{session_id}_sales")
    market_ctx    = _get_doc(session_col, f"{session_id}_market")
    features_ctx  = _get_doc(session_col, f"{session_id}_features")

    product_ctx = query_collection(
        product_col,
        "best products high revenue high rating strategic opportunities growth",
        n_results=5,
    )

    system_prompt = f"""You are the Strategy Recommendation Agent for an AI Product Strategy Assistant.
Synthesize all agent analyses into a comprehensive product strategy document.

Company Overview:
- Products: {len(raw.get('products', []))} products across {len(raw.get('categories', []))} categories
- Total Revenue: ${raw.get('total_revenue', 0):,.2f}
- Total Profit: ${raw.get('total_profit', 0):,.2f} ({raw.get('total_profit', 0)/max(raw.get('total_revenue', 1), 1)*100:.1f}% margin)
- Average Rating: {raw.get('avg_rating', 0):.2f}/5.0
- Total Returns: {raw.get('total_returns', 0)} ({raw.get('total_returns', 0)/max(raw.get('total_units', 1), 1)*100:.2f}% return rate)
- New Customers: {raw.get('total_new_customers', 0):,}
- Regions: {', '.join(raw.get('regions', []))}
- Period: {raw.get('date_range', 'N/A')}

--- Customer Feedback Agent ---
{customer_ctx}

--- Sales Performance Agent ---
{sales_ctx}

--- Market Opportunity Agent ---
{market_ctx}

--- Feature Priority Agent ---
{features_ctx}

--- Product ChromaDB Context ---
{product_ctx}

Generate the full strategy document:

## SWOT Analysis
**Strengths:** (4 specific data-backed points — cite product names/numbers)
**Weaknesses:** (4 specific data-backed points — cite product names/numbers)
**Opportunities:** (4 specific data-backed points — cite regions/categories)
**Threats:** (4 specific data-backed points)

## Top 5 Strategic Recommendations
For each: What to do | Why (data evidence) | Expected Impact

## 90-Day Action Plan
**Week 1-2:** [specific actions with owners/targets]
**Week 3-4:** [specific actions]
**Month 2:** [specific actions]
**Month 3:** [specific actions]

## 5 KPIs to Track
For each: KPI name | Current baseline | 90-day target | How to measure"""

    response = llm.invoke([SystemMessage(content=system_prompt)])

    strategy = {"analysis": response.content}

    session_col.upsert(
        documents=[f"Strategic Recommendations:\n{response.content}"],
        ids=[f"{session_id}_strategy"],
        metadatas=[{"agent": "strategy", "session_id": session_id}],
    )

    return {
        "messages": [AIMessage(content="Strategy and SWOT analysis complete.")],
        "strategy": strategy,
    }
