"""Pruebas de las funciones de ranking de scripts/baselines.py (no necesitan spaCy).

Ejecutar desde la raíz del repositorio:
    python -m unittest tests.test_baselines -v
"""

import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from baselines import rank_chunks, rank_documents

CHUNKS = ['a__1', 'a__2', 'b__1', 'c__1', 'c__2']
DOCS = ['a', 'a', 'b', 'c', 'c']


class RankingTests(unittest.TestCase):
    def test_document_gets_score_of_best_chunk_without_duplicates(self):
        ranking = rank_documents(np.array([0.2, 0.9, 0.5, 0.1, 0.7]), CHUNKS, DOCS, k=10)
        self.assertEqual([d['doc_id'] for d in ranking], ['a', 'c', 'b'])
        self.assertEqual([d['best_chunk'] for d in ranking], ['a__2', 'c__2', 'b__1'])
        self.assertEqual([d['rank'] for d in ranking], [1, 2, 3])

    def test_k_counts_documents_not_chunks(self):
        ranking = rank_documents(np.array([0.9, 0.8, 0.5, 0.1, 0.7]), CHUNKS, DOCS, k=2)
        self.assertEqual([d['doc_id'] for d in ranking], ['a', 'c'])

    def test_zero_scores_are_not_retrieved(self):
        self.assertEqual(rank_documents(np.zeros(5), CHUNKS, DOCS), [])
        ranking = rank_documents(np.array([0.0, 0.0, 0.3, 0.0, 0.0]), CHUNKS, DOCS)
        self.assertEqual([d['doc_id'] for d in ranking], ['b'])

    def test_ties_keep_corpus_order(self):
        ranking = rank_documents(np.array([0.5, 0.5, 0.5, 0.5, 0.5]), CHUNKS, DOCS)
        self.assertEqual([d['best_chunk'] for d in ranking], ['a__1', 'b__1', 'c__1'])

    def test_rank_chunks(self):
        ranking = rank_chunks(np.array([0.2, 0.9, 0.0, 0.1, 0.7]), CHUNKS, DOCS, k=3)
        self.assertEqual([c['chunk_id'] for c in ranking], ['a__2', 'c__2', 'a__1'])


if __name__ == '__main__':
    unittest.main()
