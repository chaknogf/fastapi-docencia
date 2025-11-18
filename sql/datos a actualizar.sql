BEGIN;

TRUNCATE TABLE servicio_encargado RESTART IDENTITY CASCADE;

INSERT INTO
    servicio_encargado (nombre, subdireccion_id)
VALUES ('IT', NULL),
    ('docencia', NULL),
    ('DIRECCIÓN', 1),
    ('ASESORÍA JURÍDICA', 1),
    ('GERENCIA ADMINISTRATIVA', 5),
    ('COMPRAS', 5),
    (
        'SERVICIOS GENERALES Y MENTENIMIENTO',
        5
    ),
    (
        'ENCARGADO DE BODEGA DE SUMINISTROS',
        5
    ),
    (
        'ENCARGADO DE BODEGA DE MATERIAL MÉDICO QUIRÚRGICO Y PRODUCTOS AFINES',
        5
    ),
    (
        'ENCARGADO DE BODEGA DE MEDICAMENTOS',
        5
    ),
    ('INVENTARIO', 5),
    ('CONTABILIDAD', 5),
    ('TESORERÍA', 5),
    ('PRESUPUESTO', 5),
    ('RECURSOS HUMANOS', 6),
    (
        'SUBDIRECCIÓN DE ENFERMERÍA',
        2
    ),
    ('SERVICIO DE CRN', 2),
    ('SERVICIO DE PEDIATRÍA', 2),
    ('COEX', 2),
    ('MEDICINA', 2),
    ('UCIN', 2),
    ('UCIA', 2),
    ('EMERGENCIA', 2),
    ('MATERNIDAD', 2),
    ('QUIROFANO', 2),
    ('CIRUY TRAUMA', 2),
    ('SUBDIRECCIÓN MÉDICA', 3),
    ('MEDICINA INTERNA', 3),
    ('CIRUGÍA', 3),
    ('PEDIATRÍA', 3),
    ('TRAUMATOLOGÍA', 3),
    ('GINECOLOGÍA', 3),
    ('ANESTESIA', 3),
    ('MÉDICOS GENERALES', 3),
    ('SUBDIRECCIÓN TÉCNICA', 4),
    ('EPIDEMIOLOGÍA', 4),
    ('ESTADÍSTICA', 4),
    ('GESTOR AMBIENTAL', 4),
    ('FARMACIA', 4),
    ('PRODUCTOS AFINES', 4),
    ('LABORATORIO', 4),
    ('RAYOS X', 4),
    ('REGISTROS MÉDICOS', 4),
    ('TRABAJO SOCIAL', 4),
    ('NUTRICIÓN', 4),
    ('ALIMENTCIÓN', 4),
    ('ATENCIÓN AL USUARIO', 4);

COMMIT;