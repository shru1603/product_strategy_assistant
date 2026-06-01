import httpx

API_KEY = "learner055"
BASE_URL = "https://keygateway.arshnivlabs.com/v1"
CHAT_MODEL = "gpt-4o-mini"
EMBED_MODEL = "text-embedding-3-small"
CHROMA_PATH = "./chroma_db"
REPORTS_DIR = "./reports"
DATA_DIR = "./data"


def get_http_client():
    return httpx.Client(verify=False)
