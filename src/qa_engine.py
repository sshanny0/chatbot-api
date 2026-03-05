import re
import threading

import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from database.connection import get_read_connection, get_write_connection

# =========================
# MODEL
# =========================
model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")


# =========================
# GLOBAL STATE
# =========================
lock = threading.Lock()

data = None
unknown_data = None

keyword = []
question = []
answer = []
hyperlink = []
tag = []

question_embeddings = None

u_question = []
unknown_embeddings = None

idf_vectorizer = None
idf_dict = {}
max_idf = 1
min_idf_threshold = 0


# =========================
# TOKENIZER
# =========================
def tokenize(text):
    return re.findall(r"\b\w+\b", str(text).lower())


# =========================
# LOAD MAIN DATASET
# =========================
def load_all_data():
    global data, keyword, question, answer, hyperlink, tag
    global question_embeddings
    global unknown_data, u_question, unknown_embeddings
    global idf_vectorizer, idf_dict, max_idf, min_idf_threshold

    # ================= READ MAIN DATA =================
    conn = get_read_connection()
    try:
        data = pd.read_sql(
            """
            SELECT a.keyword, a.question, a.answer,
                   b.hyperlink, b.tag
            FROM hesk_chatbot_qna a
            LEFT JOIN hesk_chatbot_link b
            ON a.id = b.qna
            """,
            con=conn,
        )
    finally:
        conn.close()

    keyword = data["keyword"].fillna("").tolist()
    question = data["question"].fillna("").tolist()
    answer = data["answer"].fillna("").tolist()
    hyperlink = data["hyperlink"].fillna("").tolist()
    tag = data["tag"].fillna("").tolist()

    # ================= TF-IDF =================
    if question:
        idf_vectorizer = TfidfVectorizer(
            lowercase=True, use_idf=True, smooth_idf=True, norm=None
        )

        idf_vectorizer.fit(question)

        idf_dict = dict(
            zip(idf_vectorizer.get_feature_names_out(), idf_vectorizer.idf_)
        )

        max_idf = max(idf_dict.values())
        min_idf_threshold = np.percentile(list(idf_dict.values()), 75)

        question_embeddings = model.encode(
            question,
            normalize_embeddings=True,
        )
    else:
        question_embeddings = None


# =========================
# LOAD UNKNOWN
# =========================
def load_unknown_data():
    global unknown_data, u_question, unknown_embeddings

    conn = get_read_connection()

    try:
        unknown_data = pd.read_sql(
            "SELECT id, question FROM hesk_chatbot_qna_unknown",
            con=conn,
        )
    finally:
        conn.close()

    if unknown_data.empty:
        u_question = []
        unknown_embeddings = None
        return

    unknown_data["question"] = unknown_data["question"].astype(str)
    u_question = unknown_data["question"].tolist()

    unknown_embeddings = model.encode(u_question, normalize_embeddings=True)


# =========================
# RELOAD ENGINE
# =========================
def reload_engine():
    print("[QA ENGINE] Reloading...")
    load_all_data()
    load_unknown_data()
    print("[QA ENGINE] Reload completed")


# =========================
# DUPLICATE CHECK
# =========================
def is_duplicate_unknown(q, threshold=0.8):
    if unknown_embeddings is None or len(u_question) == 0:
        return False

    q_vec = model.encode(q, normalize_embeddings=True)
    scores = cosine_similarity([q_vec], unknown_embeddings)[0]

    return scores.max() >= threshold


# =========================
# SAVE UNKNOWN
# =========================
def save_unknown(q):
    global unknown_data, u_question, unknown_embeddings

    if is_duplicate_unknown(q):
        return

    conn = get_write_connection()
    cursor = conn.cursor()

    insert_sql = """
        INSERT INTO hesk_chatbot_qna_unknown
        (question, status, created_at, updated_at)
        VALUES (%s, %s, NOW(), NOW())
    """

    try:
        cursor.execute(insert_sql, (q, "new"))
        conn.commit()
        new_id = cursor.lastrowid
    except Exception as e:
        conn.rollback()
        print("Insert unknown error:", e)
        return
    finally:
        cursor.close()
        conn.close()

    # Update memory
    new_row = {"id": new_id, "question": q}

    unknown_data = pd.concat([unknown_data, pd.DataFrame([new_row])], ignore_index=True)

    u_question.append(q)

    unknown_embeddings = model.encode(u_question, normalize_embeddings=True)


