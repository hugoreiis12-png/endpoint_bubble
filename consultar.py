import psycopg2

DB_CONFIG = {
    "host": "192.168.0.142",
    "port": 5432,
    "dbname": "COMPROVE-API-JS",
    "user": "postgres",
    "password": "postgres"
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
