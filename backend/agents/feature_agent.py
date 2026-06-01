import pandas as pd
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, AIMessage
from chroma_store import get_session_collection
from config import API_KEY, BASE_URL, CHAT_MODEL, get_http_client


def _get_doc(col, doc_id: str) -> str:
    try:
        r = col.get(ids=[doc_id])
        return r["documents"][0][:600] if r["documents"] else ""
    except Exception:
        return ""


def feature_agent(state: dict) -> dict:
    llm = ChatOpenAI(
        model=CHAT_MODEL,
        api_key=API_KEY,
        base_url=BASE_URL,
        http_client=get_http_client(),
        temperature=0.3,
    )

    session_id = state.get("session_id", "default")
    session_col = get_session_collection()
    uploaded_files = state.get("uploaded_files", [])

    rice_text = "No data."
    rice_dict = []

    for file_path in uploaded_files:
        if not file_path.endswith(".csv"):
            continue

        df = pd.read_csv(file_path)
        agg = df.groupby("Product_Name").agg(
            Revenue=("Revenue_USD", "sum"),
            Rating=("Customer_Rating", "mean"),
            Returns=("Returns", "sum"),
            New_Customers=("New_Customers", "sum"),
            Units=("Units_Sold", "sum"),
            Marketing=("Marketing_Spend_USD", "sum"),
        ).round(2)

        max_nc = agg["New_Customers"].max() or 1
        max_rev = agg["Revenue"].max() or 1

        agg["Reach"] = (agg["New_Customers"] / max_nc * 10).round(1)
        agg["Impact"] = (agg["Rating"] / 5 * agg["Revenue"] / max_rev * 10).round(1)
        agg["Confidence"] = (
            (1 - agg["Returns"] / agg["Units"].replace(0, 1)) * 10
        ).clip(0, 10).round(1)
        agg["Effort"] = 5.0
        agg["RICE_Score"] = (
            agg["Reach"] * agg["Impact"] * agg["Confidence"] / agg["Effort"]
        ).round(2)

        scored = agg[["Reach", "Impact", "Confidence", "Effort", "RICE_Score"]].sort_values(
            "RICE_Score", ascending=False
        )
        rice_text = scored.to_string()
        rice_dict = scored.reset_index().rename(columns={"Product_Name": "product"}).to_dict(orient="records")
        break

    customer_ctx = _get_doc(session_col, f"{session_id}_customer")
    market_ctx = _get_doc(session_col, f"{session_id}_market")

    system_prompt = f"""You are the Feature Prioritization Agent for an AI Product Strategy Assistant.
Use RICE scoring and business context to prioritize product improvements.

RICE Scores (sorted highest to lowest priority):
{rice_text}

Customer Feedback Context:
{customer_ctx}

Market Opportunity Context:
{market_ctx}

Provide a structured analysis:
1. Top 5 priority products ranked by RICE score — 1 line justification each
2. Quick wins (high RICE, issues easy to fix) — 2-3 specific actionable improvements
3. Strategic bets (lower RICE now but high long-term potential) — 1-2 products with rationale
4. Products to deprioritize and why
5. Specific feature/quality improvements for the top 3 products
6. Implementation timeline:
   - 30-day actions (quick wins — low effort, high impact)
   - 60-day actions (medium effort improvements)
   - 90-day actions (strategic investments)

Reference RICE scores and product names throughout."""

    response = llm.invoke([SystemMessage(content=system_prompt)])

    priorities = {"analysis": response.content, "rice_table": rice_dict}

    session_col.upsert(
        documents=[f"Feature Prioritization Analysis:\n{response.content}"],
        ids=[f"{session_id}_features"],
        metadatas=[{"agent": "feature_priority", "session_id": session_id}],
    )

    return {
        "messages": [AIMessage(content="Feature prioritization complete.")],
        "feature_priorities": priorities,
    }
