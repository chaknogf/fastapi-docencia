CREATE TABLE IF NOT EXISTS actividades (
    id SERIAL PRIMARY KEY,
    tema TEXT NOT NULL,
    actividad_id INTEGER NOT NULL REFERENCES actividad (id) ON DELETE CASCADE,
    subdireccion_id INTEGER NOT NULL REFERENCES subdireccion_perteneciente (id) ON DELETE CASCADE,
    servicio_id INTEGER NOT NULL REFERENCES servicio_encargado (id) ON DELETE CASCADE,
    persona_responsable JSONB,
    tiempo_aproximado VARCHAR(50),
    fechas_a_desarrollar VARCHAR(50),
    modalidad_id INTEGER NOT NULL REFERENCES modalidad (id) ON DELETE CASCADE,
    estado_id INTEGER NOT NULL REFERENCES estado (id) ON DELETE CASCADE,
    detalles JSONB,
    metadatos JSONB
);

CREATE TABLE IF NOT EXISTS subdireccion_perteneciente (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(80) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS servicio_encargado (
    id SERIAL PRIMARY KEY,
    nombre TEXT NOT NULL UNIQUE
);

INSERT INTO
    subdireccion_perteneciente (nombre)
SELECT DISTINCT
    subdireccion_perteneciente
FROM actividades
WHERE
    subdireccion_perteneciente IS NOT NULL;

INSERT INTO
    servicio_encargado (nombre)
SELECT DISTINCT
    servicio_encargado
FROM actividades
WHERE
    servicio_encargado IS NOT NULL;

ALTER TABLE actividades ADD COLUMN subdireccion_id INTEGER;

ALTER TABLE actividades ADD COLUMN servicio_id INTEGER;

UPDATE actividades a
SET
    subdireccion_id = s.id
FROM subdireccion_perteneciente s
WHERE
    a.subdireccion_perteneciente = s.nombre;

UPDATE actividades a
SET
    servicio_id = s.id
FROM servicio_encargado s
WHERE
    a.servicio_encargado = s.nombre;

-- (Opcional pero recomendable) Crear las llaves foráneas
ALTER TABLE actividades
ADD CONSTRAINT fk_subdireccion FOREIGN KEY (subdireccion_id) REFERENCES subdireccion_perteneciente (id);

ALTER TABLE actividades
ADD CONSTRAINT fk_servicio FOREIGN KEY (servicio_id) REFERENCES servicio_encargado (id);

ALTER TABLE subdireccion_perteneciente
ADD COLUMN descripcion TEXT,
ADD COLUMN activo BOOLEAN DEFAULT TRUE,
ADD COLUMN creado_en TIMESTAMP DEFAULT NOW();

ALTER TABLE servicio_encargado
ADD COLUMN descripcion TEXT,
ADD COLUMN activo BOOLEAN DEFAULT TRUE,
ADD COLUMN creado_en TIMESTAMP DEFAULT NOW();

CREATE TABLE IF NOT EXISTS subdireccion_perteneciente (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(80) NOT NULL,
    descripcion TEXT,
    activo BOOLEAN DEFAULT TRUE,
    creado_en TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS servicio_encargado (
    id SERIAL PRIMARY KEY,
    nombre TEXT NOT NULL,
    descripcion TEXT,
    activo BOOLEAN DEFAULT TRUE,
    creado_en TIMESTAMP DEFAULT NOW()
);

ALTER TABLE actividades DROP COLUMN servicio_encargado;

CREATE OR REPLACE VIEW vista_actividades_completa AS
SELECT
    a.id,
    a.tema,
    act.nombre AS actividad, -- Nombre de la actividad desde la tabla actividad
    act.descripcion AS descripcion_actividad, -- Descripción opcional de la actividad
    s.nombre AS subdireccion,
    se.nombre AS servicio_encargado,
    a.persona_responsable,
    a.tiempo_aproximado,
    a.fechas_a_desarrollar,
    m.nombre AS modalidad, -- 👈 Nombre de la modalidad desde la nueva tabla modalidad
    e.nombre AS estado, -- 👈 Nombre del estado desde la nueva tabla estado
    a.detalles,
    a.metadatos
FROM
    actividades a
    LEFT JOIN actividad act ON a.actividad_id = act.id
    LEFT JOIN servicio_encargado se ON a.servicio_id = se.id
    LEFT JOIN subdireccion_perteneciente s ON se.subdireccion_id = s.id
    LEFT JOIN modalidad m ON a.modalidad_id = m.id -- 👈 Nueva relación
    LEFT JOIN estado e ON a.estado_id = e.id;
-- 👈 Nueva relación
CREATE TABLE users (
    id integer NOT NULL,
    nombre character varying(100) NOT NULL,
    username character varying(50) NOT NULL,
    email character varying(100) NOT NULL,
    password character varying(255) NOT NULL,
    role character varying(50) NOT NULL,
    estado character(1),
    creado_en timestamp without time zone DEFAULT now(),
    actualizado_en timestamp without time zone DEFAULT now()
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
        now(),
        now()
    );

-- 🔹 Agregar la columna subdireccion_id a servicio_encargado
ALTER TABLE servicio_encargado ADD COLUMN subdireccion_id INTEGER;

-- 🔹 Establecer la relación con subdireccion_perteneciente
ALTER TABLE servicio_encargado
ADD CONSTRAINT fk_servicio_subdireccion FOREIGN KEY (subdireccion_id) REFERENCES subdireccion_perteneciente (id) ON DELETE SET NULL ON UPDATE CASCADE;

-- 🔹 Opcional: si deseas que todas tengan una subdirección obligatoria
-- (descomenta esta línea si NO quieres permitir NULL)
-- ALTER TABLE servicio_encargado ALTER COLUMN subdireccion_id SET NOT NULL;

-- 🔹 (Opcional) Crear un índice para acelerar las búsquedas por subdirección
CREATE INDEX idx_servicio_subdireccion_id ON servicio_encargado (subdireccion_id);

-- =========================================================
-- 📋 Tabla de catálogo "actividad"
-- Contiene los nombres y descripciones de las actividades disponibles.
-- =========================================================
CREATE TABLE IF NOT EXISTS actividad (
    id SERIAL PRIMARY KEY, -- Identificador único autoincremental
    nombre VARCHAR(100) NOT NULL, -- Nombre del tipo de actividad
    descripcion TEXT, -- Descripción opcional
    activo BOOLEAN DEFAULT TRUE NOT NULL -- Control lógico para habilitar/deshabilitar
);

-- =========================================================
-- 🧩 Agregar columna "actividad_id" con relación a "actividad"
-- =========================================================
-- 1️⃣ Renombrar la columna
ALTER TABLE actividades RENAME COLUMN actividad TO actividad_id;

-- 2️⃣ Asegurar que sea del tipo correcto (por si acaso)
ALTER TABLE actividades
ALTER COLUMN actividad_id TYPE INTEGER USING actividad_id::integer;

-- 3️⃣ Crear la llave foránea hacia la tabla "actividad"
ALTER TABLE actividades
ADD CONSTRAINT fk_actividades_actividad FOREIGN KEY (actividad_id) REFERENCES actividad (id) ON UPDATE CASCADE ON DELETE SET NULL;

ALTER TABLE estado RENAME COLUMN descripcion TO nombre;

ALTER TABLE modalidad RENAME COLUMN descripcion TO nombre;

CREATE TABLE modalidad (
    id SERIAL PRIMARY KEY,
    codigo CHAR(1) UNIQUE NOT NULL,
    nombre VARCHAR(50) NOT NULL
);

CREATE TABLE estado (
    id SERIAL PRIMARY KEY,
    codigo CHAR(1) UNIQUE NOT NULL,
    nombre VARCHAR(50) NOT NULL
);

-- ==========================================================
-- Tabla: usuarios
-- Descripción:
--   Almacena los datos principales de cada usuario del sistema.
--   Incluye validaciones de unicidad, estado y control automático
--   de fechas de creación y actualización.
-- ==========================================================


CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,  -- Identificador único autoincremental

    nombre VARCHAR(100) NOT NULL,  -- Nombre completo del usuario

-- username y email son únicos para evitar duplicidad de cuentas
username VARCHAR(50) NOT NULL UNIQUE, -- Nombre de usuario único
email VARCHAR(100) DEFAULT NULL UNIQUE, -- Correo electrónico único
password VARCHAR(255) NOT NULL, -- Contraseña cifrada (bcrypt recomendado)
role VARCHAR(50) NOT NULL, -- Rol o tipo de usuario (admin, soporte, técnico, etc.)

-- Estado actual del usuario: A=Activo, I=Inactivo, S=Suspendido, etc.
estado CHAR(1) DEFAULT 'A' CHECK (estado IN ('A', 'I', 'S')),

-- Timestamps automáticos
creado_en TIMESTAMP DEFAULT now(),  -- Fecha de creación
    actualizado_en TIMESTAMP DEFAULT now()  -- Última fecha de actualización
);

-- ==========================================================
-- TRIGGER: Actualiza automáticamente el campo 'actualizado_en'
-- cada vez que se modifica un registro.
-- ==========================================================

CREATE OR REPLACE FUNCTION actualizar_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.actualizado_en = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_actualizar_timestamp
BEFORE UPDATE ON usuarios
FOR EACH ROW
EXECUTE FUNCTION actualizar_timestamp();

-- ==========================================================
-- INDICES ADICIONALES (opcional)
-- Mejoran el rendimiento en búsquedas por username y email.
-- ==========================================================

CREATE INDEX idx_usuarios_username ON usuarios (username);

CREATE INDEX idx_usuarios_email ON usuarios (email);

-- Eliminar duplicados por username, conservar el id más alto
DELETE FROM users a USING users b
WHERE
    a.username = b.username
    AND a.id < b.id;

-- Eliminar duplicados por email, conservar el id más alto
DELETE FROM users a USING users b
WHERE
    a.email = b.email
    AND a.id < b.id;

ALTER TABLE users
ADD CONSTRAINT users_username_unique UNIQUE (username);

ALTER TABLE users ADD CONSTRAINT users_email_unique UNIQUE (email);