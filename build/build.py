"""Bundle question sources into questions.js.

Run:  python3 build/build.py
Each source file in data/src/ is a JSON list of
  {t: topic, s: source, q: question, a: answer, w: [3 wrong], e: explanation}
File prefix decides the subject: phil_, dm_, dv_, jp_.
Generated on top of that (Japanese):
  kanji      from build/kanji_data.txt
  vocabulary from build/vocab_*.txt
  katakana   from build/katakana.py
Every question also gets L (lesson), T (topic within the lesson, optional),
k (kind, Japanese only) so Practice can filter by lesson and topic.
"""
import glob, hashlib, json, os, random, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))
import katakana  # noqa: E402

SUBJECT_BY_PREFIX = {"phil": "philosophy", "dm": "datamining", "dv": "dataviz", "jp": "japanese"}
BOOKS = {"G1": "Genki I", "G2": "Genki II", "Q1": "Quartet I"}
DM_LESSONS = {2: "Statistical Principles", 3: "Word Embeddings", 4: "Distances", 5: "Nearest Neighbor Search (ANN & HNSW)",
              6: "Jaccard Similarity & MinHash", 7: "LSH & Distribution Distances", 8: "Hierarchical & Density Clustering",
              9: "k-Means", 10: "Spectral Clustering", 11: "Choosing k"}


def qid(q):
    return hashlib.sha1((q["q"] + "|" + q["a"]).encode("utf-8")).hexdigest()[:10]


