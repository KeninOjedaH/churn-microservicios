import os
import sqlite3
from dotenv import load_dotenv

load_dotenv()

DATABASE_PATH = os.path.join(os.path.dirname(__file__), "database.db")


async def create_transaction(phone_number: str, message_type: str, message_content: str):
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO message_transactions (phone_number, message_type, message_content, status)
            VALUES (?, ?, ?, ?)
            """,
            (phone_number, message_type, message_content, "pendiente"),
        )
        conn.commit()
        transaction_id = cur.lastrowid
        cur.close()
        conn.close()
        return transaction_id
    except Exception as e:
        print(f"Error al crear la transacción: {e}")
        raise

async def update_transaction_status(transaction_id: int, status: str, error_message: str = None):
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cur = conn.cursor()

        if error_message:
            cur.execute(
                """
                UPDATE message_transactions
                SET status = ?, error_message = ?
                WHERE id = ?;
                """,
                (status, error_message, transaction_id),
            )
        else:
            cur.execute(
                """
                UPDATE message_transactions
                SET status = ?
                WHERE id = ?;
                """,
                (status, transaction_id),
            )

        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error al actualizar la transacción: {e}")
        raise

# You'll need to create the message_transactions table in your SQLite database
# Example SQL:
# CREATE TABLE message_transactions (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     phone_number TEXT,
#     message_type TEXT,
#     message_content TEXT,
#     status TEXT,
#     transaction_id TEXT,
#     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     error_message TEXT
# );
