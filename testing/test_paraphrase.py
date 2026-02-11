import pandas as pd

from database.connection import get_db_connection
from src.qa_engine import get_answer

SIMILARITY_THRESHOLD = 85

# =========================
# CONNECT DB
# =========================
mydb, tunnel = get_db_connection()

query = pd.read_sql(
    "SELECT qna_id, paraphrase FROM hesk_chatbot_qna_paraphrase",
    con=mydb,
)

results = []

for _, row in query.iterrows():
    paraphrase = row["paraphrase"]
    expected_qna_id = row["qna_id"]

    response = get_answer(paraphrase, testing=True)

    if response["Status"] == "known":
        predicted_qna_id = response["ID"]
        is_match = predicted_qna_id == expected_qna_id
    else:
        predicted_qna_id = None
        is_match = False

    results.append(
        {
            "paraphrase": paraphrase,
            "expected_qna_id": expected_qna_id,
            "predicted_qna_id": predicted_qna_id,
            "match": is_match,
        }
    )

result_df = pd.DataFrame(results)

# =========================
# SAVE TO EXCEL
# =========================
output_file = "testing/result/paraphrase_test_result.xlsx"

with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
    result_df.to_excel(writer, sheet_name="Detail Result", index=False)

    summary_df = pd.DataFrame(
        {
            "Total Data": [len(result_df)],
            "Total Match": [result_df["match"].sum()],
            "Total Mismatch": [len(result_df) - result_df["match"].sum()],
            "Accuracy": [result_df["match"].mean()],
        }
    )

    summary_df.to_excel(writer, sheet_name="Summary", index=False)

print(f"\nFile berhasil disimpan sebagai: {output_file}")
