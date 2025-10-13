-- =========================================================
-- TABLAS PRINCIPALES
-- =========================================================

-- =========================================================
-- POBLADO INICIAL PARA USUARIOS
-- =========================================================
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,
    estado CHAR(1),
    creado_en TIMESTAMP DEFAULT NOW(),
    actualizado_en TIMESTAMP DEFAULT NOW()
);

INSERT INTO
    users (
        id,
        nombre,
        username,
        email,
        password,
        role,
        estado,
        creado_en,
        actualizado_en
    )
VALUES (
        1,
        'Administrador',
        'admin',
        'chaknogf@gmail.com',
        '$2b$12$dUC2UVF0m2qtXZbMafs8TuSw4cjWZJvQtA9r/OG8jNDdzEov85Ghm',
        'admin',
        'A',
        NOW(),
        NOW()
    );

-- 📋 Subdirecciones
CREATE TABLE IF NOT EXISTS subdireccion_perteneciente (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(80) NOT NULL UNIQUE,
    descripcion TEXT,
    activo BOOLEAN DEFAULT TRUE,
    creado_en TIMESTAMP DEFAULT NOW()
);

-- 📋 Servicios encargados
CREATE TABLE IF NOT EXISTS servicio_encargado (
    id SERIAL PRIMARY KEY,
    nombre TEXT NOT NULL UNIQUE,
    descripcion TEXT,
    activo BOOLEAN DEFAULT TRUE,
    creado_en TIMESTAMP DEFAULT NOW(),
    subdireccion_id INTEGER REFERENCES subdireccion_perteneciente (id) ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_servicio_subdireccion_id ON servicio_encargado (subdireccion_id);

-- 📋 Actividad catálogo
CREATE TABLE IF NOT EXISTS actividad (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    activo BOOLEAN DEFAULT TRUE NOT NULL
);

-- 📋 Modalidad
CREATE TABLE IF NOT EXISTS modalidad (
    id SERIAL PRIMARY KEY,
    codigo CHAR(1) UNIQUE NOT NULL,
    nombre VARCHAR(50) NOT NULL
);

-- 📋 Estado
CREATE TABLE IF NOT EXISTS estado (
    id SERIAL PRIMARY KEY,
    codigo CHAR(1) UNIQUE NOT NULL,
    nombre VARCHAR(50) NOT NULL
);

-- 📅 Meses
CREATE TABLE IF NOT EXISTS meses (
    id SERIAL PRIMARY KEY, -- 1 a 12
    nombre VARCHAR(20) NOT NULL UNIQUE
);

INSERT INTO
    meses (id, nombre)
VALUES (1, 'Enero'),
    (2, 'Febrero'),
    (3, 'Marzo'),
    (4, 'Abril'),
    (5, 'Mayo'),
    (6, 'Junio'),
    (7, 'Julio'),
    (8, 'Agosto'),
    (9, 'Septiembre'),
    (10, 'Octubre'),
    (11, 'Noviembre'),
    (12, 'Diciembre')
ON CONFLICT (id) DO NOTHING;

-- 📋 Actividades
CREATE TABLE IF NOT EXISTS actividades (
    id SERIAL PRIMARY KEY,
    tema TEXT NOT NULL,
    actividad_id INTEGER REFERENCES actividad (id) ON UPDATE CASCADE ON DELETE SET NULL,
    subdireccion_id INTEGER REFERENCES subdireccion_perteneciente (id) ON UPDATE CASCADE ON DELETE SET NULL,
    servicio_id INTEGER REFERENCES servicio_encargado (id) ON UPDATE CASCADE ON DELETE SET NULL,
    persona_responsable JSONB,
    tiempo_aproximado VARCHAR(50),
    fecha_programada DATE,
    modalidad_id INTEGER REFERENCES modalidad (id) ON UPDATE CASCADE ON DELETE SET NULL,
    estado_id INTEGER REFERENCES estado (id) ON UPDATE CASCADE ON DELETE SET NULL,
    detalles JSONB,
    metadatos JSONB,
    mes_id INTEGER REFERENCES meses (id) ON UPDATE CASCADE ON DELETE SET NULL
);

-- ==========================================================
-- 🌐 VISTA: vista_actividades_completa
-- Descripción: Combina toda la información relevante de actividades
-- Incluye nombres descriptivos, relaciones, mes y año derivado de la fecha programada.
-- ==========================================================

CREATE OR REPLACE VIEW vista_actividades_completa AS
SELECT
    a.id,
    a.tema,
    act.nombre AS actividad,
    act.id AS actividad_id,
    act.descripcion AS descripcion_actividad,
    s.nombre AS subdireccion,
    a.subdireccion_id,
    se.nombre AS servicio_encargado,
    a.servicio_id,
    a.persona_responsable,
    a.tiempo_aproximado,
    a.fecha_programada,
    m2.id AS mes_id,
    m2.nombre AS mes,
    EXTRACT(
        YEAR
        FROM a.fecha_programada
    )::INT AS anio,
    mo.nombre AS modalidad,
    a.modalidad_id,
    e.nombre AS estado,
    a.estado_id,
    a.detalles,
    a.metadatos
FROM
    actividades a
    LEFT JOIN actividad act ON a.actividad_id = act.id
    LEFT JOIN servicio_encargado se ON a.servicio_id = se.id
    LEFT JOIN subdireccion_perteneciente s ON se.subdireccion_id = s.id
    LEFT JOIN modalidad mo ON a.modalidad_id = mo.id
    LEFT JOIN estado e ON a.estado_id = e.id
    LEFT JOIN meses m2 ON a.mes_id = m2.id;

-- ==========================================================
-- 🌐 VISTA: vista_reporte
-- Descripción: Vista resumida orientada a reportes y tableros.
-- Incluye información simplificada de fechas, estado, mes y nota.
-- ==========================================================

CREATE OR REPLACE VIEW vista_reporte AS
SELECT
    a.id,
    a.tema,
    act.nombre AS actividad,
    se.nombre AS servicio_encargado,
    su.nombre AS subdireccion,
    a.fecha_programada,
    m2.nombre AS mes,
    m2.id AS mes_id,
    EXTRACT(
        YEAR
        FROM a.fecha_programada
    )::INT AS anio,
    mo.nombre AS modalidad,
    e.nombre AS estado,
    COALESCE(a.detalles ->> 'nota', '') AS nota
FROM
    actividades a
    LEFT JOIN actividad act ON a.actividad_id = act.id
    LEFT JOIN servicio_encargado se ON a.servicio_id = se.id
    LEFT JOIN subdireccion_perteneciente su ON se.subdireccion_id = su.id
    LEFT JOIN modalidad mo ON a.modalidad_id = mo.id
    LEFT JOIN estado e ON a.estado_id = e.id
    LEFT JOIN meses m2 ON a.mes_id = m2.id;

-- ==========================================================
-- 🌐 VISTA: vista_ejecucion
-- Descripción: Vista mostrara la cantidad de actividades segun estado, mes y servicio.
-- Incluye información simplificada de fechas, estado, mes y nota.
-- ==========================================================

CREATE OR REPLACE VIEW vista_ejecucion AS
SELECT
    s.id AS subdireccion_id,
    s.nombre AS subdireccion,
    se.id AS servicio_id,
    se.nombre AS servicio_encargado,
    m.id AS mes_id,
    m.nombre AS mes,
    EXTRACT(
        YEAR
        FROM a.fecha_programada
    )::INT AS anio,

-- Conteo por estado
COUNT(*) FILTER (
    WHERE
        e.nombre ILIKE '%completa%'
) AS completa,
COUNT(*) FILTER (
    WHERE
        e.nombre ILIKE '%programada%'
) AS programada,
COUNT(*) FILTER (
    WHERE
        e.nombre ILIKE '%reprogramada%'
) AS reprogramada,
COUNT(*) FILTER (
    WHERE
        e.nombre ILIKE '%anulada%'
) AS anulada,

-- Total de todas
COUNT(*) AS total
FROM
    actividades a
    LEFT JOIN subdireccion_perteneciente s ON a.subdireccion_id = s.id
    LEFT JOIN servicio_encargado se ON a.servicio_id = se.id
    LEFT JOIN meses m ON a.mes_id = m.id
    LEFT JOIN estado e ON a.estado_id = e.id
WHERE
    a.mes_id IS NOT NULL
GROUP BY
    s.id,
    s.nombre,
    se.id,
    se.nombre,
    m.id,
    m.nombre,
    anio
ORDER BY anio DESC, mes_id ASC, s.id ASC, se.id ASC;