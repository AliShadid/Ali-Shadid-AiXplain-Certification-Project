import os
import io
import hashlib
import tempfile
from uuid import uuid4

import streamlit as st
import pandas as pd
import PyPDF2


# CONFIG
TEAM_API_KEY="#"
os.environ["TEAM_API_KEY"] = TEAM_API_KEY

from aixplain.factories import AgentFactory, IndexFactory
from aixplain.modules.model.record import Record


AGENT_ID = "68baf18ddef19d770c25f3f3"
INDEX_ID = "68baf93ad4e0b5e6e1fb7182"

# INIT AIXPLAIN OBJECTS
@st.cache_resource(show_spinner=False)
def _get_agent_and_index():
    agent = AgentFactory.get(AGENT_ID)
    index = IndexFactory.get(INDEX_ID)
    return agent, index


agent, knowledge_index = _get_agent_and_index()

if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_id" not in st.session_state:
    st.session_state.session_id = None

# HELPERS FUNCTIONS
def human_filetype(uploaded_file):
    name = uploaded_file.name.lower()
    if name.endswith(".pdf"):
        return "pdf"
    if name.endswith(".csv"):
        return "csv"
    if name.endswith(".xlsx") or name.endswith(".xls"):
        return "xlsx"
    return None

def process_uploaded_file(uploaded_file, file_type):
    """
    Extract text content from PDF / CSV / XLSX in-memory.
    Returns a tuple (text_content, meta_bytes) where meta_bytes are used for hashing doc_id.
    """
    file_type = file_type.lower()
    raw_bytes = uploaded_file.read()
    uploaded_file.seek(0)

    if file_type == "pdf":
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(raw_bytes))
        pages = []
        for p in pdf_reader.pages:
            text = p.extract_text() or ""
            pages.append(text)
        text_content = "\n".join(pages)

    elif file_type == "csv":
        df = pd.read_csv(io.BytesIO(raw_bytes))
        text_content = df.to_csv(index=False)

    elif file_type == "xlsx":
        df = pd.read_excel(io.BytesIO(raw_bytes))
        text_content = df.to_csv(index=False)

    else:
        raise ValueError(f"Unsupported file_type: {file_type}")

    return text_content, raw_bytes

def chunk_text(text, chunk_size=200, chunk_overlap=50):
    chunks = []
    step = max(1, chunk_size - chunk_overlap)
    for i in range(0, len(text), step):
        chunk = text[i:i+chunk_size]
        if chunk.strip():
            chunks.append(chunk)
    return chunks

def make_doc_id(filename: str, raw_bytes: bytes):
    h = hashlib.md5(raw_bytes).hexdigest()[:12]
    return f"{os.path.basename(filename)}:{h}"

def batched(iterable, n=200):
    for i in range(0, len(iterable), n):
        yield iterable[i:i+n]

def index_uploaded_file(uploaded_file, file_type, chunk_size=200, chunk_overlap=50, extra_meta=None):
    """
    Index a single UploadedFile into the shared index with metadata.
    Deterministic record IDs (doc_id:chunk_index) allow updates on re-upload.
    """
    content, raw_bytes = process_uploaded_file(uploaded_file, file_type)
    chunks = chunk_text(content, chunk_size, chunk_overlap)

    filename = uploaded_file.name
    doc_id = make_doc_id(filename, raw_bytes)

    base_meta = {
        "doc_id": doc_id,
        "file_name": filename,
        "total_chunks": len(chunks),
    }
    if extra_meta:
        base_meta.update(extra_meta)

    records = [
        Record(
            id=f"{doc_id}:{i}",
            value=chunk,
            attributes={**base_meta, "chunk_index": i},
        )
        for i, chunk in enumerate(chunks)
    ]

    for batch in batched(records, n=200):
        knowledge_index.upsert(batch)

    return doc_id, len(records)


def run_agent(prompt: str):
    """
    Call your deployed agent. Store session_id and return the agent response.
    """
    try:
        resp = agent.run(prompt, session_id=st.session_state.get("session_id"))

        # Try to extract and store the session_id
        if hasattr(resp.data, "session_id"):
            st.session_state["session_id"] = resp.data.session_id

        if isinstance(resp, str):
            return resp

        for key in ("data", "output", "text", "result"):
            if isinstance(resp, dict) and key in resp:
                return resp[key]

        print(resp.data.intermediate_steps)
        print("-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")
        return str(resp.data.output)
    except Exception as e:
        return f"⚠️ Agent error: {e}"


# UI
st.set_page_config(page_title="RAG Chatbot", page_icon="💬", layout="wide")
st.title("💬 RAG Chatbot (aiXplain Index + Agent)")
st.caption(f"Agent `{AGENT_ID}` — Index `{INDEX_ID}`")

with st.sidebar:
    st.header("📄 Upload & Index")
    st.write("Upload **PDF / CSV / XLSX**. Files will be chunked & upserted into your index.")
    uploads = st.file_uploader(
        "Choose files",
        type=["pdf", "csv", "xlsx", "xls"],
        accept_multiple_files=True
    )
    chunk_size = st.slider("Chunk size (chars)", 500, 3000, 200, step=100)
    chunk_overlap = st.slider("Chunk overlap (chars)", 0, 500, 200, step=50)
    extra_meta_note = st.text_input("Optional tag (e.g., project name)", value="")

    if st.button("Index files", type="primary") and uploads:
        for up in uploads:
            ftype = human_filetype(up)
            if not ftype:
                st.error(f"Unsupported file type: {up.name}")
                continue

            with st.status(f"Indexing `{up.name}`...", expanded=False) as status:
                try:
                    extra_meta = {"tag": extra_meta_note} if extra_meta_note else None
                    doc_id, n = index_uploaded_file(
                        up, ftype,
                        chunk_size=chunk_size,
                        chunk_overlap=chunk_overlap,
                        extra_meta=extra_meta
                    )
                    status.update(
                        label=f"Indexed `{up.name}` → {n} chunks",
                        state="complete"
                    )
                    st.success(f"✅ `{up.name}` indexed (doc_id={doc_id}, chunks={n})")
                except Exception as e:
                    status.update(
                        label=f"Failed to index `{up.name}`",
                        state="error"
                    )
                    st.error(f"❌ Error: {e}")

st.divider()

# CHAT
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Ask anything about your uploaded files...")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            answer = run_agent(user_input)
            st.markdown(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})