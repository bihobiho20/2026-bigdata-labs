#!/usr/bin/env python3
"""Week 3 · Task 1 — Minhash and LSH, built from the matrix up.

Textbook §3.2 - §3.4.

Comparing every pair is quadratic, so it stops being possible somewhere around
a hundred thousand documents. The way out is two ideas stacked:

    minhash   replace a set with a short signature, such that the chance two
              signatures agree in a position equals their Jaccard similarity
    LSH       hash bands of those signatures so that similar pairs collide and
              you only ever compare the ones that did

You build both. The textbook's §3.3.5 example is small enough to check by hand,
and the harness checks you against it.

    python3 task1_minhash.py --verify
"""
import argparse

# §3.3.5. Rows are elements 0..4, columns are the sets S1..S4.
BOOK = [[1, 0, 0, 1],
        [0, 0, 1, 0],
        [0, 1, 0, 1],
        [1, 0, 1, 1],
        [0, 0, 1, 0]]
# The two hash functions the textbook uses on the row numbers.
BOOK_HASHES = [lambda r: (r + 1) % 5, lambda r: (3 * r + 1) % 5]


def jaccard(a, b):
    # 교집합 / 합집합, 빈 합집합은 0
    union = a | b
    return len(a & b) / len(union) if union else 0.0


def minhash_signatures(columns, hashes, n_rows):
    # 서명 초기화, 빈 열은 무한대
    signatures = [[float("inf")] * len(hashes) for _ in columns]
    for row in range(n_rows):
        # 행별 해시 계산 및 재사용
        values = [h(row) for h in hashes]
        for column_index, column in enumerate(columns):
            if row in column:
                # 해당 열의 최솟값 갱신
                for hash_index, value in enumerate(values):
                    signatures[column_index][hash_index] = min(
                        signatures[column_index][hash_index], value)
    return signatures


def lsh_candidates(signatures, bands):
    if not isinstance(bands, int) or bands <= 0:
        raise ValueError("bands must be a positive integer")
    if not signatures:
        return set()
    length = len(signatures[0])
    if any(len(signature) != length for signature in signatures):
        raise ValueError("all signatures must have the same length")
    # 균등 분할 불가능한 입력 거부
    if length == 0 or length % bands:
        raise ValueError("signature length must be positive and divisible by bands")

    rows_per_band = length // bands
    candidates = set()
    for band in range(bands):
        # band별 버킷 초기화
        buckets = {}
        start = band * rows_per_band
        for column_index, signature in enumerate(signatures):
            key = tuple(signature[start:start + rows_per_band])
            bucket = buckets.setdefault(key, [])
            # 같은 버킷의 후보 쌍 추가 (앞 번호 < 뒤 번호)
            for previous in bucket:
                candidates.add((previous, column_index))
            bucket.append(column_index)
    return candidates


# ------------------------------------------------------------------- harness
def columns_from_matrix(matrix):
    n_rows, n_cols = len(matrix), len(matrix[0])
    return [{r for r in range(n_rows) if matrix[r][c]} for c in range(n_cols)]


def verify():
    fails = 0

    def check(label, got, want):
        nonlocal fails
        ok = got == want
        print(f"  {'ok  ' if ok else 'FAIL'}  {label:<44} {got}"
              + ("" if ok else f"\n{'':>54}want {want}"))
        fails += not ok

    cols = columns_from_matrix(BOOK)
    try:
        # S1 = {0,3}, S4 = {0,2,3}: intersection 2, union 3
        check("jaccard(S1, S4)", round(jaccard(cols[0], cols[3]), 4), round(2 / 3, 4))
        check("jaccard(S1, S2)", jaccard(cols[0], cols[1]), 0.0)
        check("jaccard on empty sets", jaccard(set(), set()), 0)
    except NotImplementedError:
        print("  jaccard is still a stub"); return 1

    try:
        sig = minhash_signatures(cols, BOOK_HASHES, len(BOOK))
    except NotImplementedError:
        print("  minhash_signatures is still a stub"); return 1

    # Figure 3.4 in the textbook.
    check("signature of S1", sig[0], [1, 0])
    check("signature of S2", sig[1], [3, 2])
    check("signature of S3", sig[2], [0, 0])
    check("signature of S4", sig[3], [1, 0])

    try:
        cands = lsh_candidates([[1, 0], [3, 2], [0, 0], [1, 0]], bands=2)
    except NotImplementedError:
        print("  lsh_candidates is still a stub"); return 1
    # With one row per band, S1 and S4 are identical, so they must collide.
    check("S1 and S4 are candidates", (0, 3) in cands, True)
    check("S1 and S2 are not", (0, 1) in cands, False)

    print(f"\n  {'all ok' if not fails else str(fails) + ' failed'}")
    if not fails:
        print("  Note that S1 and S4 agree in both signature positions, which "
              "estimates\n  their similarity as 1.0 when it is actually 2/3. "
              "Two hashes is not many.")
    return 1 if fails else 0


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--verify", action="store_true")
    a = p.parse_args()
    raise SystemExit(verify() if a.verify else p.print_help())
