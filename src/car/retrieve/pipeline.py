"""The five retrieval conditions compared in the benchmark.

C1  dense                  embedding similarity only
C2  hybrid                 BM25 + dense, fused with reciprocal rank fusion (RRF)
C3  hybrid + filter        C2 restricted to procedures that list the device's hardware class
C4  hybrid + filter + rerank   C3 top-N re-scored by a cross-encoder
C5  C4 + constraint verification   drop procedures whose preconditions are false for the device's
                                   telemetry; keep ones that cannot be checked, but flag them

C1-C4 receive telemetry the way many RAG pipelines do: flattened into text and appended to the question.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

import numpy as np
from rank_bm25 import BM25Okapi

from car.corpus import Precondition, Procedure
from car.verify.check import Verdict, check_procedure

CONDITIONS = ("C1", "C2", "C3", "C4", "C5")
_TOKEN = re.compile(r"[a-z0-9_]+")


def tokenize(text: str) -> list[str]:
    return _TOKEN.findall(text.lower())


def rrf(rankings: list[list[str]], k: int = 60) -> list[str]:
    """Reciprocal rank fusion (Cormack, Clarke & Buettcher, 2009): score(d) = sum 1 / (k + rank)."""
    scores: dict[str, float] = {}
    for ranking in rankings:
        for rank, doc in enumerate(ranking, start=1):
            scores[doc] = scores.get(doc, 0.0) + 1.0 / (k + rank)
    return sorted(scores, key=lambda d: (-scores[d], d))


@dataclass
class Result:
    id: str
    flagged: bool = False  # C5 only: preconditions could not be checked (missing telemetry)


class Retriever:
    def __init__(self, procs: list[Procedure], embed_model: str, rerank_model: str,
                 query_prefix: str = "", rrf_k: int = 60, rerank_depth: int = 20):
        from sentence_transformers import CrossEncoder, SentenceTransformer

        self.procs = procs
        self.by_id = {p.id: p for p in procs}
        self.ids = [p.id for p in procs]
        self.query_prefix = query_prefix
        self.rrf_k = rrf_k
        self.rerank_depth = rerank_depth
        self.bm25 = BM25Okapi([tokenize(p.text) for p in procs])
        self.embedder = SentenceTransformer(embed_model, device="cpu")
        self.doc_emb = self.embedder.encode([p.text for p in procs], normalize_embeddings=True)
        self.reranker = CrossEncoder(rerank_model, device="cpu")

    # --- single-signal rankings ---
    def dense(self, text: str) -> list[str]:
        q = self.embedder.encode([self.query_prefix + text], normalize_embeddings=True)[0]
        sims = self.doc_emb @ q
        return [self.ids[i] for i in np.argsort(-sims, kind="stable")]

    def lexical(self, text: str) -> list[str]:
        scores = self.bm25.get_scores(tokenize(text))
        return [self.ids[i] for i in np.argsort(-scores, kind="stable")]

    def rerank(self, text: str, candidates: list[str]) -> list[str]:
        if not candidates:
            return []
        scores = self.reranker.predict([(text, self.by_id[c].text) for c in candidates])
        order = np.argsort(-np.asarray(scores), kind="stable")
        return [candidates[i] for i in order]

    # --- conditions ---
    def search(self, condition: str, text: str, device_class: str, state: dict,
               k: int, preconditions: dict[str, list[Precondition]] | None = None) -> list[Result]:
        if condition == "C1":
            return [Result(d) for d in self.dense(text)[:k]]
        hybrid = rrf([self.lexical(text), self.dense(text)], k=self.rrf_k)
        if condition == "C2":
            return [Result(d) for d in hybrid[:k]]
        filtered = [d for d in hybrid if device_class in self.by_id[d].device_classes]
        if condition == "C3":
            return [Result(d) for d in filtered[:k]]
        reranked = self.rerank(text, filtered[: self.rerank_depth])
        return self._finish(condition, reranked, device_class, state, k, preconditions)

    def candidates(self, text: str, device_class: str) -> list[str]:
        """The full C4 ranking (hybrid -> class filter -> rerank top-N), reused by the ablations."""
        hybrid = rrf([self.lexical(text), self.dense(text)], k=self.rrf_k)
        filtered = [d for d in hybrid if device_class in self.by_id[d].device_classes]
        return self.rerank(text, filtered[: self.rerank_depth])

    def _finish(self, condition, reranked, device_class, state, k, preconditions):
        if condition == "C4":
            return [Result(d) for d in reranked[:k]]
        if condition == "C5":
            return self.verify(reranked, device_class, state, k, preconditions)
        raise ValueError(f"unknown condition {condition}")

    def verify(self, ranked: list[str], device_class: str, state: dict, k: int,
               preconditions: dict[str, list[Precondition]] | None = None) -> list[Result]:
        """Constraint verification is a filter, not a re-ranker: drop FAIL, keep the ranking order,
        and flag UNKNOWN results so the agent (or a person) knows they could not be checked."""
        out = []
        for d in ranked:
            pres = None if preconditions is None else preconditions[d]
            v = check_procedure(self.by_id[d], device_class, state, pres)
            if v is not Verdict.FAIL:
                out.append(Result(d, flagged=v is Verdict.UNKNOWN))
            if len(out) == k:
                break
        return out
