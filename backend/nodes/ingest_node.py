import pandas as pd
from pathlib import Path
from langchain_core.messages import AIMessage
from chroma_store import get_product_collection


def ingest_node(state: dict) -> dict:
    uploaded_files = state.get("uploaded_files", [])
    collection = get_product_collection()
    summary = {}

    for file_path in uploaded_files:
        if not file_path.endswith(".csv"):
            continue

        df = pd.read_csv(file_path)
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

        summary = {
            "total_records": len(df),
            "products": df["Product_Name"].dropna().unique().tolist(),
            "categories": df["Category"].dropna().unique().tolist(),
            "regions": df["Region"].dropna().unique().tolist(),
            "date_range": f"{df['Date'].min().date()} to {df['Date'].max().date()}",
            "total_revenue": round(float(df["Revenue_USD"].sum()), 2),
            "total_profit": round(float(df["Profit_USD"].sum()), 2),
            "total_cost": round(float(df["Cost_USD"].sum()), 2),
            "avg_rating": round(float(df["Customer_Rating"].mean()), 2),
            "total_units": int(df["Units_Sold"].sum()),
            "total_returns": int(df["Returns"].sum()),
            "total_new_customers": int(df["New_Customers"].sum()),
            "total_marketing_spend": round(float(df["Marketing_Spend_USD"].sum()), 2),
        }

        docs, ids, metas = [], [], []

        # Index by product
        for product in df["Product_Name"].unique():
            pdf = df[df["Product_Name"] == product]
            reviews = " | ".join(pdf["Review"].dropna().tolist()[:15])
            units = pdf["Units_Sold"].sum()
            returns = pdf["Returns"].sum()
            doc = (
                f"Product: {product}\n"
                f"Category: {pdf['Category'].iloc[0]}\n"
                f"Total Revenue: ${pdf['Revenue_USD'].sum():,.2f}\n"
                f"Total Profit: ${pdf['Profit_USD'].sum():,.2f}\n"
                f"Profit Margin: {pdf['Profit_USD'].sum()/max(pdf['Revenue_USD'].sum(),1)*100:.1f}%\n"
                f"Units Sold: {units}\n"
                f"Avg Rating: {pdf['Customer_Rating'].mean():.2f}\n"
                f"Returns: {returns} ({returns/max(units,1)*100:.1f}% return rate)\n"
                f"New Customers: {pdf['New_Customers'].sum()}\n"
                f"Marketing Spend: ${pdf['Marketing_Spend_USD'].sum():,.2f}\n"
                f"Marketing ROI: {pdf['Revenue_USD'].sum()/max(pdf['Marketing_Spend_USD'].sum(),1):.2f}x\n"
                f"Regions: {', '.join(pdf['Region'].unique())}\n"
                f"Reviews: {reviews}"
            )
            docs.append(doc)
            ids.append(f"product_{product.replace(' ', '_')}")
            metas.append({"type": "product", "product": product})

        # Index by region
        for region in df["Region"].unique():
            rdf = df[df["Region"] == region]
            top_product = rdf.groupby("Product_Name")["Revenue_USD"].sum().idxmax()
            doc = (
                f"Region: {region}\n"
                f"Total Revenue: ${rdf['Revenue_USD'].sum():,.2f}\n"
                f"Total Profit: ${rdf['Profit_USD'].sum():,.2f}\n"
                f"Top Product: {top_product}\n"
                f"Avg Rating: {rdf['Customer_Rating'].mean():.2f}\n"
                f"New Customers: {rdf['New_Customers'].sum()}\n"
                f"Products sold: {', '.join(rdf['Product_Name'].unique())}"
            )
            docs.append(doc)
            ids.append(f"region_{region}")
            metas.append({"type": "region", "region": region})

        # Index by category
        for cat in df["Category"].unique():
            cdf = df[df["Category"] == cat]
            doc = (
                f"Category: {cat}\n"
                f"Total Revenue: ${cdf['Revenue_USD'].sum():,.2f}\n"
                f"Avg Rating: {cdf['Customer_Rating'].mean():.2f}\n"
                f"Products: {', '.join(cdf['Product_Name'].unique())}\n"
                f"New Customers: {cdf['New_Customers'].sum()}"
            )
            docs.append(doc)
            ids.append(f"category_{cat.replace(' ', '_')}")
            metas.append({"type": "category", "category": cat})

        collection.upsert(documents=docs, ids=ids, metadatas=metas)

    return {
        "messages": [AIMessage(content=f"Ingested {summary.get('total_records', 0)} records. Indexed {len(docs)} documents into ChromaDB.")],
        "raw_data_summary": summary,
    }
