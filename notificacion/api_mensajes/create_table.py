import os
import sqlite3
from dotenv import load_dotenv

load_dotenv()

DATABASE_PATH = os.path.join(os.path.dirname(__file__), "database.db")

try:
    conn = sqlite3.connect(DATABASE_PATH)
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS message_transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone_number TEXT,
            message_type TEXT,
            message_content TEXT,
            status TEXT,
            transaction_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            error_message TEXT
        );
        """
    )

    conn.commit()
    print("Tabla 'message_transactions' creada exitosamente.")

    cur.close()
    conn.close()

except Exception as e:
    print(f"Error al crear la tabla: {e}")
