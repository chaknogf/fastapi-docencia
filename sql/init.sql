CREATE TABLE actividades (
    id SERIAL PRIMARY KEY,
    tema TEXT NOT NULL,
    actividad INTEGER NOT NULL,
    servicio_encargado TEXT NOT NULL,
    persona_responsable JSONB,
    tiempo_aproximado VARCHAR(50),
    fechas_a_desarrollar VARCHAR(50),
    modalidad VARCHAR(2),
    estado VARCHAR(2),
    detalles JSONB,
    metadatos JSONB
);

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
        '$2b$12$ORcHnbOpNS4ErczFOUZsWukQkRax3zxH9dtfCw9T1A9ZshXc6Y/UW',
        'admin',
        'A',
        now(),
        now()
    );