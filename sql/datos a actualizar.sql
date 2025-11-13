BEGIN;

TRUNCATE TABLE servicio_encargado RESTART IDENTITY CASCADE;

INSERT INTO
    servicio_encargado (id, nombre, subdireccion_id)
VALUES (1, 'IT', NULL),
    (2, 'docencia', NULL),
    (3, 'DIRECCIÓN', 1),
    (4, 'ASESORÍA JURÍDICA', 1),
    (
        5,
        'GERENCIA ADMINISTRATIVA',
        5
    ),
    (6, 'COMPRAS', 5),
    (
        7,
        'SERVICIOS GENERALES Y MENTENIMIENTO',
        5
    ),
    (
        8,
        'ENCARGADO DE BODEGA DE SUMINISTROS',
        5
    ),
    (
        9,
        'ENCARGADO DE BODEGA DE MATERIAL MÉDICO QUIRÚRGICO Y PRODUCTOS AFINES',
        5
    ),
    (
        10,
        'ENCARGADO DE BODEGA DE MEDICAMENTOS',
        5
    ),
    (11, 'INVENTARIO', 5),
    (12, 'CONTABILIDAD', 5),
    (13, 'TESORERÍA', 5),
    (14, 'PRESUPUESTO', 5),
    (15, 'RECURSOS HUMANOS', 6),
    (
        16,
        'SUBDIRECCIÓN DE ENFERMERÍA',
        2
    ),
    (17, 'SERVICIO DE CRN', 2),
    (
        18,
        'SERVICIO DE PEDIATRÍA',
        2
    ),
    (19, 'COEX', 2),
    (20, 'MEDICINA', 2),
    (21, 'UCIN', 2),
    (22, 'UCIA', 2),
    (23, 'EMERGENCIA', 2),
    (24, 'MATERNIDAD', 2),
    (25, 'QUIROFANO', 2),
    (26, 'CIRUY TRAUMA', 2),
    (27, 'SUBDIRECCIÓN MÉDICA', 3),
    (28, 'MEDICINA INTERNA', 3),
    (29, 'CIRUGÍA', 3),
    (30, 'PEDIATRÍA', 3),
    (31, 'TRAUMATOLOGÍA', 3),
    (32, 'GINECOLOGÍA', 3),
    (33, 'ANESTESIA', 3),
    (34, 'MÉDICOS GENERALES', 3),
    (35, 'SUBDIRECCIÓN TÉCNICA', 4),
    (36, 'EPIDEMIOLOGÍA', 4),
    (37, 'ESTADÍSTICA', 4),
    (38, 'GESTOR AMBIENTAL', 4),
    (39, 'FARMACIA', 4),
    (40, 'PRODUCTOS AFINES', 4),
    (41, 'LABORATORIO', 4),
    (42, 'RAYOS X', 4),
    (43, 'REGISTROS MÉDICOS', 4),
    (44, 'TRABAJO SOCIAL', 4),
    (45, 'NUTRICIÓN', 4),
    (46, 'ALIMENTCIÓN', 4),
    (47, 'ATENCIÓN AL USUARIO', 4);

COMMIT;