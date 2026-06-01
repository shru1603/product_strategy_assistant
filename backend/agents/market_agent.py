import pandas as pd
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, AIMessage
from chroma_store import get_product_collection, get_session_collection, query_collection
from config import API_KEY, BASE_URL, CHAT_MODEL, get_http_client


def market_agent(state: dict) -> dict:
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
    uploaded_files = state.get("uploaded_files", [])

    chroma_context = query_collection(
        product_col,
        "growth opportunity new customers region expansion underperforming",
        n_results=8,
    )

    opportunity_text = "No CSV data found."

    for file_path in uploaded_files:
        if not file_path.endswith(".csv"):
            continue

        df = pd.read_csv(file_path)
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df["Month"] = df["Date"].dt.to_period("M").astype(str)

        nc_by_product = df.groupby("Product_Name")["New_Customers"].sum().sort_values(ascending=False)
        nc_by_region = df.groupby("Region")["New_Customers"].sum().sort_values(ascending=False)
        nc_by_month = df.groupby("Month")["New_Customers"].sum().sort_index()

        product_summary = df.groupby("Product_Name").agg(
            Revenue=("Revenue_USD", "sum"),
            Rating=("Customer_Rating", "mean"),
            New_Customers=("New_Customers", "sum"),
            Units=("Units_Sold", "sum"),
            Returns=("Returns", "sum"),
        ).round(2)
        product_summary["Return_Rate_Pct"] = (
            product_summary["Returns"] / product_summary["Units"].replace(0, 1) * 100
        ).round(2)

        category_summary = df.groupby("Category").agg(
            Revenue=("Revenue_USD", "sum"),
            New_Customers=("New_Customers", "sum"),
            Rating=("Customer_Rating", "mean"),
        ).round(2)

        opportunity_text = f"""New Customers by Product:
{nc_by_product.to_string()}

New Customers by Region:
{nc_by_region.to_string()}

Monthly New Customer Trend:
{nc_by_month.to_string()}

Full Product Summary (Revenue, Rating, New_Customers, Units, Return_Rate_Pct):
{product_summary.to_string()}

Category Summary (Revenue, New_Customers, Rating):
{category_summary.to_string()}"""
        break

    system_prompt = f"""You are the Market Opportunity Agent for an AI Product Strategy Assistant.
Identify growth opportunities, underperformers, and expansion areas.

Computed Market Data:
{opportunity_text}

ChromaDB Context:
{chroma_context}

Provide a structured analysis:
1. Top 2 growth-opportunity products — high rating AND growing new customer base with evidence
2. Underperforming products with recovery potential — decent rating but low revenue/customers
3. Best region for expansion — highest new customer acquisition rate with numbers
4. Category with the biggest untapped potential and why
5. New customer acquisition trend — is it growing or slowing month over month?
6. Products with worrying return rates that need immediate attention (flag > 3%)
7. 3 specific market expansion recommendations with target regions and expected impact

Use exact product names, regions, and numbers throughout."""

    response = llm.invoke([SystemMessage(content=system_prompt)])

    opportunities = {"analysis": response.content}

    session_col.upsert(
        documents=[f"Market Opportunity Analysis:\n{response.content}"],
        ids=[f"{session_id}_market"],
        metadatas=[{"agent": "market_opportunity", "session_id": session_id}],
    )

    return {
        "messages": [AIMessage(content="Market opportunity analysis complete.")],
        "market_opportunities": opportunities,
    }
