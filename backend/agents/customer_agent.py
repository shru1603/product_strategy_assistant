from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, AIMessage
from chroma_store import get_product_collection, get_session_collection, query_collection
from config import API_KEY, BASE_URL, CHAT_MODEL, get_http_client


def customer_agent(state: dict) -> dict:
    llm = ChatOpenAI(
        model=CHAT_MODEL,
        api_key=API_KEY,
        base_url=BASE_URL,
        http_client=get_http_client(),
        temperature=0.3,
    )

    session_id = state.get("session_id", "default")
    product_col = get_product_collection()
    session_col = get_session_collection()
    raw = state.get("raw_data_summary", {})

    context = query_collection(
        product_col,
        "customer reviews ratings satisfaction complaints returns quality",
        n_results=10,
    )

    system_prompt = f"""You are the Customer Feedback Agent for an AI Product Strategy Assistant.
Analyze customer reviews, ratings, and return data from the product data.

ChromaDB Product Context:
{context}

Data Summary:
- Total Records: {raw.get('total_records', 0)}
- Average Rating: {raw.get('avg_rating', 0)}/5.0
- Total Returns: {raw.get('total_returns', 0)}
- Total Units Sold: {raw.get('total_units', 0)}
- Return Rate: {raw.get('total_returns', 0) / max(raw.get('total_units', 1), 1) * 100:.2f}%
- Products: {', '.join(raw.get('products', []))}

Provide a structured analysis:
1. Overall sentiment breakdown — estimate positive/neutral/negative percentages
2. Top 3 pain points with specific product names and evidence from reviews
3. Top 3 most praised aspects with specific product names
4. Products with concerning return rates (flag > 3% return rate)
5. Highest vs lowest rated products with exact scores
6. 3 actionable recommendations to improve customer satisfaction

Be specific — use exact product names and numbers from the data."""

    response = llm.invoke([SystemMessage(content=system_prompt)])

    insights = {"analysis": response.content}

    session_col.upsert(
        documents=[f"Customer Feedback Analysis:\n{response.content}"],
        ids=[f"{session_id}_customer"],
        metadatas=[{"agent": "customer_feedback", "session_id": session_id}],
    )

    return {
        "messages": [AIMessage(content="Customer feedback analysis complete.")],
        "customer_insights": insights,
    }
