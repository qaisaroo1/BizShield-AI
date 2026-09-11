import json
import os
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
import numpy as np

from src.config import GEMINI_API_KEY, EMBEDDING_MODEL, DATA_DIR

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None


class LegalRAGStore:
    """
    Retrieval-Augmented Generation (RAG) Vector Knowledge Store:
    Indexes official Pakistani commercial laws, FBR tax statutes, SECP regulations,
    and contract rubrics using Google Gemini Embeddings (gemini-embedding-001).
    Performs semantic vector retrieval with cosine similarity and keyword fallback.
    """

    def __init__(self, storage_file: Optional[Path] = None):
        self.storage_file = storage_file or (DATA_DIR / "legal_rag_cache.json")
        self.chunks: List[Dict[str, Any]] = []
        self.embeddings: Optional[np.ndarray] = None
        self.client = None

        if GEMINI_API_KEY and genai:
            try:
                self.client = genai.Client(api_key=GEMINI_API_KEY)
            except Exception as e:
                print(f"[LegalRAGStore] Gemini client error: {e}")

        # Load or initialize index
        self._initialize_knowledge_base()

    def _get_embedding(self, text: str) -> Optional[List[float]]:
        """Compute 768-dimensional dense vector embedding using Google Gemini."""
        if not self.client:
            return None
        try:
            response = self.client.models.embed_content(
                model=EMBEDDING_MODEL,
                contents=text,
            )
            if response.embeddings:
                return response.embeddings[0].values
        except Exception as e:
            print(f"[LegalRAGStore] Embedding generation error: {e}")
        return None

    def _initialize_knowledge_base(self):
        """Loads existing cached vector index or builds from raw data files."""
        if self.storage_file.exists():
            try:
                with open(self.storage_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.chunks = data.get("chunks", [])
                    raw_embs = data.get("embeddings", [])
                    if raw_embs:
                        self.embeddings = np.array(raw_embs, dtype=np.float32)
                if self.chunks:
                    print(f"[LegalRAGStore] Loaded {len(self.chunks)} legal chunks from vector cache.")
                    return
            except Exception as e:
                print(f"[LegalRAGStore] Error loading cache: {e}. Rebuilding index...")

        # Build fresh chunks from data folder
        self._build_and_index_chunks()

    def _build_and_index_chunks(self):
        """Ingests and chunks all legal and tax reference files in data/."""
        raw_chunks: List[Dict[str, Any]] = []

        # 1. Ingest Pakistan Business Regulations
        reg_file = DATA_DIR / "pakistan_business_regulations.json"
        if reg_file.exists():
            with open(reg_file, "r", encoding="utf-8") as f:
                regs = json.load(f)
                for auth in regs.get("authorities", []):
                    raw_chunks.append({
                        "id": f"reg_{auth['code'].lower()}",
                        "title": f"{auth['name']} ({auth['code']})",
                        "authority": auth["code"],
                        "statute": auth["primary_statute"],
                        "content": f"Authority: {auth['name']} ({auth['code']}). Primary Statute: {auth['primary_statute']}. Portal: {auth['portal']}. Regulatory Mandate: {auth['mandate']}"
                    })
                for d in regs.get("key_compliance_deadlines", []):
                    raw_chunks.append({
                        "id": f"deadline_{len(raw_chunks)}",
                        "title": f"Deadline: {d['event']}",
                        "authority": "FBR / Statutory",
                        "statute": "Income Tax Ordinance 2001",
                        "content": f"Compliance Event: {d['event']}. Statutory Deadline: {d['statutory_deadline']}. Legal Consequences of Non-Compliance: {d['consequence_of_delay']}"
                    })

        # 2. Ingest Common Legal Traps
        traps_file = DATA_DIR / "common_legal_traps.json"
        if traps_file.exists():
            with open(traps_file, "r", encoding="utf-8") as f:
                traps = json.load(f)
                for t in traps:
                    raw_chunks.append({
                        "id": t["id"],
                        "title": f"Contract Trap: {t['name']}",
                        "authority": "Commercial Contract Law",
                        "statute": "Contract Act 1872 & Standard Best Practices",
                        "content": f"Risk Category: {t['name']}. Severity: {t['risk_level']} Risk. Legal Details: {t['description']}"
                    })

        # 3. Ingest SME QA Knowledge Base
        qa_file = DATA_DIR / "sme_qa_knowledge_base.json"
        if qa_file.exists():
            with open(qa_file, "r", encoding="utf-8") as f:
                qas = json.load(f)
                for i, q in enumerate(qas.get("faq", [])):
                    raw_chunks.append({
                        "id": f"faq_{i}",
                        "title": q["question"],
                        "authority": "Pakistani Commercial Law & Taxation",
                        "statute": q["legal_basis"],
                        "content": f"Question: {q['question']}. Legal Guidance: {q['summary']}. Governing Legal Basis: {q['legal_basis']}"
                    })

        self.chunks = raw_chunks
        print(f"[LegalRAGStore] Created {len(self.chunks)} structured legal chunks.")

        # Compute embeddings
        emb_list = []
        for i, chunk in enumerate(self.chunks):
            emb = self._get_embedding(chunk["content"])
            if emb is not None:
                emb_list.append(emb)
            else:
                # Deterministic pseudo-embedding for offline fallback
                np.random.seed(hash(chunk["id"]) % (2**32))
                emb_list.append(np.random.randn(768).tolist())

        self.embeddings = np.array(emb_list, dtype=np.float32)

        # Normalize for fast cosine similarity via dot product
        norms = np.linalg.norm(self.embeddings, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        self.embeddings = self.embeddings / norms

        # Cache to disk
        try:
            with open(self.storage_file, "w", encoding="utf-8") as f:
                json.dump({
                    "chunks": self.chunks,
                    "embeddings": self.embeddings.tolist()
                }, f, indent=2)
            print(f"[LegalRAGStore] Cached {len(self.chunks)} vector embeddings to {self.storage_file.name}.")
        except Exception as e:
            print(f"[LegalRAGStore] Cache write error: {e}")

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Semantic RAG Search:
        Embeds the user query, computes cosine similarity with legal statutes,
        and returns the top-k most relevant statutory contexts.
        """
        if not self.chunks:
            return []

        # Vector search
        query_emb = self._get_embedding(query)
        if query_emb is not None and self.embeddings is not None:
            q_vec = np.array(query_emb, dtype=np.float32)
            q_norm = np.linalg.norm(q_vec)
            if q_norm > 0:
                q_vec = q_vec / q_norm
                sims = np.dot(self.embeddings, q_vec)
                top_indices = np.argsort(sims)[::-1][:top_k]

                results = []
                for idx in top_indices:
                    chunk_copy = dict(self.chunks[idx])
                    chunk_copy["similarity_score"] = float(round(sims[idx], 4))
                    results.append(chunk_copy)
                return results

        # Keyword / BM25 fallback if offline
        query_terms = set(re.findall(r"\w+", query.lower()))
        scored = []
        for chunk in self.chunks:
            c_terms = set(re.findall(r"\w+", chunk["content"].lower()))
            overlap = len(query_terms.intersection(c_terms))
            score = overlap / (len(query_terms) + 1)
            scored.append((score, chunk))

        scored.sort(key=lambda x: x[0], reverse=True)
        fallback_results = []
        for score, chunk in scored[:top_k]:
            c_copy = dict(chunk)
            c_copy["similarity_score"] = float(round(score, 4))
            fallback_results.append(c_copy)
        return fallback_results
