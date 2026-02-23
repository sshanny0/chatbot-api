import pandas as pd

from database.connection import get_db_connection


def get_qna_data(page: int = 1, limit: int = 10):
    mydb, tunnel = get_db_connection()

    try:
        offset = (page - 1) * limit

        data = pd.read_sql(
            f"""
            SELECT a.ID AS id,
                   a.question AS question,
                   a.keyword AS category,
                   a.answer AS answer,
                   b.hyperlink AS hyperlink,
                   b.tag AS tag,
                   a.status AS status
            FROM hesk_chatbot_qna a
            LEFT JOIN hesk_chatbot_link b
            ON a.id = b.qna
            ORDER BY id ASC
            LIMIT {limit} OFFSET {offset}
            """,
            con=mydb,
        )

        total = pd.read_sql(
            "SELECT COUNT(*) as count FROM hesk_chatbot_qna",
            con=mydb,
        )

        return {
            "data": data.to_dict(orient="records"),
            "total": int(total["count"][0]),
            "page": page,
            "limit": limit,
        }

    finally:
        mydb.close()
        tunnel.stop()


def get_categories():
    mydb, tunnel = get_db_connection()

    try:
        category = pd.read_sql("SELECT name AS category FROM hesk_categories", con=mydb)

        return category.to_dict(orient="records")

    finally:
        mydb.close()
        tunnel.stop()


def insert_qna_data(
    question: str, category: str, answer: str, hyperlink: str, tag: str, status: int
):

    mydb, tunnel = get_db_connection()

    try:
        cursor = mydb.cursor()
        sql = "INSERT INTO hesk_chatbot_qna (question, keyword, answer, status) VALUES (%s, %s, %s, %s)"
        val = (question, category, answer, status)
        cursor.execute(sql, val)
        mydb.commit()

        qna_id = cursor.lastrowid

        sql_link = (
            "INSERT INTO hesk_chatbot_link (qna, hyperlink, tag) VALUES (%s, %s, %s)"
        )
        val_link = (qna_id, hyperlink, tag)
        cursor.execute(sql_link, val_link)
        mydb.commit()

        return qna_id

    finally:
        mydb.close()
        tunnel.stop()


def update_qna_data(
    qna_id: int,
    question: str,
    category: str,
    answer: str,
    hyperlink: str,
    tag: str,
    status: int,
):
    mydb, tunnel = get_db_connection()

    try:
        cursor = mydb.cursor()
        sql = "UPDATE hesk_chatbot_qna SET question = %s, keyword = %s, answer = %s, status = %s WHERE id = %s"
        val = (question, category, answer, status, qna_id)
        cursor.execute(sql, val)
        mydb.commit()

        sql_link = (
            "UPDATE hesk_chatbot_link SET hyperlink = %s, tag = %s WHERE qna = %s"
        )
        val_link = (hyperlink, tag, qna_id)
        cursor.execute(sql_link, val_link)
        mydb.commit()

    finally:
        mydb.close()
        tunnel.stop()


def delete_qna_data(qna_id: int):
    mydb, tunnel = get_db_connection()

    try:
        cursor = mydb.cursor()
        sql_link = "DELETE FROM hesk_chatbot_link WHERE qna = %s"
        cursor.execute(sql_link, (qna_id,))
        mydb.commit()

        sql = "DELETE FROM hesk_chatbot_qna WHERE id = %s"
        cursor.execute(sql, (qna_id,))
        mydb.commit()

    finally:
        mydb.close()
        tunnel.stop()