def kanji_questions():
    rows = []
    for line in open(os.path.join(ROOT, "build", "kanji_data.txt"), encoding="utf-8"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        lesson, k, meaning, word, reading, wmeaning = line.split("|")
        book = "Genki I" if lesson.startswith("G1") else "Genki II"
        rows.append(dict(lesson=lesson, book=book, num=lesson.split("L")[1], k=k,
                         meaning=meaning, word=word, reading=reading, wmeaning=wmeaning))
    rng = random.Random(42)
    out, seen_words = [], set()
    for r in rows:
        same_book = [x for x in rows if x["book"] == r["book"] and x["k"] != r["k"]]
        topic = f"{r['book']} L{r['num']} – Kanji"
        src = f"{r['book']}, Lesson {r['num']} kanji"
        pool = list({x["meaning"] for x in same_book if x["meaning"] != r["meaning"]})
        rng.shuffle(pool)
        out.append(dict(t=topic, s=src, q=f"What does the kanji 「{r['k']}」 mean?",
                        a=r["meaning"], w=pool[:3],
                        e=f"{r['k']} = {r['meaning']}. Example: {r['word']}（{r['reading']}）: {r['wmeaning']}."))
        if r["word"] not in seen_words:
            seen_words.add(r["word"])
            pool = list({x["reading"] for x in same_book if x["reading"] != r["reading"]})
            pool.sort(key=lambda s: (abs(len(s) - len(r["reading"])), rng.random()))
            out.append(dict(t=topic, s=src, q=f"How do you read 「{r['word']}」?",
                            a=r["reading"], w=pool[:3],
                            e=f"{r['word']} is read {r['reading']} and means '{r['wmeaning']}'."))
            pool = list({x["wmeaning"] for x in same_book if x["wmeaning"] != r["wmeaning"]})
            rng.shuffle(pool)
            out.append(dict(t=topic, s=src, q=f"What does 「{r['word']}」 mean?",
                            a=r["wmeaning"], w=pool[:3],
                            e=f"{r['word']}（{r['reading']}）= {r['wmeaning']}. Kanji: {r['k']} ({r['meaning']})."))
    return out


def vocab_questions():
    rows, seen = [], set()
    for f in sorted(glob.glob(os.path.join(ROOT, "build", "vocab_*.txt"))):
        for line in open(f, encoding="utf-8"):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            lesson, word, reading, meaning = line.split("|")
            reading = reading or word
            if (word, reading) in seen:      # first lesson that introduces a word keeps it
                continue
            seen.add((word, reading))
            book, num = BOOKS[lesson[:2]], lesson.split("L")[1]
            rows.append(dict(book=book, num=num, word=word, reading=reading, meaning=meaning,
                             verb=meaning.startswith("to ") or "(honorific)" in meaning or "(humble)" in meaning or "(extra-modest)" in meaning))
    rng = random.Random(11)
    show = lambda r: r["word"] if r["word"] == r["reading"] else f"{r['word']}（{r['reading']}）"
    out = []
    for r in rows:
        same = [x for x in rows if x["book"] == r["book"] and x["num"] == r["num"] and x is not r and x["meaning"] != r["meaning"]]
        near = [x for x in rows if x["book"] == r["book"] and abs(int(x["num"]) - int(r["num"])) <= 2 and x is not r and x["meaning"] != r["meaning"]]
        def parts(m):
            return {re.sub(r"\s+", " ", re.sub(r"\([^)]*\)", "", x)).strip().lower() for x in m.split(";")} - {""}
        def pick(key):
            pool, got = sorted(same, key=lambda x: (x["verb"] != r["verb"], rng.random())), []
            pool += sorted(near, key=lambda x: (x["verb"] != r["verb"], rng.random()))
            for x in pool:
                v = key(x)
                if v != key(r) and v not in got and not (parts(x["meaning"]) & parts(r["meaning"])):
                    got.append(v)
                if len(got) == 3:
                    break
            return got
        topic = f"{r['book']} L{r['num']} – Vocabulary"
        src = f"{r['book']}, Lesson {r['num']} vocabulary"
        e = f"{show(r)}: {r['meaning']}."
        out.append(dict(t=topic, s=src, q=f"What does 「{show(r)}」 mean?", a=r["meaning"], w=pick(lambda x: x["meaning"]), e=e))
        out.append(dict(t=topic, s=src, q=f"How do you say “{r['meaning']}” in Japanese?", a=show(r), w=pick(show), e=e))
    return out


def annotate(subj, q):
    """Attach lesson (L), topic within lesson (T), kind (k) and group (g)."""
    t, s = q["t"], q.get("s", "")
    if subj == "japanese":
        if q.get("k") == "kana":
            return
        m = re.match(r"^(Genki II|Genki I|Quartet I) L(\d+) – (.*)$", t)
        book, num, rest = m.groups()
        q["g"], q["L"] = book, f"{book} L{num}"
        if rest == "Kanji":
            q["k"], q["T"] = "kanji", "Kanji"
        elif rest == "Vocabulary":
            q["k"], q["T"] = "vocab", "Vocabulary"
        else:
            q["k"], q["T"] = "grammar", rest
    elif subj == "datamining":
        m = re.match(r"^L(\d+) – (.*)$", t)
        n = int(m.group(1))
        q["L"], q["T"] = f"L{n} – {DM_LESSONS.get(n, '')}".rstrip(" –"), m.group(2)
    elif subj == "dataviz":
        q["L"] = t
    elif subj == "philosophy":
        if s.startswith("Lecture:"):
            q["g"], q["L"], q["T"] = "Lecture slides", re.sub(r"\s*\(.*$", "", s).replace("Lecture: ", "Lecture – "), t
        else:
            q["g"], q["L"] = "Readings", t
            part = re.sub(r"\s*\([^)]*\)", "", s.split(", ")[-1]).strip()
            if part and not part.startswith(t.split(" – ")[0]):
                q["T"] = part[0].upper() + part[1:]


def lesson_order(subj, qs):
    def key(L):
        g = next(q.get("g", "") for q in qs if q["L"] == L)
        if subj == "japanese":
            gi = ["Kana", "Genki I", "Genki II", "Quartet I"].index(g)
            n = int(re.search(r"L(\d+)$", L).group(1)) if g != "Kana" else 0
            return (gi, n)
        if subj == "philosophy":
            return (0 if g == "Lecture slides" else 1, L)
        m = re.match(r"^L?(\d+)", L)
        return (int(m.group(1)) if m else 999, L)
    out = []
    for L in sorted({q["L"] for q in qs}, key=key):
        group = next(q.get("g", "") for q in qs if q["L"] == L)
        topics = []
        for q in qs:
            if q["L"] == L and q.get("T") and q["T"] not in topics:
                topics.append(q["T"])
        if subj == "philosophy" and len(topics) < 2:   # a single section isn't worth a filter
            topics = []
            for q in qs:
                if q["L"] == L:
                    q.pop("T", None)
        out.append({"L": L, "g": group, "topics": topics})
    return out


def main():
    bank = {v: [] for v in SUBJECT_BY_PREFIX.values()}
    for f in sorted(glob.glob(os.path.join(ROOT, "data", "src", "*.json"))):
        subj = SUBJECT_BY_PREFIX[os.path.basename(f).split("_")[0]]
        bank[subj].extend(json.load(open(f, encoding="utf-8")))
    bank["japanese"].extend(kanji_questions())
    bank["japanese"].extend(vocab_questions())
    bank["japanese"].extend(katakana.questions())
    lessons = {}
    for subj, qs in bank.items():
        ids, keep = set(), []
        for q in qs:
            assert q["a"] not in q["w"] and len(set(q["w"])) == 3, q
            q["id"] = qid(q)
            if q["id"] in ids:
                assert q.get("k") in ("vocab", "kana"), q
                continue
            ids.add(q["id"])
            annotate(subj, q)
            keep.append(q)
        bank[subj] = keep
        lessons[subj] = lesson_order(subj, keep)
        kinds = {}
        for q in keep:
            kinds[q.get("k", "-")] = kinds.get(q.get("k", "-"), 0) + 1
        print(f"{subj}: {len(keep)} questions, {len(lessons[subj])} lessons", kinds if subj == "japanese" else "")
    js = "// Generated by build/build.py. Edit data/src/*.json and build/*.txt instead.\nwindow.QUESTION_BANK = " + \
        json.dumps(bank, ensure_ascii=False, separators=(",", ":")) + ";\nwindow.LESSONS = " + \
        json.dumps(lessons, ensure_ascii=False, separators=(",", ":")) + ";\n"
    open(os.path.join(ROOT, "questions.js"), "w", encoding="utf-8").write(js)


if __name__ == "__main__":
    main()
