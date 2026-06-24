import os
import psycopg2

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "192.168.0.142"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "dbname": os.getenv("DB_NAME", "COMPROVE-API-JS"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "postgres")
}

conn = psycopg2.connect(**DB_CONFIG)
cur = conn.cursor()
cur.execute("SELECT * FROM portalpedido.analise_pedido_bi ORDER BY data_entrega DESC")

colunas = [desc[0] for desc in cur.description]
print(" | ".join(colunas))
print("-" * 100)
for row in cur.fetchall():
    print(" | ".join(str(v) for v in row))

cur.close()
conn.close()
