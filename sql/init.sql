
-- 1. Tabla Maestra de Parques (Dimension)
CREATE TABLE IF NOT EXISTS parks_master (
    park_id VARCHAR(20) PRIMARY KEY,
    park_name VARCHAR(100) NOT NULL,
    capacity_mw DECIMAL(5, 2),
    city VARCHAR(50),
    region VARCHAR(50)
);

-- Insertamos datos semilla (Mock Data) para que no esté vacía
INSERT INTO parks_master (park_id, park_name, capacity_mw, city, region) VALUES
('PARQUE_00', 'Sol del Desierto', 9.00, 'Calama', 'Antofagasta'),
('PARQUE_02', 'Inti Raymi', 5.50, 'Copiapó', 'Atacama');


-- 2. Indicadores Económicos (Contexto)
CREATE TABLE IF NOT EXISTS economic_indicators (
    indicator_date DATE PRIMARY KEY,
    usd_value DECIMAL(10, 2), -- Ej: 950.50
    uf_value DECIMAL(10, 2)   -- Ej: 36000.00
);


-- 3. Logs de Producción (Hechos - Lo que manda Don Pedro)
CREATE TABLE IF NOT EXISTS production_logs (
    log_id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    park_id VARCHAR(20) REFERENCES parks_master(park_id),
    energy_generated_kwh DECIMAL(10, 2),
    irradiation DECIMAL(10, 2), -- W/m2
    comments TEXT,
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);