import signal
import sys
import time
from sync_service.database import init_pool, close_pool
from sync_service.sync import executar_sincronizacao
from sync_service.config import SYNC_INTERVAL
from sync_service.logger import logger

running = True


def _signal_handler(sig, frame):
    global running
    logger.info("Sinal recebido, encerrando...")
    running = False


signal.signal(signal.SIGTERM, _signal_handler)
signal.signal(signal.SIGINT, _signal_handler)


def main():
    logger.info("=== SYNC SERVICE INICIADO ===")
    logger.info("Intervalo de sincronização: %ds", SYNC_INTERVAL)

    try:
        init_pool()
    except Exception as e:
        logger.critical("Falha ao inicializar pool de conexões: %s", e)
        sys.exit(1)

    try:
        while running:
            executar_sincronizacao()
            if not running:
                break
            logger.info("Aguardando %d segundos...", SYNC_INTERVAL)
            time.sleep(SYNC_INTERVAL)
    finally:
        close_pool()
        logger.info("=== SYNC SERVICE ENCERRADO ===")


if __name__ == "__main__":
    main()
