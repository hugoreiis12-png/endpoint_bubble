import json
import os
import time
import requests
import psycopg2
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "192.168.0.142"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "dbname": os.getenv("DB_NAME", "COMPROVE-API-JS"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "postgres")
}

URL = os.getenv("API_URL", "https://comprover.bubbleapps.io/version-test/api/1.1/wf/analise_de_pedidobi")
HEADERS = {
    "Content-Type": "application/json",
    "chave": os.getenv("API_KEY", "hgd5h4d5f64j65fgh4k56fj465dfg4h56dt465ryt4j56y4j65ytr4j65yt4")
}

BR = ZoneInfo("America/Sao_Paulo")

def buscar_e_salvar(data_alvo):
    ts = int(data_alvo.timestamp())
    try:
        resp = requests.post(URL, headers=HEADERS, json={"data": ts}, timeout=30)
        resp.raise_for_status()
        dados = json.loads(resp.json()["response"]["informações"])
    except requests.RequestException as e:
        print(f"  ERRO API {data_alvo}: {e}")
        return -1
    except (KeyError, json.JSONDecodeError, TypeError) as e:
        print(f"  ERRO resposta API {data_alvo}: {e}")
        return -1

    if not dados:
        return 0

    try:
        conn = psycopg2.connect(**DB_CONFIG, connect_timeout=10)
        cur = conn.cursor()
        for item in dados:
            cur.execute("""
                INSERT INTO portalpedido.analise_pedido_bi
                    (api_id, data_entrega, codigo_cliente, latitude, longitude,
                     numero_pedido, pedido_sap, via_portal, via_whatsapp)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (api_id) DO UPDATE SET
                    data_entrega = EXCLUDED.data_entrega,
                    codigo_cliente = EXCLUDED.codigo_cliente,
                    latitude = EXCLUDED.latitude,
                    longitude = EXCLUDED.longitude,
                    numero_pedido = EXCLUDED.numero_pedido,
                    pedido_sap = EXCLUDED.pedido_sap,
                    via_portal = EXCLUDED.via_portal,
                    via_whatsapp = EXCLUDED.via_whatsapp,
                    atualizado_em = CURRENT_TIMESTAMP
            """, (
                item["id"], item["data de entrega"], item["codigo_cliente"],
                item["latitude"], item["longitude"], item["numero_pedido"],
                item["pedido_sap"], item["via_portal"], item["via_whatsapp"]
            ))
        conn.commit()
        cur.close()
        conn.close()
        return len(dados)
    except psycopg2.Error as e:
        print(f"  ERRO BD {data_alvo}: {e}")
        return -1

agora = datetime.now(BR)
inicio = agora.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)

# --- CARGA INICIAL: desde ontem 00:00 até agora, a cada 6h ---
total = 0
print("=== CARGA INICIAL: desde ontem 00:00 ===")
proxima = inicio
while proxima <= agora:
    qtd = buscar_e_salvar(proxima)
    if qtd > 0:
        print(f"  {proxima}: {qtd} registros")
        total += qtd
    proxima += timedelta(hours=6)
print(f"Carga inicial concluída: {total} registros inseridos")

# --- LOOP CONTÍNUO: de 6 em 6h ---
print("=== LOOP CONTÍNUO: atualizando a cada 6h ===")
proxima = agora.replace(minute=0, second=0, microsecond=0)
proxima += timedelta(hours=((proxima.hour // 6) + 1) * 6 - proxima.hour)

while True:
    qtd = buscar_e_salvar(proxima)
    if qtd >= 0:
        print(f"{datetime.now(BR)} | {proxima} — {qtd} registros sincronizados")
    else:
        print(f"{datetime.now(BR)} | {proxima} — FALHA na sincronização")
    print(f"Próxima execução em 6h: {proxima + timedelta(hours=6)}")
    proxima += timedelta(hours=6)
    time.sleep(21600)
