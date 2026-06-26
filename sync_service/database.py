from psycopg2 import pool, extras
from sync_service.config import (
    DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD,
    DB_POOL_MIN, DB_POOL_MAX
)
from sync_service.logger import logger

_pool = None

COLUNAS = [
    "api_id", "data_entrega", "codigo_cliente", "latitude",
    "longitude", "numero_pedido", "pedido_sap", "via_portal", "via_whatsapp"
]

INSERT_SQL = """
    INSERT INTO portalpedido.analise_pedido_bi ({})
    VALUES %s
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
""".format(", ".join(COLUNAS))

SYNC_SELECT = """
    SELECT ultimo_timestamp FROM portalpedido.sync_control
    WHERE processo = 'analise_pedido_bi'
"""

SYNC_UPSERT = """
    INSERT INTO portalpedido.sync_control (processo, ultimo_timestamp, ultima_execucao)
    VALUES ('analise_pedido_bi', %s, NOW())
    ON CONFLICT (processo) DO UPDATE SET
        ultimo_timestamp = EXCLUDED.ultimo_timestamp,
        ultima_execucao = NOW(),
        atualizado_em = CURRENT_TIMESTAMP
"""


def init_pool():
    global _pool
    dsn = (
        f"host={DB_HOST} port={DB_PORT} "
        f"dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD}"
    )
    _pool = pool.SimpleConnectionPool(DB_POOL_MIN, DB_POOL_MAX, dsn)
    logger.info("Pool de conexões inicializado (min=%d, max=%d)", DB_POOL_MIN, DB_POOL_MAX)


def close_pool():
    global _pool
    if _pool:
        _pool.closeall()
        _pool = None
        logger.info("Pool de conexões fechado")


def get_conn():
    return _pool.getconn()


def put_conn(conn):
    _pool.putconn(conn)


def ler_ultimo_timestamp(conn) -> int | None:
    cur = conn.cursor()
    cur.execute(SYNC_SELECT)
    row = cur.fetchone()
    cur.close()
    return row[0] if row else None


def atualizar_timestamp(conn, timestamp: int):
    cur = conn.cursor()
    cur.execute(SYNC_UPSERT, (timestamp,))
    conn.commit()
    cur.close()
    logger.info("Timestamp atualizado para %d", timestamp)


def upsert_lote(conn, dados: list[dict]) -> tuple[int, int]:
    if not dados:
        return 0, 0

    registros = []
    for item in dados:
        registros.append((
            item.get("id", ""),
            item.get("data de entrega"),
            item.get("codigo_cliente"),
            _float_safe(item.get("latitude")),
            _float_safe(item.get("longitude")),
            item.get("numero_pedido"),
            item.get("pedido_sap") or None,
            _bool_safe(item.get("via_portal")),
            _bool_safe(item.get("via_whatsapp")),
        ))

    cur = conn.cursor()
    extras.execute_values(cur, INSERT_SQL, registros, page_size=500)
    conn.commit()
    cur.close()

    return len(registros), 0


def _float_safe(val) -> float | None:
    if val is None:
        return None
    try:
        return float(str(val).replace(",", "."))
    except (ValueError, TypeError):
        return None


def _bool_safe(val) -> bool:
    if val is None:
        return False
    return str(val).strip().lower() in ("sim", "true", "1", "s", "yes", "y", "x")
