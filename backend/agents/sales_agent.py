import pandas as pd
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, AIMessage
from chroma_store import get_session_collection
from config import API_KEY, BASE_URL, CHAT_MODEL, get_http_client


def sales_agent(state: dict) -> dict:
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

    charts_data = {}
    analysis_text = "No CSV data found."

    for file_path in uploaded_files:
        if not file_path.endswith(".csv"):
            continue

        df = pd.read_csv(file_path)
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df["Month"] = df["Date"].dt.to_period("M").astype(str)
        df["Profit_Margin_Pct"] = (
            df["Profit_USD"] / df["Revenue_USD"].replace(0, 1) * 100
        ).round(2)
        df["Marketing_ROI"] = (
            df["Revenue_USD"] / df["Marketing_Spend_USD"].replace(0, 1)
        ).round(2)

        rev_by_product = df.groupby("Product_Name")["Revenue_USD"].sum().sort_values(ascending=False)
        profit_by_product = df.groupby("Product_Name")["Profit_USD"].sum().sort_values(ascending=False)
        margin_by_product = df.groupby("Product_Name")["Profit_Margin_Pct"].mean().sort_values(ascending=False)
        monthly_rev = df.groupby("Month")["Revenue_USD"].sum().sort_index()
        roi_by_product = df.groupby("Product_Name")["Marketing_ROI"].mean().sort_values(ascending=False)
        region_rev = df.groupby("Region")["Revenue_USD"].sum().sort_values(ascending=False)
        category_rev = df.groupby("Category")["Revenue_USD"].sum().sort_values(ascending=False)

        total_rev = rev_by_product.sum()
        rev_pct = (rev_by_product / total_rev * 100).round(1)

        charts_data = {
            "revenue_by_product": {k: round(float(v), 2) for k, v in rev_by_product.items()},
            "profit_by_product": {k: round(float(v), 2) for k, v in profit_by_product.items()},
            "margin_by_product": {k: round(float(v), 2) for k, v in margin_by_product.items()},
            "monthly_revenue": {k: round(float(v), 2) for k, v in monthly_rev.items()},
            "roi_by_product": {k: round(float(v), 2) for k, v in roi_by_product.items()},
            "region_revenue": {k: round(float(v), 2) for k, v in region_rev.items()},
            "category_revenue": {k: round(float(v), 2) for k, v in category_rev.items()},
        }

        analysis_text = f"""Revenue by Product (with % of total):
{chr(10).join(f"  {p}: ${v:,.0f} ({rev_pct[p]:.1f}%)" for p, v in rev_by_product.items())}

Profit Margin (%) by Product:
{margin_by_product.to_string()}

Monthly Revenue Trend:
{monthly_rev.to_string()}

Marketing ROI by Product (Revenue per $1 spent):
{roi_by_product.to_string()}

Revenue by Region:
{region_rev.to_string()}

Revenue by Category:
{category_rev.to_string()}"""
        break

    system_prompt = f"""You are the Sales Performance Agent for an AI Product Strategy Assistant.
Analyze the sales data and provide strategic insights.

Computed Sales Data:
{analysis_text}

Provide a structured analysis:
1. Top 3 revenue-generating products — include % of total revenue each
2. Best and worst profit margin products — flag any below 40%
3. Monthly revenue trend — growing, declining, or flat? Calculate MoM growth if possible
4. Best-performing region and why (revenue + context)
5. Best vs worst marketing ROI — is spend aligned with performance?
6. Category performance summary
7. 3 specific sales strategy recommendations with expected impact

Use exact numbers from the data."""

    response = llm.invoke([SystemMessage(content=system_prompt)])

    sales_data = {"analysis": response.content, "charts_data": charts_data}

    session_col.upsert(
        documents=[f"Sales Performance Analysis:\n{response.content}"],
        ids=[f"{session_id}_sales"],
        metadatas=[{"agent": "sales_performance", "session_id": session_id}],
    )

    return {
        "messages": [AIMessage(content="Sales performance analysis complete.")],
        "sales_analysis": sales_data,
    }
