import paramiko

# PATCH: tambahin DSSKey palsu biar sshtunnel ga error
if not hasattr(paramiko, "DSSKey"):
    paramiko.DSSKey = paramiko.RSAKey
import os
import re

import mysql.connector as sql
import numpy as np
import pandas as pd
import sshtunnel
from dotenv import load_dotenv

# from datetime import datetime
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

load_dotenv()  # LOAD ENV


def get_db_connection():
    # CONENCTION VIA SSH TUNNEL
    tunnel = sshtunnel.SSHTunnelForwarder(
        (os.getenv("SSH_HOST"), int(os.getenv("SSH_PORT"))),
        ssh_username=os.getenv("SSH_USERNAME"),
        ssh_password=os.getenv("SSH_PASSWORD"),
        remote_bind_address=(os.getenv("DB_HOST"), int(os.getenv("DB_PORT"))),
    )
    tunnel.start()
    conn = sql.connect(
        user=os.getenv("DB_USERNAME"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=tunnel.local_bind_port,
        database=os.getenv("DB_NAME"),
        autocommit=True,
    )

    return conn, tunnel


# CONNECTION IF LOCAL
# mydb = sql.connect(
#   host="localhost",
#   user="hesk",
#   password="@S3cr3tDBp55n",
#   database="hesk"
# )

# =========================
# DATASET
# =========================
mydb, tunnel = get_db_connection()

data = pd.read_sql(
    "SELECT a.question AS question, a.answer AS answer, b.hyperlink AS hyperlink, b.tag AS tag FROM hesk_chatbot_qna a LEFT JOIN hesk_chatbot_link b ON a.id = b.qna",
    con=mydb,
)
# data = pd.read_excel("data/list-qna.xlsx") # EXCEL
# data.Pertanyaan = data.Pertanyaan.astype(str)
# data.Jawaban = data.Jawaban.astype(str)

question = data["question"].tolist()
answer = data["answer"].tolist()
hyperlink = data["hyperlink"].tolist()
tag = data["tag"].tolist()
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
unknown_data = pd.read_sql("SELECT * FROM hesk_chatbot_qna_unknown", con=mydb)
mydb.close()
tunnel.stop()

unknown_data["question"] = unknown_data["question"].astype(str)
u_question = unknown_data["question"].tolist()

### EXCEL ###
# unknown_path = "data/unknown-questions.xlsx"
# if os.path.exists(unknown_path):
#     unknown_data = pd.read_excel(unknown_path)
#     unknown_data.question = unknown_data.question.astype(str)
#     u_question = unknown_data.question.tolist()
# else:
#     unknown_data = pd.DataFrame(columns=["question", "timestamp"])
#     u_question = []

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

    cursor = mydb.cursor()

    sql = """
        INSERT INTO hesk_chatbot_qna_unknown
        (question, status, created_at, updated_at)
        VALUES (:question, :status, NOW(), NOW())
    """

    try:
        cursor.execute(sql, (q, "new"))
        new_id = cursor.lastrowid
    except sql.errors.IntegrityError:
        # duplicate di level DB
        mydb.close()
        tunnel.stop()
        return

    # Update dataframe in-memory
    new_row = {"id": new_id, "question": q}

    unknown_data = pd.concat([unknown_data, pd.DataFrame([new_row])], ignore_index=True)

    ### EXCEL
    # new_row = {"question": q, "timestamp": datetime.now()}
    # unknown_data = pd.concat([unknown_data, pd.DataFrame([new_row])], ignore_index=True)
    # unknown_data.to_excel(unknown_path, index=False)

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
def get_answer(user_question):
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

    # =========================
    # DECISION LOGIC
    # =========================
    if best_base_score >= 0.6:
        return {
            "Status": "known",
            "Pertanyaan": question[best_idx],
            "Jawaban": answer[best_idx],
            "Link": {"url": hyperlink[best_idx], "tag": tag[best_idx]},
            "Skor": {
                "base": round(float(best_base_score), 3),
                "final": round(float(best_score), 3),
            },
        }

    # 2. TOPIK BARU (tidak ada yang mendekati)
    #
    else:
        save_unknown(user_question)
        return {
            "Status": "unknown",
            "Message": "Mohon maaf saya belum yakin dengan jawaban saya, silakan hubungi Helpdesk TI",
            "Skor": round(float(best_score), 3),
        }
