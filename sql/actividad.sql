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
    servicio_id INT, -- 🔹 Nueva columna para asociar el usuario a un servicio
    creado_en TIMESTAMP DEFAULT NOW(),
    actualizado_en TIMESTAMP DEFAULT NOW(),
    CONSTRAINT fk_servicio FOREIGN KEY (servicio_id) REFERENCES servicio_encargado (id) ON UPDATE CASCADE ON DELETE SET NULL
);

ALTER TABLE users ADD COLUMN google_id VARCHAR(100) UNIQUE NULL;

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
    persona_encargada VARCHAR(150),
    descripcion TEXT,
    activo BOOLEAN DEFAULT TRUE,
    creado_en TIMESTAMP DEFAULT NOW()
);

-- 📋 Servicios encargados
CREATE TABLE IF NOT EXISTS servicio_encargado (
    id SERIAL PRIMARY KEY,
    nombre TEXT NOT NULL UNIQUE,
    descripcion TEXT,
    encargado_servicio VARCHAR(200),
    jefe_inmediato VARCHAR(200),
    activo BOOLEAN DEFAULT TRUE,
    creado_en TIMESTAMP DEFAULT NOW(),
    subdireccion_id INT,
    CONSTRAINT fk_sub FOREIGN KEY (subdireccion_id) REFERENCES subdireccion_perteneciente (id) ON UPDATE CASCADE ON DELETE SET NULL
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

-- Lugares_de_Realizacion
CREATE TABLE IF NOT EXISTS lugares_de_realizacion (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL UNIQUE,
    descripcion VARCHAR(200) NULL
);

CREATE INDEX IF NOT EXISTS idx_lugares_nombre ON lugares_de_realizacion (nombre);

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
    horario_programado TIME NULL,
    lugar_id INTEGER NULL,
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
    a.horario_programado,
    a.lugar_id,
    ldr.nombre AS lugar,
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
    LEFT JOIN meses m2 ON a.mes_id = m2.id
    LEFT JOIN lugares_de_realizacion ldr ON a.lugar_id = ldr.id;

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
    se.id AS servicio_id,
    su.nombre AS subdireccion,
    su.id AS subdireccion_id,
    a.fecha_programada,
    a.horario_programado,
    a.lugar_id,
    ldr.nombre AS lugar,
    m2.nombre AS mes,
    m2.id AS mes_id,
    se.jefe_inmediato AS jefe_inmediato,
    se.encargado_servicio AS encargado_servicio,
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
    LEFT JOIN lugares_de_realizacion ldr ON a.lugar_id = ldr.id
    LEFT JOIN meses m2 ON a.mes_id = m2.id;

-- ==========================================================
-- 🌐 VISTA: vista_ejecucion
-- Descripción: Vista mostrara la cantidad de actividades segun estado, mes y servicio.
-- Incluye información simplificada de fechas, estado, mes y nota.
-- ==========================================================

CREATE OR REPLACE VIEW vista_ejecucion AS
SELECT
    se.id AS servicio_id,
    se.nombre AS servicio_encargado,
    s.id AS subdireccion_id,
    s.nombre AS subdireccion,
    EXTRACT(
        YEAR
        FROM a.fecha_programada
    )::INT AS anio,

-- Conteos por estado
COUNT(*) FILTER (
    WHERE
        e.id = 3
) AS completa,
COUNT(*) FILTER (
    WHERE
        e.id = 1
) AS programada,
COUNT(*) FILTER (
    WHERE
        e.id = 2
) AS reprogramada,
COUNT(*) FILTER (
    WHERE
        e.id = 4
) AS suspendida,

-- Total general
COUNT(*) AS total,

-- Proporción ejecutada 0-1
CASE
    WHEN COUNT(*) = 0 THEN 0
    ELSE (
        COUNT(*) FILTER (
            WHERE
                e.id = 3
        )
    )::numeric / COUNT(*)
END AS ejecutado
FROM
    actividades a
    LEFT JOIN servicio_encargado se ON a.servicio_id = se.id
    LEFT JOIN subdireccion_perteneciente s ON se.subdireccion_id = s.id
    LEFT JOIN estado e ON a.estado_id = e.id
WHERE
    a.fecha_programada IS NOT NULL
GROUP BY
    se.id,
    se.nombre,
    s.id,
    s.nombre,
    anio
ORDER BY anio DESC, s.id ASC, se.id ASC;

CREATE OR REPLACE VIEW resumen_anual AS
SELECT
    EXTRACT(
        YEAR
        FROM a.fecha_programada
    )::INT AS anio,
    COUNT(*) FILTER (
        WHERE
            a.estado_id = 1
    ) AS programadas,
    COUNT(*) FILTER (
        WHERE
            a.estado_id = 2
    ) AS reprogramadas,
    COUNT(*) FILTER (
        WHERE
            a.estado_id = 3
    ) AS completadas,
    COUNT(*) FILTER (
        WHERE
            a.estado_id = 4
    ) AS anuladas,
    COUNT(*) AS total
FROM actividades a
GROUP BY
    anio
ORDER BY anio DESC;

-- ==========================================
-- TABLA: sexo
-- ==========================================
CREATE TABLE sexo (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(20) UNIQUE NOT NULL
);

-- ==========================================
-- TABLA: grupo_edad
-- ==========================================
CREATE TABLE grupo_edad (
    id SERIAL PRIMARY KEY,
    rango VARCHAR(50) UNIQUE NOT NULL
);

-- ==========================================
-- TABLA: pertenencia_cultural
-- ==========================================
CREATE TABLE pertenencia_cultural (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) UNIQUE NOT NULL
);

-- ==========================================
-- TABLA: asistencia
-- ==========================================
CREATE TABLE asistencia (
    id SERIAL PRIMARY KEY,
    nombre_completo VARCHAR(150) NOT NULL,
    sexo_id INT REFERENCES sexo (id) ON DELETE SET NULL,
    grupo_edad_id INT REFERENCES grupo_edad (id) ON DELETE SET NULL,
    cui BIGINT,
    puesto_funcional VARCHAR(100),
    pertenencia_cultural_id INT REFERENCES pertenencia_cultural (id) ON DELETE SET NULL,
    telefono_email VARCHAR(150),
    datos_extras JSONB,
    capacitacion_id INT NOT NULL REFERENCES actividades (id) ON DELETE CASCADE,
    fecha_registro TIMESTAMP DEFAULT NOW()
);