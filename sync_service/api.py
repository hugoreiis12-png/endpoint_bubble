import json
import time
import requests
from sync_service.config import API_URL, API_KEY, API_RETRIES, API_CONNECT_TIMEOUT, API_READ_TIMEOUT
from sync_service.logger import logger

def buscar_pedidos(timestamp: int) -> list[dict]:
    headers = {
        "Content-Type": "application/json",
        "chave": API_KEY
    }
    payload = {"data": timestamp}
    backoff = [2, 4, 8]

    for tentativa in range(1 + API_RETRIES):
        try:
            resp = requests.post(
                API_URL,
                headers=headers,
                json=payload,
                timeout=(API_CONNECT_TIMEOUT, API_READ_TIMEOUT)
            )
            resp.raise_for_status()
            body = resp.json()

            if body.get("status") != "success":
                logger.warning("API retornou status=%s", body.get("status"))
                return []

            info = body.get("response", {}).get("informações")

            if info is None or info == "" or info == "[]":
                return []

            if isinstance(info, str):
                info = json.loads(info)

            if not isinstance(info, list):
                logger.warning("informações não é uma lista: %s", type(info))
                return []

            logger.info("API retornou %d registros", len(info))
            return info

        except requests.RequestException as e:
            if tentativa < API_RETRIES:
                delay = backoff[tentativa] if tentativa < len(backoff) else 10
                logger.warning(
                    "API falhou (tentativa %d/%d): %s — retry em %ds",
                    tentativa + 1, API_RETRIES, e, delay
                )
                time.sleep(delay)
            else:
                logger.error("API falhou após %d tentativas: %s", API_RETRIES + 1, e)
                raise

    return []
