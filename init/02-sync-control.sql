CREATE TABLE IF NOT EXISTS portalpedido.sync_control (
    processo        VARCHAR(100) PRIMARY KEY,
    ultimo_timestamp BIGINT NOT NULL,
    ultima_execucao  TIMESTAMP,
    atualizado_em   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO portalpedido.sync_control (processo, ultimo_timestamp, ultima_execucao)
SELECT 'analise_pedido_bi', EXTRACT(EPOCH FROM NOW() - INTERVAL '2 days')::BIGINT, NOW()
WHERE NOT EXISTS (SELECT 1 FROM portalpedido.sync_control WHERE processo = 'analise_pedido_bi');

CREATE INDEX IF NOT EXISTS idx_analise_pedido_bi_codigo_cliente
  ON portalpedido.analise_pedido_bi (codigo_cliente);
CREATE INDEX IF NOT EXISTS idx_analise_pedido_bi_numero_pedido
  ON portalpedido.analise_pedido_bi (numero_pedido);
CREATE INDEX IF NOT EXISTS idx_analise_pedido_bi_data_entrega
  ON portalpedido.analise_pedido_bi (data_entrega);
