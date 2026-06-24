CREATE SCHEMA IF NOT EXISTS portalpedido;

CREATE TABLE IF NOT EXISTS portalpedido.analise_pedido_bi (
    api_id          TEXT PRIMARY KEY,
    data_entrega    DATE,
    codigo_cliente  TEXT,
    latitude        DOUBLE PRECISION,
    longitude       DOUBLE PRECISION,
    numero_pedido   TEXT,
    pedido_sap      TEXT,
    via_portal      BOOLEAN DEFAULT FALSE,
    via_whatsapp    BOOLEAN DEFAULT FALSE,
    atualizado_em   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
