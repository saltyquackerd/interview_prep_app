# RAG utilities

import pdfplumber
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import tempfile
import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
import logging

RESUME_TEXT = ""
CHROMA_COLLECTION = None
EMBEDDING_MODEL = None

def process_resume(file, filename):
	global RESUME_TEXT, CHROMA_COLLECTION, EMBEDDING_MODEL
	if filename.endswith(".pdf"):
		with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
			tmp.write(file)
			tmp_path = tmp.name
		with pdfplumber.open(tmp_path) as pdf:
			RESUME_TEXT = "\n".join(page.extract_text() or "" for page in pdf.pages)
		os.remove(tmp_path)
	else:
		RESUME_TEXT = file.decode(errors="ignore")


	logging.basicConfig(level=logging.INFO)
	logger = logging.getLogger("rag_utils")
	logger.info("[RAG] Extracted RESUME_TEXT:\n%s", RESUME_TEXT)

	# Use LangChain's RecursiveCharacterTextSplitter for chunking
	splitter = RecursiveCharacterTextSplitter(
		chunk_size=500,
		chunk_overlap=50,
		separators=["\n\n", "\n", ". ", "! ", "? "]
	)
	chunks = splitter.split_text(RESUME_TEXT)

	logger.info("[RAG] Number of chunks: %d", len(chunks))
	for i, chunk in enumerate(chunks):
		logger.info("[RAG] Chunk %d:\n%s\n---", i, chunk)

	if EMBEDDING_MODEL is None:
		EMBEDDING_MODEL = SentenceTransformer("all-MiniLM-L6-v2")


	client = chromadb.Client(Settings(anonymized_telemetry=False))
	try:
		CHROMA_COLLECTION = client.create_collection("resume_chunks")
	except Exception:
		CHROMA_COLLECTION = client.get_collection("resume_chunks")

	embeddings = EMBEDDING_MODEL.encode(chunks).tolist()
	ids = [f"chunk_{i}" for i in range(len(chunks))]
	CHROMA_COLLECTION.add(documents=chunks, embeddings=embeddings, ids=ids)

def get_relevant_chunks(query):
	global CHROMA_COLLECTION, EMBEDDING_MODEL
	if CHROMA_COLLECTION and EMBEDDING_MODEL and query:
		query_emb = EMBEDDING_MODEL.encode([query]).tolist()[0]
		results = CHROMA_COLLECTION.query(query_embeddings=[query_emb], n_results=3)
		return results.get("documents", [[]])[0]
	return []
