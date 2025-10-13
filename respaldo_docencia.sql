--
-- PostgreSQL database dump
--

-- Dumped from database version 15.12 (Debian 15.12-1.pgdg120+1)
-- Dumped by pg_dump version 15.12 (Debian 15.12-1.pgdg120+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: actividades; Type: TABLE; Schema: public; Owner: mide
--

CREATE TABLE public.actividades (
    id integer NOT NULL,
    tema text NOT NULL,
    actividad integer NOT NULL,
    servicio_encargado text NOT NULL,
    persona_responsable jsonb,
    tiempo_aproximado character varying(50),
    fechas_a_desarrollar character varying(50),
    modalidad character varying(2) NOT NULL,
    estado character varying(2) NOT NULL,
    detalles jsonb,
    metadatos jsonb
);


ALTER TABLE public.actividades OWNER TO mide;

--
-- Name: actividades_id_seq; Type: SEQUENCE; Schema: public; Owner: mide
--

CREATE SEQUENCE public.actividades_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.actividades_id_seq OWNER TO mide;

--
-- Name: actividades_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: mide
--

ALTER SEQUENCE public.actividades_id_seq OWNED BY public.actividades.id;


--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: mide
--

CREATE SEQUENCE public.users_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.users_id_seq OWNER TO mide;

--
-- Name: users; Type: TABLE; Schema: public; Owner: mide
--

CREATE TABLE public.users (
    id integer DEFAULT nextval('public.users_id_seq'::regclass) NOT NULL,
    nombre character varying(100) NOT NULL,
    username character varying(50) NOT NULL,
    email character varying(100) NOT NULL,
    password character varying(255) NOT NULL,
    role character varying(50) NOT NULL,
    estado character(1),
    creado_en timestamp without time zone DEFAULT now(),
    actualizado_en timestamp without time zone DEFAULT now()
);


ALTER TABLE public.users OWNER TO mide;

--
-- Name: vista_ejecucion; Type: VIEW; Schema: public; Owner: mide
--

CREATE VIEW public.vista_ejecucion AS
 SELECT sub.anio,
    sub.estado,
    (count(*))::integer AS total_estado,
    round((((count(*))::numeric * 100.0) / sum(count(*)) OVER (PARTITION BY sub.anio)), 2) AS porcentaje
   FROM ( SELECT actividades.estado,
            to_date((actividades.fechas_a_desarrollar)::text, 'YYYY-MM-DD'::text) AS fecha,
            (EXTRACT(year FROM to_date((actividades.fechas_a_desarrollar)::text, 'YYYY-MM-DD'::text)))::integer AS anio
           FROM public.actividades
          WHERE ((actividades.fechas_a_desarrollar)::text ~ '^\d{4}-\d{2}-\d{2}'::text)) sub
  GROUP BY sub.anio, sub.estado;


ALTER TABLE public.vista_ejecucion OWNER TO mide;

--
-- Name: vista_ejecucion_servicio; Type: VIEW; Schema: public; Owner: mide
--

CREATE VIEW public.vista_ejecucion_servicio AS
 SELECT sub.anio,
    sub.servicio_encargado,
    sub.estado,
    sub.total_estado,
    round((((sub.total_estado)::numeric * 100.0) / (sum(sub.total_estado) OVER (PARTITION BY sub.anio, sub.servicio_encargado))::numeric), 2) AS porcentaje
   FROM ( SELECT (EXTRACT(year FROM to_date((actividades.fechas_a_desarrollar)::text, 'YYYY-MM-DD'::text)))::integer AS anio,
            actividades.servicio_encargado,
            actividades.estado,
            (count(*))::integer AS total_estado
           FROM public.actividades
          WHERE ((actividades.fechas_a_desarrollar)::text ~ '^\d{4}-\d{2}-\d{2}'::text)
          GROUP BY ((EXTRACT(year FROM to_date((actividades.fechas_a_desarrollar)::text, 'YYYY-MM-DD'::text)))::integer), actividades.servicio_encargado, actividades.estado) sub;


ALTER TABLE public.vista_ejecucion_servicio OWNER TO mide;

--
-- Name: vista_estadisticas; Type: VIEW; Schema: public; Owner: mide
--

CREATE VIEW public.vista_estadisticas AS
 SELECT actividades.estado,
    (EXTRACT(year FROM to_date((actividades.fechas_a_desarrollar)::text, 'YYYY-MM-DD'::text)))::integer AS anio,
    actividades.servicio_encargado,
    count(*) AS total
   FROM public.actividades
  WHERE (actividades.fechas_a_desarrollar IS NOT NULL)
  GROUP BY actividades.estado, ((EXTRACT(year FROM to_date((actividades.fechas_a_desarrollar)::text, 'YYYY-MM-DD'::text)))::integer), actividades.servicio_encargado;


ALTER TABLE public.vista_estadisticas OWNER TO mide;

--
-- Name: vista_reporte; Type: VIEW; Schema: public; Owner: mide
--

CREATE VIEW public.vista_reporte AS
 SELECT a.id,
    a.tema,
    a.actividad,
    a.servicio_encargado,
    a.fechas_a_desarrollar,
    a.modalidad,
    a.estado,
    ((a.detalles ->> 'mes'::text))::integer AS mes,
        CASE
            WHEN ((a.fechas_a_desarrollar)::text ~ '^\d{4}-\d{2}-\d{2}$'::text) THEN (EXTRACT(year FROM to_date((a.fechas_a_desarrollar)::text, 'YYYY-MM-DD'::text)))::integer
            ELSE NULL::integer
        END AS anio,
    (a.detalles ->> 'fecha_entrega_informe'::text) AS fecha_entrega_informe,
    (a.detalles ->> 'nota'::text) AS nota
   FROM public.actividades a
  WHERE ((a.fechas_a_desarrollar IS NOT NULL) AND ((a.detalles ->> 'mes'::text) ~ '^\d+$'::text));


ALTER TABLE public.vista_reporte OWNER TO mide;

--
-- Name: vista_servicios; Type: VIEW; Schema: public; Owner: mide
--

CREATE VIEW public.vista_servicios AS
 SELECT (EXTRACT(year FROM (a.fechas_a_desarrollar)::date))::integer AS anio,
    a.servicio_encargado,
    count(*) AS total,
    count(*) FILTER (WHERE ((a.estado)::text = 'C'::text)) AS completado,
    count(*) FILTER (WHERE ((a.estado)::text = 'R'::text)) AS reprogramado,
    count(*) FILTER (WHERE ((a.estado)::text = 'A'::text)) AS anulado,
    round((((count(*) FILTER (WHERE ((a.estado)::text = 'C'::text)))::numeric * 100.0) / (count(*))::numeric), 2) AS porcentaje,
    min((a.detalles ->> 'nota'::text)) AS nota
   FROM public.actividades a
  GROUP BY ((EXTRACT(year FROM (a.fechas_a_desarrollar)::date))::integer), a.servicio_encargado
  ORDER BY ((EXTRACT(year FROM (a.fechas_a_desarrollar)::date))::integer), a.servicio_encargado;


ALTER TABLE public.vista_servicios OWNER TO mide;

--
-- Name: actividades id; Type: DEFAULT; Schema: public; Owner: mide
--

ALTER TABLE ONLY public.actividades ALTER COLUMN id SET DEFAULT nextval('public.actividades_id_seq'::regclass);


--
-- Data for Name: actividades; Type: TABLE DATA; Schema: public; Owner: mide
--

COPY public.actividades (id, tema, actividad, servicio_encargado, persona_responsable, tiempo_aproximado, fechas_a_desarrollar, modalidad, estado, detalles, metadatos) FROM stdin;
3	Manejo Medicamentoso para el Aborto Incompleto: Misoprostol y Mifepristona	2	GINECOLOGÍA Y OBSTETRICIA	{"r0": {"nombre": "Dra. Karen Junay", "puesto": "Ginecóloga"}}	50 minutos	2025-05-15	V	P	{"mes": 5, "link": "", "bueno": 0, "lugar": "", "regular": 0, "duracion": "", "contenido": "", "excelente": 0, "asistencia": 0, "deficiente": 0, "inasistencia": 0, "grupo_dirigido": "", "fecha_entrega_informe": ""}	{"user": "", "registro": ""}
4	Obligaciones y derechos de los trabajadores	2	Asesoría Juridica	{"r0": {"nombre": "Lic. Rudy Carpio", "puesto": "Asesor Juridico"}}	1 hora	2025-05-30	P	P	{"mes": 5, "link": "", "bueno": 0, "lugar": "", "regular": 0, "duracion": "", "contenido": "", "excelente": 0, "asistencia": 0, "deficiente": 0, "inasistencia": 0, "grupo_dirigido": "", "fecha_entrega_informe": ""}	{"user": "", "registro": ""}
5	Manejo de Desechos Solidos Hospitalarios Según Acuerdo Gubernativo 509	2	Comite de Desechos Solidos Hospitalarios	{"r0": {"nombre": "", "puesto": ""}}	1 hora 30 minutos	2025-05-30	P	P	{"mes": 5, "link": "", "bueno": 0, "lugar": "", "regular": 0, "duracion": "", "contenido": "", "excelente": 0, "asistencia": 0, "deficiente": 0, "inasistencia": 0, "grupo_dirigido": "", "fecha_entrega_informe": ""}	{"user": "", "registro": ""}
2	Beneficios de la Lactancia Materna	1	Nutrición	{"r0": {"nombre": "Licda. Angelica Chiquito", "puesto": "Nutricionista"}}	2 horas	2025-05-30	P	C	{"mes": 5, "link": "", "bueno": 0, "lugar": "", "regular": 0, "duracion": "", "contenido": "", "excelente": 0, "asistencia": 0, "deficiente": 0, "inasistencia": 0, "grupo_dirigido": "", "fecha_entrega_informe": ""}	{"user": "", "registro": ""}
6	 Buenas practicas de almacenamiento 	2	PRODUCTOS AFINES	{"r0": {"nombre": "Elsa Hernandez Ramón", "puesto": "Encargada"}}	1/2 hora	2025-06-03	P	P	{"mes": 6, "link": "", "bueno": 0, "lugar": "", "regular": 0, "duracion": "", "contenido": "", "excelente": 0, "asistencia": 0, "deficiente": 0, "inasistencia": 0, "grupo_dirigido": "", "fecha_entrega_informe": ""}	{"user": "", "registro": ""}
15	Retroalimentación de manejo adecuado de desechos Sólidos Hospitalarios y Comunes	1	SERVICIOS GENERALES Y MANTENIMIENTO	{"r0": {"nombre": "Mery Cúc", "puesto": "Encargada"}}	2 horas	2025-07-30	P	C	{"mes": 7, "link": "", "bueno": 0, "lugar": "", "regular": 0, "duracion": "", "contenido": "", "excelente": 0, "asistencia": 0, "deficiente": 0, "inasistencia": 0, "grupo_dirigido": "", "fecha_entrega_informe": "2025-07-30"}	{"user": "", "registro": ""}
8	Interpretación Resultados de Química	1	LABORATORIO CLÍNICO	{"r0": {"nombre": "Lic. Marvynn Coy", "puesto": "Jefe"}}	1 hora	2025-06-27	P	P	{"mes": 6, "link": "", "bueno": 0, "lugar": "", "regular": 0, "duracion": "", "contenido": "", "excelente": 0, "asistencia": 0, "deficiente": 0, "inasistencia": 0, "grupo_dirigido": "", "fecha_entrega_informe": ""}	{"user": "", "registro": ""}
11	Herramientas de comunicación para la educación en salud de adultos	2	NUTRICIÓN	{"r0": {"nombre": "Lcda. Angélica Chiquitó", "puesto": "Encargada"}}	1 hora	2025-06-30	P	P	{"mes": 6, "link": "", "bueno": 0, "lugar": "", "regular": 0, "duracion": "", "contenido": "", "excelente": 0, "asistencia": 0, "deficiente": 0, "inasistencia": 0, "grupo_dirigido": "", "fecha_entrega_informe": ""}	{"user": "", "registro": ""}
12	Manipulación de alimentos	2	NUTRICIÓN	{"r0": {"nombre": "Lcda. Angélica Chiquitó", "puesto": "Encargada"}}	1 hora	2025-06-30	P	P	{"mes": 6, "link": "", "bueno": 0, "lugar": "", "regular": 0, "duracion": "", "contenido": "", "excelente": 0, "asistencia": 0, "deficiente": 0, "inasistencia": 0, "grupo_dirigido": "", "fecha_entrega_informe": ""}	{"user": "", "registro": ""}
13	Plan educacional (Prevención en Salud bucal)	2	ODONTOLOGÍA	{"r0": {"nombre": "Dra. Erika Meléndez", "puesto": "Odontóloga"}}	45 minutos	2025-06-30	P	P	{"mes": 6, "link": "", "bueno": 0, "lugar": "", "regular": 0, "duracion": "", "contenido": "", "excelente": 0, "asistencia": 0, "deficiente": 0, "inasistencia": 0, "grupo_dirigido": "", "fecha_entrega_informe": ""}	{"user": "", "registro": ""}
14	Bress de medicamentos	1	BODEGA	{"r0": {"nombre": "Eddy Hernández", "puesto": "Bodeguero"}}	1 hora	2025-07-30	P	P	{"mes": 7, "link": "", "bueno": 0, "lugar": "", "regular": 0, "duracion": "", "contenido": "", "excelente": 0, "asistencia": 0, "deficiente": 0, "inasistencia": 0, "grupo_dirigido": "", "fecha_entrega_informe": ""}	{"user": "", "registro": ""}
16	Compras Directas, Npg y Contrato Abierto	2	COMPRAS	{"r0": {"nombre": "Ronald Orrego", "puesto": "Encargado"}}	1 hora	2025-07-30	P	P	{"mes": 7, "link": "", "bueno": 0, "lugar": "", "regular": 0, "duracion": "", "contenido": "", "excelente": 0, "asistencia": 0, "deficiente": 0, "inasistencia": 0, "grupo_dirigido": "", "fecha_entrega_informe": ""}	{"user": "", "registro": ""}
7	Traslado sin afectación en libros y traslados con afectación en libros en el  Módulo de Inventarios de SICOIN	1	INVENTARIO DE ACTIVOS FIJOS	{"r0": {"nombre": "Christian Gomez", "puesto": "Encargado"}}	1 hora	2025-06-09	P	C	{"mes": 6, "link": "", "bueno": 0, "lugar": "", "regular": 0, "duracion": "", "contenido": "", "excelente": 0, "asistencia": 0, "deficiente": 0, "inasistencia": 0, "grupo_dirigido": "", "fecha_entrega_informe": "2025-07-15"}	{"user": "", "registro": ""}
10	Manejo de Desechos Sólidos Hospitalarios según Acuerdo Gubernativo 509-2001	2	GESTIÓN AMBIENTAL	{"r0": {"nombre": "Ing. Ambiental", "puesto": "Gestor Ambiental"}}	1.5 horas	2025-06-30	P	C	{"mes": 6, "link": "", "bueno": 0, "lugar": "", "regular": 0, "duracion": "", "contenido": "", "excelente": 0, "asistencia": 0, "deficiente": 0, "inasistencia": 0, "grupo_dirigido": "Estudiantes Médicos Externos", "fecha_entrega_informe": "2025-06-13"}	{"user": "", "registro": ""}
17	Choque séptico en Pediatría	2	PEDIATRÍA	{"r0": {"nombre": "Dr. Fredy Chalí", "puesto": "Jefe"}}	1 hora	2025-07-30	V	P	{"mes": 7, "link": "", "bueno": 0, "lugar": "", "regular": 0, "duracion": "1 hora", "contenido": "", "excelente": 0, "asistencia": 0, "deficiente": 0, "inasistencia": 0, "grupo_dirigido": "Médicos Pediatras", "fecha_entrega_informe": ""}	{"user": "", "registro": ""}
23	Redaccion de documentos para traslado de información 	1	SUBDIRECCIÓN TÉCNICA	{"r0": {"nombre": "", "puesto": "Subdirectora Técnica"}}	1 hora	2025-07-30	P	P	{"mes": 7, "link": "", "bueno": 0, "lugar": "", "regular": 0, "duracion": "1 hora", "contenido": "", "excelente": 0, "asistencia": 0, "deficiente": 0, "inasistencia": 0, "grupo_dirigido": "Jefes de servicio de la subdirección Técnica ", "fecha_entrega_informe": ""}	{"user": "", "registro": ""}
9	Obligaciones de los Contratistas	2	ASESORÍA JURÍDICA	{"r0": {"nombre": "Lic. Rudy Carpio", "puesto": "Asesor Jurídico"}}	1 hora	2025-06-30	P	C	{"mes": 6, "link": "", "bueno": 0, "lugar": "", "regular": 0, "duracion": "", "contenido": "", "excelente": 0, "asistencia": 0, "deficiente": 0, "inasistencia": 0, "grupo_dirigido": "", "fecha_entrega_informe": "2025-07-14"}	{"user": "", "registro": ""}
19	Inteligencia Emocional en el Liderazgo	2	RECURSOS HUMANOS	{"r0": {"nombre": "Gladis Argueta", "puesto": "Encargada del Subgrupo 18"}}	1 hora	2025-07-30	P	P	{"mes": 7, "link": "", "bueno": 0, "lugar": "", "regular": 0, "duracion": "1 hora", "contenido": "", "excelente": 0, "asistencia": 0, "deficiente": 0, "inasistencia": 0, "grupo_dirigido": "A todos los jefes de departamentos y servicios. (PENDIENTE DE REPROGRAMACIÓN)", "fecha_entrega_informe": ""}	{"user": "", "registro": ""}
21	Manejo de Desechos Sólidos Hospitalarios según Acuerdo Gubernativo 509-2001	2	GESTIÓN AMBIENTAL	{"r0": {"nombre": "Ing.", "puesto": "Gestor Ambiental"}}	1.5 horas	2025-07-25	P	C	{"mes": 7, "link": "", "bueno": 0, "lugar": "", "regular": 0, "duracion": "1.5 horas", "contenido": "", "excelente": 0, "asistencia": 0, "deficiente": 0, "inasistencia": 0, "grupo_dirigido": "Estudiantes Practicantes", "fecha_entrega_informe": "2025-08-01"}	{"user": "", "registro": ""}
25	Atención al paciente 	2	RAYOS X	{"r0": {"nombre": "Luis Fernando Miza Chalí", "puesto": "Radiólogo"}}	45 minutos	2025-07-11	P	C	{"mes": 7, "link": "", "nota": "", "bueno": 0, "lugar": "", "regular": 0, "duracion": "", "contenido": "", "excelente": 0, "asistencia": 7, "deficiente": 0, "inasistencia": 0, "grupo_dirigido": "Personal de Rayos X", "fecha_entrega_informe": "2025-08-05"}	{"user": "", "registro": ""}
18	Clasificación de desechos 	1	GERENCIA ADMINISTRATIVA FINANCIERA	{"r0": {"nombre": "Gerente Administrativo Financiero", "puesto": "Gerencia"}}	1 hora	2025-07-22	P	P	{"mes": 7, "link": "", "bueno": 0, "lugar": "", "regular": 0, "duracion": "", "contenido": "", "excelente": 0, "asistencia": 0, "deficiente": 0, "inasistencia": 0, "grupo_dirigido": "", "fecha_entrega_informe": ""}	{"user": "", "registro": ""}
22	Ética Médica	2	SUBDIRECCIÓN MÉDICA	{"r0": {"nombre": "", "puesto": "Subdirectora médica"}}	1 hora	2025-07-30	V	P	{"mes": 7, "link": "", "bueno": 0, "lugar": "", "regular": 0, "duracion": "1 hora", "contenido": "", "excelente": 0, "asistencia": 0, "deficiente": 0, "inasistencia": 0, "grupo_dirigido": "JEFES DE DEPARTAMENTO", "fecha_entrega_informe": ""}	{"user": "", "registro": ""}
24	Trauma Craneoencefálico	2	CIRUGÍA	{"r0": {"nombre": "", "puesto": "Cirujano"}}	1 hora	2025-07-30	V	P	{"mes": 7, "link": "", "bueno": 0, "lugar": "", "regular": 0, "duracion": "1 hora", "contenido": "", "excelente": 0, "asistencia": 0, "deficiente": 0, "inasistencia": 0, "grupo_dirigido": "DEPARTAMENTO DE CIRUGÍA", "fecha_entrega_informe": ""}	{"user": "", "registro": ""}
34	Actualización del Manejo de Síndrome del Ovario Poliquístico	2	GINECOLOGÍA Y OBSTETRICIA	{"r0": {"nombre": "Dra. Karen Junay", "puesto": "Jefa del Departamento"}}	50 minutos	2025-08-22	V	P	{"mes": 8, "link": "", "bueno": 0, "lugar": "", "regular": 0, "duracion": "", "contenido": "", "excelente": 0, "asistencia": 0, "deficiente": 0, "inasistencia": 0, "grupo_dirigido": "", "fecha_entrega_informe": ""}	{"user": "", "registro": ""}
20	Conflictos de las normas juridicas laborales CAMBIO POR Consideraciones Generales de la Ley de Acceso a la Información Pública	2	ASESORÍA JURÍDICA	{"r0": {"nombre": "Lic. Rudy Carpio", "puesto": "Jurídico"}}	1 hora	2025-07-30	P	C	{"mes": 7, "link": "", "bueno": 0, "lugar": "", "regular": 0, "duracion": "", "contenido": "", "excelente": 0, "asistencia": 0, "deficiente": 0, "inasistencia": 0, "grupo_dirigido": "Personal de recursos humanos", "fecha_entrega_informe": "2025-08-01"}	{"user": "", "registro": ""}
26	Salud mental	2	SERVICIOS GENERALES Y MANTENIMIENTO	{"r0": {"nombre": "Lcda. Flor Eguizabal", "puesto": "Psicologa"}}	1 hora	2025-08-29	P	P	{"mes": 8, "link": "", "bueno": 0, "lugar": "", "regular": 0, "duracion": "", "contenido": "", "excelente": 0, "asistencia": 0, "deficiente": 0, "inasistencia": 0, "grupo_dirigido": "SERVICIOS GENERALES Y MANTENIMIENTO", "fecha_entrega_informe": ""}	{"user": "", "registro": ""}
27	NPG y Inclusión de Códigos a SIGES	2	COMPRAS	{"r0": {"nombre": "Astrid Argelia Oliva", "puesto": "Analista de compras"}}	1 hora	2025-08-31	P	P	{"mes": 8, "link": "", "bueno": 0, "lugar": "", "regular": 0, "duracion": "", "contenido": "", "excelente": 0, "asistencia": 0, "deficiente": 0, "inasistencia": 0, "grupo_dirigido": "", "fecha_entrega_informe": ""}	{"user": "", "registro": ""}
28	Síndrome Metabólico y Riesgo Cardiovascular	2	MEDICINA INTERNA	{"r0": {"nombre": "Dra. Cuín y Médico EPS", "puesto": "Jefa de Departamento"}}	50 minutos	2025-08-20	V	P	{"mes": 8, "link": "", "bueno": 0, "lugar": "", "regular": 0, "duracion": "", "contenido": "", "excelente": 0, "asistencia": 0, "deficiente": 0, "inasistencia": 0, "grupo_dirigido": "", "fecha_entrega_informe": ""}	{"user": "", "registro": ""}
29	Síndrome Metabólico y Riesgo Cardiovascular	2	MEDICINA INTERNA	{"r0": {"nombre": "Dra. Cuín y Médico EPS", "puesto": "Jefa de Departamento"}}	50 minutos	2025-08-20	V	P	{"mes": 8, "link": "", "bueno": 0, "lugar": "", "regular": 0, "duracion": "", "contenido": "", "excelente": 0, "asistencia": 0, "deficiente": 0, "inasistencia": 0, "grupo_dirigido": "", "fecha_entrega_informe": ""}	{"user": "", "registro": ""}
30	Hipertensión intraoperatoria: bases fisiológicas y manejo	2	ANESTESIOLOGÍA	{"r0": {"nombre": "Dra. Ana Lucía Pérez", "puesto": "Jefa del Departamento"}, "r1": {"nombre": "Dr. Marlon López", "puesto": "Invitado"}}	1 hora	2025-08-20	V	P	{"mes": 8, "link": "", "bueno": 0, "lugar": "", "regular": 0, "duracion": "", "contenido": "", "excelente": 0, "asistencia": 0, "deficiente": 0, "inasistencia": 0, "grupo_dirigido": "", "fecha_entrega_informe": ""}	{"user": "", "registro": ""}
31	Medidas de Seguridad	2	EPIDEMIOLOGÍA	{"r0": {"nombre": "Dra. Lesbia Coló", "puesto": "Jefa del Departamento"}}	1 hora	2025-08-23	P	P	{"mes": 8, "link": "", "bueno": 0, "lugar": "", "regular": 0, "duracion": "", "contenido": "", "excelente": 0, "asistencia": 0, "deficiente": 0, "inasistencia": 0, "grupo_dirigido": "", "fecha_entrega_informe": ""}	{"user": "", "registro": ""}
33	Normativas vigentes	1	FARMACIA	{"r0": {"nombre": "Lcda. Heidi Santos", "puesto": "Jefa del Departamento"}}	1 hora	2025-08-13	P	P	{"mes": 8, "link": "", "bueno": 0, "lugar": "", "regular": 0, "duracion": "", "contenido": "", "excelente": 0, "asistencia": 0, "deficiente": 0, "inasistencia": 0, "grupo_dirigido": "", "fecha_entrega_informe": ""}	{"user": "", "registro": ""}
35	Salud Mental	2	PSICOLOGÍA	{"r0": {"nombre": "Lcda. CIndy Martínez", "puesto": "Psicológa"}}	30 minutos	2025-08-31	P	P	{"mes": 8, "link": "", "bueno": 0, "lugar": "", "regular": 0, "duracion": "", "contenido": "", "excelente": 0, "asistencia": 0, "deficiente": 0, "inasistencia": 0, "grupo_dirigido": "Personal Asistencial", "fecha_entrega_informe": ""}	{"user": "", "registro": ""}
36	La evaluación de desempeño y sus efectos	2	ASESORÍA JURÍDICA	{"r0": {"nombre": "Lic. Rudy Carpio", "puesto": "Asesor Jurídico"}}	1 hora	2025-08-31	P	P	{"mes": 8, "link": "", "bueno": 0, "lugar": "", "regular": 0, "duracion": "", "contenido": "", "excelente": 0, "asistencia": 0, "deficiente": 0, "inasistencia": 0, "grupo_dirigido": "", "fecha_entrega_informe": ""}	{"user": "", "registro": ""}
39	1. Oxigenoterapia y aerosolterapia 2. Manejo de medicamentos para inducción y conducción del trabajo de parto  3. Manejo de monitores materno fetal  4. Manejo de instrumental quirúrgico 	1	SUBDIRECCIÓN DE ENFERMERÍA	{"r0": {"nombre": "Comité de Formación y  Capacitación", "puesto": ""}}	6 horas	2025-08-27	P	P	{"mes": 8, "link": "", "bueno": 0, "lugar": "", "regular": 0, "duracion": "", "contenido": "", "excelente": 0, "asistencia": 0, "deficiente": 0, "inasistencia": 0, "grupo_dirigido": "", "fecha_entrega_informe": ""}	{"user": "", "registro": ""}
42	Gastronomía Hospitalaria	2	NUTRICIÓN	{"r0": {"nombre": "Lcda. Angélica Chiquitó", "puesto": "Encargada del Departamento"}}	30 minutos	2025-08-31	P	P	{"mes": 8, "link": "", "bueno": 0, "lugar": "", "regular": 0, "duracion": "", "contenido": "", "excelente": 0, "asistencia": 0, "deficiente": 0, "inasistencia": 0, "grupo_dirigido": "Dirigido a personal del Servicio de Alimentación", "fecha_entrega_informe": ""}	{"user": "", "registro": ""}
37	Manejo de Desechos Sólidos Hospitalarios según Acuerdo Gubernativo 509-2001	2	GESTIÓN AMBIENTAL	{"r0": {"nombre": "Ing. Ambiental", "puesto": "Gestor Ambiental"}}	1.5 horas	2025-08-31	P	P	{"mes": 8, "link": "", "bueno": 0, "lugar": "", "regular": 0, "duracion": "", "contenido": "", "excelente": 0, "asistencia": 0, "deficiente": 0, "inasistencia": 0, "grupo_dirigido": "Todo el Personal (Personal operativo, asistencial, administrativo y médico)", "fecha_entrega_informe": ""}	{"user": "", "registro": ""}
38	1. Atención y cuidados de pacientes con quemaduras 2. Atención de paciente politraumatizado 3. Cuidados post-mortem	1	SUBDIRECCIÓN DE ENFERMERÍA	{"r0": {"nombre": "Comité de Formación y  Capacitación", "puesto": ""}}	6 horas	2025-08-26	P	P	{"mes": 8, "link": "", "bueno": 0, "lugar": "", "regular": 0, "duracion": "", "contenido": "", "excelente": 0, "asistencia": 0, "deficiente": 0, "inasistencia": 0, "grupo_dirigido": "", "fecha_entrega_informe": ""}	{"user": "", "registro": ""}
40	1. Limpieza concurrente y terminal 2. Cuidado humanizado 3. Monitoreo materno fetal 4. Atención y cuidados de pacientes con quemaduras	1	SUBDIRECCIÓN DE ENFERMERÍA	{"r0": {"nombre": "Comité de Formación y  Capacitación", "puesto": ""}}	6 horas	2025-08-28	P	P	{"mes": 8, "link": "", "bueno": 0, "lugar": "", "regular": 0, "duracion": "", "contenido": "", "excelente": 0, "asistencia": 0, "deficiente": 0, "inasistencia": 0, "grupo_dirigido": "", "fecha_entrega_informe": ""}	{"user": "", "registro": ""}
41	1. Técnicas de alimentación en recién nacidos 2. Limpieza terminal y concurrente 3. Cuidado humanizado 4. Oxigenoterapia y aerosolterapia 	1	SUBDIRECCIÓN DE ENFERMERÍA	{"r0": {"nombre": "Comité de Formación y  Capacitación", "puesto": ""}}	6 horas	2025-08-29	P	P	{"mes": 8, "link": "", "bueno": 0, "lugar": "", "regular": 0, "duracion": "", "contenido": "", "excelente": 0, "asistencia": 0, "deficiente": 0, "inasistencia": 0, "grupo_dirigido": "", "fecha_entrega_informe": ""}	{"user": "", "registro": ""}
32	Uso de Tecnologías de computo	2	INFORMÁTICA	{"r0": {"nombre": "Ronald Chacón", "puesto": "Encargado del departamento"}}	1 horas	2025-08-28	V	R	{"mes": 8, "link": "https://meet.google.com/yhw-rati-fsu", "nota": "14:00 A 15:00 HORAS", "bueno": 0, "lugar": "", "regular": 0, "duracion": "", "contenido": "TIPS DE EXECEL Y USO DE IA EN ENTORNO ADMINISTRATIVO", "excelente": 0, "asistencia": 0, "deficiente": 0, "inasistencia": 0, "grupo_dirigido": "Personal Administrativo", "fecha_entrega_informe": ""}	{"user": "", "registro": ""}
43	Infección de sitio quirúrgico	2	TRAUMATOLOGÍA Y ORTOPEDIA	{"r0": {"nombre": "Dr. Luis Ávalos", "puesto": "Jefe del Departamento"}}	2 horas	2025-08-31	P	R	{"mes": 8, "link": "", "nota": "otra prueba", "bueno": 0, "lugar": "", "regular": 0, "duracion": "", "contenido": "", "excelente": 0, "asistencia": 0, "deficiente": 0, "inasistencia": 0, "grupo_dirigido": "", "fecha_entrega_informe": ""}	{"user": "", "registro": ""}
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: mide
--

COPY public.users (id, nombre, username, email, password, role, estado, creado_en, actualizado_en) FROM stdin;
1	Administrador	admin	chaknogf@gmail.com	$2b$12$ENHIoxPN5ValfeHbBrE.4uJ514utKTh61arCXuHmX0SXvevd3FvDi	admin	A	2025-05-14 21:49:40.553347	2025-05-14 21:49:40.553347
2	user1	user1	user@example.com	$2b$12$9DgDQQFonZQF4.DQVxUIlucWKM8JnmzfVWj0q6tzrELHF0nLg.1fS	estandar	A	2025-05-21 22:54:13.105341	2025-05-21 22:54:13.105341
4	Marylin Guajan	marylin	user@example.com	$2b$12$BfQ.E7xcND9LVriNPmKxzejNXz2gurte//IxEwSAKga7vA6SQ5kpa	estandar	A	2025-07-04 15:46:40.871239	2025-07-04 15:46:40.871239
\.


--
-- Name: actividades_id_seq; Type: SEQUENCE SET; Schema: public; Owner: mide
--

SELECT pg_catalog.setval('public.actividades_id_seq', 43, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: mide
--

SELECT pg_catalog.setval('public.users_id_seq', 4, true);


--
-- Name: actividades actividades_pkey; Type: CONSTRAINT; Schema: public; Owner: mide
--

ALTER TABLE ONLY public.actividades
    ADD CONSTRAINT actividades_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: mide
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- PostgreSQL database dump complete
--

