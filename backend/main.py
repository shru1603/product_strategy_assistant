import asyncio
import json
import uuid
from pathlib import Path

from fastapi.staticfiles import StaticFiles

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from config import API_KEY, BASE_URL, CHAT_MODEL, DATA_DIR, REPORTS_DIR, get_http_client
from chroma_store import get_session_collection
from graph import graph

app = FastAPI(title="Product Strategy Assistant API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Path(DATA_DIR).mkdir(exist_ok=True)
Path(REPORTS_DIR).mkdir(exist_ok=True)

sessions: dict = {}

NODE_LABELS = {
    "ingest":             "Ingesting and indexing data",
    "customer_feedback":  "Analyzing customer feedback",
    "sales_performance":  "Computing sales performance",
    "market_opportunity": "Identifying market opportunities",
    "feature_priority":   "Prioritizing features with RICE",
    "strategy_node":      "Generating strategy and SWOT",
    "report":             "Generating PDF report",
}


class ChatRequest(BaseModel):
    session_id: str
    question: str


@app.get("/")
def root():
    return {"status": "ok", "message": "Product Strategy Assistant API is running"}


@app.get("/api/load-existing")
def load_existing():
    """Return all CSV/PDF/TXT files already present in the data folder."""
    data_dir = Path(DATA_DIR)
    files = [f.name for f in data_dir.iterdir() if f.suffix.lower() in {".csv", ".pdf", ".txt"}]
    return {"files": files}


@app.post("/api/load-existing")
def create_session_from_existing(filenames: list[str]):
    """Create a session from files already in the data folder — no upload needed."""
    data_dir = Path(DATA_DIR)
    paths = []
    missing = []
    for name in filenames:
        p = data_dir / name
        if p.exists():
            paths.append(str(p))
        else:
            missing.append(name)
    if missing:
        raise HTTPException(status_code=404, detail=f"Files not found in data/: {missing}")
    session_id = str(uuid.uuid4())[:8]
    sessions[session_id] = {"uploaded_files": paths, "status": "uploaded", "result": {}}
    return {"session_id": session_id, "files": [Path(p).name for p in paths]}


@app.post("/api/upload")
async def upload_files(files: list[UploadFile] = File(...)):
    session_id = str(uuid.uuid4())[:8]
    saved_paths = []
    for file in files:
        dest = Path(DATA_DIR) / f"{session_id}_{file.filename}"
        content = await file.read()
        dest.write_bytes(content)
        saved_paths.append(str(dest))
    sessions[session_id] = {
        "uploaded_files": saved_paths,
        "status": "uploaded",
        "result": {},
    }
    return {"session_id": session_id, "files": [Path(p).name for p in saved_paths]}


@app.get("/api/analyze/{session_id}")
async def analyze(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found. Upload files first.")

    uploaded_files = sessions[session_id]["uploaded_files"]

    initial_state = {
        "messages":            [HumanMessage(content="Analyze uploaded product data and generate insights.")],
        "session_id":          session_id,
        "uploaded_files":      uploaded_files,
        "raw_data_summary":    {},
        "customer_insights":   {},
        "sales_analysis":      {},
        "market_opportunities":{},
        "feature_priorities":  {},
        "strategy":            {},
        "report_status":       {},
    }

    async def event_stream():
        accumulated: dict = {}

        for event in graph.stream(initial_state, config={"recursion_limit": 30}, stream_mode="updates"):
            for node_name, update in event.items():
                for k, v in update.items():
                    if k == "messages":
                        accumulated[k] = accumulated.get(k, []) + (v if isinstance(v, list) else [v])
                    else:
                        accumulated[k] = v

                label = NODE_LABELS.get(node_name, node_name)
                payload = json.dumps({"node": node_name, "label": label, "status": "completed"})
                yield f"data: {payload}\n\n"
                await asyncio.sleep(0)

        clean_result = {}
        for k, v in accumulated.items():
            if k == "messages":
                continue
            try:
                json.dumps(v)
                clean_result[k] = v
            except Exception:
                clean_result[k] = str(v)

        sessions[session_id]["result"] = clean_result
        sessions[session_id]["status"] = "completed"

        final = json.dumps({"node": "done", "label": "Analysis complete", "status": "done", "result": clean_result})
        yield f"data: {final}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.get("/api/results/{session_id}")
def get_results(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    return sessions[session_id].get("result", {})


@app.post("/api/chat")
def chat(req: ChatRequest):
    session_col = get_session_collection()
    llm = ChatOpenAI(
        model=CHAT_MODEL,
        api_key=API_KEY,
        base_url=BASE_URL,
        http_client=get_http_client(),
        temperature=0.3,
    )

    context = ""
    try:
        results = session_col.query(
            query_texts=[req.question],
            n_results=5,
            where={"session_id": req.session_id},
        )
        if results and results["documents"] and results["documents"][0]:
            context = "\n\n".join(results["documents"][0])
    except Exception:
        pass

    response = llm.invoke([
        SystemMessage(content=f"""You are a Product Strategy Assistant answering questions about analyzed product data.
Use the analysis context below to answer. Cite specific product names, numbers, and regions when available.
If the data does not cover the question, say so clearly.

Analysis Context:
{context or 'No analysis context available for this session.'}"""),
        HumanMessage(content=req.question),
    ])

    return {"answer": response.content}


@app.get("/api/report/{session_id}")
def download_report(session_id: str):
    report_path = Path(REPORTS_DIR) / f"product_strategy_{session_id}.pdf"
    if not report_path.exists():
        raise HTTPException(status_code=404, detail="Report not found. Run /api/analyze first.")
    return FileResponse(
        str(report_path),
        media_type="application/pdf",
        filename=f"strategy_report_{session_id}.pdf",
    )


@app.get("/api/sessions/{session_id}/status")
def session_status(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"session_id": session_id, "status": sessions[session_id].get("status", "unknown")}


# Serve React frontend — must be last so API routes take priority
_frontend_dist = Path(__file__).parent.parent / "frontend" / "dist"
if _frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(_frontend_dist), html=True), name="static")
