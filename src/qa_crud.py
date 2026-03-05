import mysql.connector
import pandas as pd
from fastapi import HTTPException

from database.connection import get_read_connection, get_write_connection


def get_qna_data(page: int = 1, limit: int = 10):
    conn = get_read_connection()

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
            con=conn,
        )

        total = pd.read_sql(
            "SELECT COUNT(*) as count FROM hesk_chatbot_qna",
            con=conn,
        )

        return {
            "data": data.to_dict(orient="records"),
            "total": int(total["count"][0]),
            "page": page,
            "limit": limit,
        }

    finally:
        conn.close()


def get_categories():
    conn = get_read_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT name AS category FROM hesk_categories")
    result = cursor.fetchall()

    cursor.close()
    conn.close()

    return result


def insert_qna_data(
    question: str, category: str, answer: str, hyperlink: str, tag: str, status: str
):

    conn = get_write_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id FROM hesk_categories WHERE name = %s", (category,))
        join = cursor.fetchone()
        if not join:
            raise HTTPException(status_code=400, detail="Category does not exist")

        category_id = join[0]

        sql = "INSERT INTO hesk_chatbot_qna (category, keyword, question, answer, status) VALUES (%s, %s, %s, %s, %s)"
        val = (
            category_id,
            category,
            question,
            answer,
            status,
        )
        cursor.execute(sql, val)
        conn.commit()

        qna_id = cursor.lastrowid

        if hyperlink and tag:
            sql_link = "INSERT INTO hesk_chatbot_link (category, qna, hyperlink, tag) VALUES (%s, %s, %s, %s)"
            val_link = (category_id, qna_id, hyperlink, tag)
            cursor.execute(sql_link, val_link)
            conn.commit()

            return qna_id

    except mysql.connector.errors.IntegrityError:
        raise HTTPException(status_code=400, detail="Question already exists")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        cursor.close()
        conn.close()


def update_qna_data(
    qna_id: int,
    question: str,
    category: str,
    answer: str,
    hyperlink: str,
    tag: str,
    status: int,
):
    conn = get_write_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id FROM hesk_categories WHERE name = %s", (category,))
        join = cursor.fetchone()
        if not join:
            raise HTTPException(status_code=400, detail="Category does not exist")

        cursor.execute("SELECT id FROM hesk_chatbot_link WHERE qna = %s", (qna_id,))

        check_id = cursor.fetchone()
        category_id = join[0]

        sql = "UPDATE hesk_chatbot_qna SET category = %s, keyword = %s, question = %s, answer = %s, status = %s WHERE id = %s"
        val = (category_id, category, question, answer, status, qna_id)
        cursor.execute(sql, val)
        conn.commit()

        if not check_id:
            sql_link = "INSERT INTO hesk_chatbot_link (category, qna, hyperlink, tag) VALUES (%s, %s, %s, %s)"
            val_link = (category_id, qna_id, hyperlink, tag)
            cursor.execute(sql_link, val_link)
            conn.commit()
        else:
            sql_link = "UPDATE hesk_chatbot_link SET category = %s, hyperlink = %s, tag = %s WHERE qna = %s"
            val_link = (category_id, hyperlink, tag, qna_id)
            cursor.execute(sql_link, val_link)
            conn.commit()

    finally:
        cursor.close()
        conn.close()


def delete_qna_data(qna_id: int):
    conn = get_write_connection()
    cursor = conn.cursor()

    try:
        sql_link = "DELETE FROM hesk_chatbot_link WHERE qna = %s"
        cursor.execute(sql_link, (qna_id,))
        conn.commit()

        sql = "DELETE FROM hesk_chatbot_qna WHERE id = %s"
        cursor.execute(sql, (qna_id,))
        conn.commit()

    finally:
        cursor.close()
        conn.close()


def delete_qna_bulk(qna_ids: list):
    conn = get_write_connection()
    cursor = conn.cursor()

    try:
        format_strings = ",".join(["%s"] * len(qna_ids))

        sql_link = f"DELETE FROM hesk_chatbot_link WHERE qna IN ({format_strings})"
        cursor.execute(sql_link, tuple(qna_ids))
        conn.commit()

        sql = f"DELETE FROM hesk_chatbot_qna WHERE id IN ({format_strings})"
        cursor.execute(sql, tuple(qna_ids))
        conn.commit()

    finally:
        cursor.close()
        conn.close()
