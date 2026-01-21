import pandas as pd
import numpy as np
import os
import re
from datetime import datetime
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

# =========================
# DATASET
# =========================
data = pd.read_excel("data/list-qna.xlsx")
data.Pertanyaan = data.Pertanyaan.astype(str)
data.Jawaban = data.Jawaban.astype(str)

question = data.Pertanyaan.tolist()
answer = data.Jawaban.tolist()

# =========================
# TF-IDF (TOKEN IMPORTANCE)
# =========================
idf_vectorizer = TfidfVectorizer(
    lowercase=True, use_idf=True, smooth_idf=True, norm=None
)

idf_vectorizer.fit(question)

idf_dict = dict(zip(idf_vectorizer.get_feature_names_out(), idf_vectorizer.idf_))

max_idf = max(idf_dict.values())
min_idf_threshold = np.percentile(list(idf_dict.values()), 75)  # token penting


# =========================
# TOKENIZER
# =========================
def tokenize(text):
    return re.findall(r"\b\w+\b", text.lower())


# =========================
# EMBEDDING MODEL
# =========================
model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

question_embeddings = model.encode(question, normalize_embeddings=True)

# =========================
# UNKNOWN QUESTION MEMORY
# =========================
unknown_path = "data/unknown-questions.xlsx"

if os.path.exists(unknown_path):
    unknown_data = pd.read_excel(unknown_path)
    unknown_data.question = unknown_data.question.astype(str)
    u_question = unknown_data.question.tolist()
else:
    unknown_data = pd.DataFrame(columns=["question", "timestamp"])
    u_question = []

unknown_embeddings = (
    model.encode(u_question, normalize_embeddings=True) if u_question else None
)


# =========================
# DUPLICATE CHECK
# =========================
def is_duplicate_unknown(q, threshold=0.8):
    global unknown_embeddings

    if unknown_embeddings is None or len(u_question) == 0:
        return False

    q_vec = model.encode(q, normalize_embeddings=True)
    scores = cosine_similarity([q_vec], unknown_embeddings)[0]

    return scores.max() >= threshold


# =========================
# SAVE UNKNOWN QUESTION
# =========================
def save_unknown(q):
    global unknown_data, unknown_embeddings, u_question

    if is_duplicate_unknown(q):
        return

    new_row = {"question": q, "timestamp": datetime.now()}

    unknown_data = pd.concat([unknown_data, pd.DataFrame([new_row])], ignore_index=True)

    unknown_data.to_excel(unknown_path, index=False)

    u_question.append(q)
    unknown_embeddings = model.encode(u_question, normalize_embeddings=True)


# =========================
# SCORING FUNCTIONS
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
    """
    INI KUNCI UTAMA:
    token penting user yang hilang di kandidat → penalti
    """
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
# MAIN FUNCTION
# =========================
def get_answer(user_question, suggest_top=2):
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

    # =========================
    # DECISION LOGIC
    # =========================
    if best_score >= 0.75:
        return {
            "Status": "known",
            "Pertanyaan": question[best_idx],
            "Jawaban": answer[best_idx],
            "Skor": round(float(best_score), 3),
        }

    elif 0.5 <= best_score < 0.75:
        save_unknown(user_question)

        top_indices = final_scores.argsort()[-suggest_top:][::-1]

        return {
            "Status": "unknown",
            "Message": "Saya mungkin dapat menemukan jawaban yang relevan:",
            "Saran": [
                {
                    "Pertanyaan": question[i],
                    "Jawaban": answer[i],
                    "Skor": round(float(final_scores[i]), 3),
                }
                for i in top_indices
            ],
        }

    else:
        save_unknown(user_question)
        return {
            "Status": "unknown",
            "Message": "Mohon maaf saya belum yakin dengan jawaban saya, silakan hubungi Helpdesk TI",
            "Skor": round(float(best_score), 3),
        }
