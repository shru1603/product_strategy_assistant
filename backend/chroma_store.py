import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from langchain_openai import OpenAIEmbeddings
from config import API_KEY, BASE_URL, EMBED_MODEL, CHROMA_PATH, get_http_client

embeddings = OpenAIEmbeddings(
    model=EMBED_MODEL,
    api_key=API_KEY,
    base_url=BASE_URL,
    http_client=get_http_client(),
)

_client = chromadb.PersistentClient(path=CHROMA_PATH)

_embedding_fn = OpenAIEmbeddingFunction(
    api_key=API_KEY,
    model_name=EMBED_MODEL,
    api_base=BASE_URL,
)


def get_product_collection():
    return _client.get_or_create_collection("product_data", embedding_function=_embedding_fn)


def get_session_collection():
    return _client.get_or_create_collection("session_memory", embedding_function=_embedding_fn)


def query_collection(collection, query_text: str, n_results: int = 6) -> str:
    results = collection.query(query_texts=[query_text], n_results=n_results)
    if results and results["documents"] and results["documents"][0]:
        return "\n\n".join(results["documents"][0])
    return ""
