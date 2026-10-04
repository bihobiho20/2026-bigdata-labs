#!/usr/bin/env python3
"""Week 3 · Task 3 — Find the same pairs without comparing everything.

Textbook §3.4.

`BruteForce` compares every pair. On 3,000 documents that is 4.5 million
comparisons and it is completely correct. On 3 million documents it is 4.5
trillion and it is completely useless.

Beat it. Find the same near-duplicate pairs while making far fewer comparisons.

    python3 bench.py
    python3 bench.py --yours

The harness counts every call you make to `similarity()`. That is your score.
It also checks **recall** - which of the truly similar pairs you found. Skipping
comparisons is easy; skipping comparisons without losing the pairs is the task.
"""


import random

from task1_minhash import lsh_candidates, minhash_signatures


class BruteForce:
    """Correct, and quadratic."""

    def __init__(self, threshold):
        self.threshold = threshold

    def find(self, docs, similarity):
        """docs is [set_of_shingles, ...]. Return {(i, j), ...} with i < j."""
        out = set()
        for i in range(len(docs)):
            for j in range(i + 1, len(docs)):
                if similarity(docs[i], docs[j]) >= self.threshold:
                    out.add((i, j))
        return out


class YourFinder:
    def __init__(self, threshold):
        self.threshold = threshold
        self.n_hashes = 120
        self.bands = 30

        # 고정 시드의 해시 함수 생성
        rng = random.Random(246)
        prime = 2_147_483_647
        self.hashes = []
        for _ in range(self.n_hashes):
            a = rng.randrange(1, prime)
            b = rng.randrange(prime)
            self.hashes.append(lambda row, a=a, b=b: (a * row + b) % prime)

    def find(self, docs, similarity):
        # shingle을 연속된 행 번호로 변환
        row_numbers = {}
        columns = []
        for doc in docs:
            column = set()
            for shingle in sorted(doc):
                if shingle not in row_numbers:
                    row_numbers[shingle] = len(row_numbers)
                column.add(row_numbers[shingle])
            columns.append(column)

        # Task1의 서명 생성 및 banding 재사용
        signatures = minhash_signatures(columns, self.hashes, len(row_numbers))
        candidates = lsh_candidates(signatures, self.bands)

        # 후보만 실제 유사도 비교
        out = set()
        for i, j in candidates:
            if similarity(docs[i], docs[j]) >= self.threshold:
                out.add((i, j))
        return out