# =========================
# SCORING
# =========================
def keyword_bonus(user_q, cand_q, max_bonus=0.4):
    user_tokens = set(tokenize(user_q))
    cand_tokens = set(tokenize(cand_q))

    overlap = user_tokens & cand_tokens
    bonus = 0.0

    for token in overlap:
        idf = idf_dict.get(token, 0)
        if idf >= min_idf_threshold:
            bonus += idf / max_idf

    return min(bonus, max_bonus)


def mismatch_penalty(user_q, cand_q, max_penalty=0.4):
    user_tokens = set(tokenize(user_q))
    cand_tokens = set(tokenize(cand_q))

    extra_tokens = cand_tokens - user_tokens
    penalty = 0.0

    for token in extra_tokens:
        idf = idf_dict.get(token, 0)
        if idf >= min_idf_threshold:
            penalty += idf / max_idf

    return min(penalty, max_penalty)


def missing_user_token_penalty(user_q, cand_q, max_penalty=0.7):
    user_tokens = set(tokenize(user_q))
    cand_tokens = set(tokenize(cand_q))

    missing = user_tokens - cand_tokens
    penalty = 0.0

    for token in missing:
        idf = idf_dict.get(token, 0)
        if idf >= min_idf_threshold:
            penalty += idf / max_idf

    return min(penalty, max_penalty)


# =========================
# MAIN ANSWER FUNCTION
# =========================
def get_answer(user_question, testing=False):

    if question_embeddings is None:
        return {"Status": "empty", "Message": "Dataset kosong"}

    user_vec = model.encode(user_question, normalize_embeddings=True)

    raw_scores = cosine_similarity([user_vec], question_embeddings)[0]
    final_scores = []

    for i, base_score in enumerate(raw_scores):
        bonus = keyword_bonus(user_question, question[i])
        penalty = mismatch_penalty(user_question, question[i])
        missing_penalty = missing_user_token_penalty(user_question, question[i])

        final = base_score + bonus - penalty - missing_penalty
        final_scores.append(max(final, 0))

    final_scores = np.array(final_scores)

    best_idx = final_scores.argmax()
    best_score = final_scores[best_idx]
    best_base_score = raw_scores[best_idx]

    if best_base_score >= 0.6:
        return {
            "Status": "known",
            "Pertanyaan": question[best_idx],
            "Jawaban": answer[best_idx],
            "Link": {
                "url": hyperlink[best_idx],
                "tag": tag[best_idx],
            },
            "Skor": {
                "base": round(float(best_base_score), 3),
                "final": round(float(best_score), 3),
            },
        }

    else:
        if not testing:
            save_unknown(user_question)

        return {
            "Status": "unknown",
            "Message": "Mohon maaf saya belum yakin dengan jawaban saya, silakan hubungi Helpdesk TI",
            "Skor": round(float(best_score), 3),
        }


# =========================
# FILTER BY KEYWORD
# =========================
def get_by_keyword(selected_keyword: str):

    results = []

    for i, k in enumerate(keyword):
        if k.lower() == selected_keyword.lower():
            results.append(
                {
                    "question": question[i],
                    "answer": answer[i],
                    "link": {
                        "url": hyperlink[i],
                        "tag": tag[i],
                    },
                }
            )
    if not results:
        return {"Status": "empty", "Message": "Kategori tidak ditemukan"}

    return {
        "Status": "category",
        "Keyword": selected_keyword,
        "Data": results,
    }


# =========================
# AUTO LOAD ON STARTUP
# =========================
reload_engine()
