import mysql.connector
import pandas as pd
from fastapi import HTTPException

from database.connection import get_read_connection, get_write_connection


def get_qna_data(page: int = 1, limit: int = 10):
    conn = get_read_connection()

    try:
        offset = (page - 1) * limit

        data_qna = pd.read_sql(
            f"""
            SELECT ID AS id,
                    question AS question,
                    keyword AS category,
                    answer AS answer,
                    status AS status
            FROM hesk_chatbot_qna
            ORDER BY id ASC
            LIMIT {limit} OFFSET {offset}
            """,
            con=conn,
        )

        #  GET QNA ID
        qna_ids = data_qna["id"].tolist()

        if not qna_ids:
            return {
                "data": [],
                "total": 0,
                "page": page,
                "limit": limit,
            }

        data_link = pd.read_sql(
            f"""        
            SELECT id AS id_link,
                qna AS qna,
                hyperlink AS hyperlink,
                tag AS tag
            FROM hesk_chatbot_link
            WHERE qna IN ({",".join(map(str, qna_ids))})
            """,
            con=conn,
        )

        # group links by qna
        links_grouped = {}

        for _, row in data_link.iterrows():
            qna_id = row["qna"]

            if qna_id not in links_grouped:
                links_grouped[qna_id] = []

            links_grouped[qna_id].append(
                {"id": row["id_link"], "hyperlink": row["hyperlink"], "tag": row["tag"]}
            )

        # MERGE QNA AND LINKS DATA
        final_data = []

        for _, row in data_qna.iterrows():
            qna_id = row["id"]

            final_data.append(
                {
                    "id": qna_id,
                    "question": row["question"],
                    "category": row["category"],
                    "answer": row["answer"],
                    "status": row["status"],
                    "links": links_grouped.get(qna_id, []),
                }
            )

        total = pd.read_sql(
            "SELECT COUNT(*) as count FROM hesk_chatbot_qna",
            con=conn,
        )

        return {
            "data": final_data,
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
    question: str, category: str, answer: str, links: list, status: str
):

    conn = get_write_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id FROM hesk_categories WHERE name = %s", (category,))
        join = cursor.fetchone()
        if not join:
            raise HTTPException(status_code=400, detail="Category does not exist")

        category_id = join[0]

        sql = (
            "INSERT INTO hesk_chatbot_qna "
            "(category, keyword, question, answer, status) "
            "VALUES (%s, %s, %s, %s, %s)"
        )
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

        if links:
            for link in links:
                if not link.get("hyperlink") or not link.get("tag"):
                    continue

                sql_link = (
                    "INSERT INTO hesk_chatbot_link "
                    "(category, qna, hyperlink, tag) "
                    "VALUES (%s, %s, %s, %s)"
                )
                val_link = (category_id, qna_id, link.get("hyperlink"), link.get("tag"))
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
    links: list,
    status: int,
):
    conn = get_write_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id FROM hesk_categories WHERE name = %s", (category,))
        join = cursor.fetchone()
        if not join:
            raise HTTPException(status_code=400, detail="Category does not exist")

        category_id = join[0]

        cursor.execute("SELECT id FROM hesk_chatbot_link WHERE qna = %s", (qna_id,))

        existing_link = cursor.fetchall()

        existing_ids = {row[0] for row in existing_link}

        incoming_ids = {link["id"] for link in links if link.get("id")}

        deleted_ids = existing_ids - incoming_ids

        # delete link yg dihapus
        for link_id in deleted_ids:
            cursor.execute("DELETE FROM hesk_chatbot_link WHERE id = %s", (link_id,))

        # update qna
        sql = (
            "UPDATE hesk_chatbot_qna SET category = %s, keyword = %s, "
            "question = %s, answer = %s, status = %s, updated_at = NOW()"
            " WHERE id = %s"
        )

        val = (category_id, category, question, answer, status, qna_id)
        cursor.execute(sql, val)

        # update / insert links
        for link in links:
            # skip kalau hyperlink kosong
            if not link.get("hyperlink"):
                continue

            if link.get("id"):
                # UPDATE existing link
                sql_link = (
                    "UPDATE hesk_chatbot_link "
                    "SET hyperlink = %s, tag = %s "
                    "WHERE id = %s"
                )

                val_link = (link["hyperlink"], link.get("tag"), link["id"])

                cursor.execute(sql_link, val_link)

            else:
                # INSERT new link
                sql_link = (
                    "INSERT INTO hesk_chatbot_link "
                    "(category, qna, hyperlink, tag) "
                    "VALUES (%s, %s, %s, %s)"
                )

                val_link = (category_id, qna_id, link["hyperlink"], link.get("tag"))

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
