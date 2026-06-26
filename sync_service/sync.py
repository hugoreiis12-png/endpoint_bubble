import time
from datetime import datetime
from zoneinfo import ZoneInfo
from sync_service.api import buscar_pedidos
from sync_service.database import (
    get_conn, put_conn, upsert_lote,
    ler_ultimo_timestamp, atualizar_timestamp
)
from sync_service.logger import logger

BR = ZoneInfo("America/Sao_Paulo")


def executar_sincronizacao():
    conn = get_conn()
    inicio = time.time()

    try:
        ts = ler_ultimo_timestamp(conn)
        agora = datetime.now(BR)
        hoje_meia_noite = int(agora.replace(
            hour=0, minute=0, second=0, microsecond=0
        ).timestamp())

        if ts is None:
            ts = hoje_meia_noite
            logger.info(
                "Primeira execução — timestamp inicial: %d",
                ts
            )

        logger.info("Sincronizando a partir do timestamp %d...", ts)
        dados = buscar_pedidos(ts)

        if not dados:
            duracao = time.time() - inicio
            logger.info(
                "Nenhum registro — timestamp=%d | tempo=%.2fs",
                ts, duracao
            )
        else:
            inseridos, atualizados = upsert_lote(conn, dados)
            duracao = time.time() - inicio
            logger.info(
                "API retornou %d | inseridos %d | tempo=%.2fs | timestamp=%d",
                len(dados), inseridos, duracao, ts
            )

        atualizar_timestamp(conn, hoje_meia_noite)

    except Exception:
        logger.exception("Erro na sincronização")
        if conn:
            conn.rollback()
    finally:
        if conn:
            put_conn(conn)
