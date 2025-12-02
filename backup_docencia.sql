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

--
-- Name: actualizar_timestamp(); Type: FUNCTION; Schema: public; Owner: admin
--

CREATE FUNCTION public.actualizar_timestamp() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.actualizado_en = now();
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.actualizar_timestamp() OWNER TO admin;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: actividad; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.actividad (
    id integer NOT NULL,
    nombre character varying(100) NOT NULL,
    descripcion text,
    activo boolean DEFAULT true NOT NULL
);


ALTER TABLE public.actividad OWNER TO admin;

--
-- Name: actividad_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.actividad_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.actividad_id_seq OWNER TO admin;

--
-- Name: actividad_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.actividad_id_seq OWNED BY public.actividad.id;


--
-- Name: actividades; Type: TABLE; Schema: public; Owner: mide
--

CREATE TABLE public.actividades (
    id integer NOT NULL,
    tema text NOT NULL,
    actividad_id integer NOT NULL,
    persona_responsable jsonb,
    tiempo_aproximado character varying(50),
    fecha_programada date,
    detalles jsonb,
    metadatos jsonb,
    subdireccion_id integer,
    servicio_id integer,
    modalidad_id integer,
    estado_id integer,
    mes_id integer,
    horario_programado time without time zone,
    lugar_id integer
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
-- Name: actividades_id_seq1; Type: SEQUENCE; Schema: public; Owner: mide
--

CREATE SEQUENCE public.actividades_id_seq1
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.actividades_id_seq1 OWNER TO mide;

--
-- Name: actividades_id_seq1; Type: SEQUENCE OWNED BY; Schema: public; Owner: mide
--

ALTER SEQUENCE public.actividades_id_seq1 OWNED BY public.actividades.id;


--
-- Name: asistencia; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.asistencia (
    id integer NOT NULL,
    nombre_completo character varying(150) NOT NULL,
    sexo_id integer,
    grupo_edad_id integer,
    cui bigint,
    puesto_funcional character varying(100),
    pertenencia_cultural_id integer,
    telefono_email character varying(150),
    datos_extras jsonb,
    capacitacion_id integer NOT NULL,
    fecha_registro timestamp without time zone DEFAULT now()
);


ALTER TABLE public.asistencia OWNER TO admin;

--
-- Name: asistencia_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.asistencia_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.asistencia_id_seq OWNER TO admin;

--
-- Name: asistencia_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.asistencia_id_seq OWNED BY public.asistencia.id;


--
-- Name: backup_users; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.backup_users (
    id integer,
    nombre character varying(100),
    username character varying(50),
    email character varying(100),
    password character varying(255),
    role character varying(50),
    estado character(1),
    creado_en timestamp without time zone,
    actualizado_en timestamp without time zone
);


ALTER TABLE public.backup_users OWNER TO admin;

--
-- Name: estado; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.estado (
    id integer NOT NULL,
    codigo character(1) NOT NULL,
    nombre character varying(50) NOT NULL
);


ALTER TABLE public.estado OWNER TO admin;

--
-- Name: estado_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.estado_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.estado_id_seq OWNER TO admin;

--
-- Name: estado_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.estado_id_seq OWNED BY public.estado.id;


--
-- Name: grupo_edad; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.grupo_edad (
    id integer NOT NULL,
    rango character varying(50) NOT NULL
);


ALTER TABLE public.grupo_edad OWNER TO admin;

--
-- Name: grupo_edad_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.grupo_edad_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.grupo_edad_id_seq OWNER TO admin;

--
-- Name: grupo_edad_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.grupo_edad_id_seq OWNED BY public.grupo_edad.id;


--
-- Name: lugares_de_realizacion; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.lugares_de_realizacion (
    id integer NOT NULL,
    nombre character varying(150) NOT NULL,
    descripcion character varying(200)
);


ALTER TABLE public.lugares_de_realizacion OWNER TO admin;

--
-- Name: lugares_de_realizacion_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.lugares_de_realizacion_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.lugares_de_realizacion_id_seq OWNER TO admin;

--
-- Name: lugares_de_realizacion_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.lugares_de_realizacion_id_seq OWNED BY public.lugares_de_realizacion.id;


--
-- Name: meses; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.meses (
    id integer NOT NULL,
    nombre character varying(20) NOT NULL
);


ALTER TABLE public.meses OWNER TO admin;

--
-- Name: meses_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.meses_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.meses_id_seq OWNER TO admin;

--
-- Name: meses_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.meses_id_seq OWNED BY public.meses.id;


--
-- Name: modalidad; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.modalidad (
    id integer NOT NULL,
    codigo character(1) NOT NULL,
    nombre character varying(50) NOT NULL
);


ALTER TABLE public.modalidad OWNER TO admin;

--
-- Name: modalidad_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.modalidad_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.modalidad_id_seq OWNER TO admin;

--
-- Name: modalidad_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.modalidad_id_seq OWNED BY public.modalidad.id;


--
-- Name: pertenencia_cultural; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.pertenencia_cultural (
    id integer NOT NULL,
    nombre character varying(100) NOT NULL
);


ALTER TABLE public.pertenencia_cultural OWNER TO admin;

--
-- Name: pertenencia_cultural_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.pertenencia_cultural_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.pertenencia_cultural_id_seq OWNER TO admin;

--
-- Name: pertenencia_cultural_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.pertenencia_cultural_id_seq OWNED BY public.pertenencia_cultural.id;


--
-- Name: resumen_anual; Type: VIEW; Schema: public; Owner: admin
--

CREATE VIEW public.resumen_anual AS
 SELECT (EXTRACT(year FROM a.fecha_programada))::integer AS anio,
    count(*) FILTER (WHERE (a.estado_id = 1)) AS programadas,
    count(*) FILTER (WHERE (a.estado_id = 2)) AS reprogramadas,
    count(*) FILTER (WHERE (a.estado_id = 3)) AS completadas,
    count(*) FILTER (WHERE (a.estado_id = 4)) AS anuladas,
    count(*) AS total
   FROM public.actividades a
  GROUP BY ((EXTRACT(year FROM a.fecha_programada))::integer)
  ORDER BY ((EXTRACT(year FROM a.fecha_programada))::integer) DESC;


ALTER TABLE public.resumen_anual OWNER TO admin;

--
-- Name: servicio_encargado; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.servicio_encargado (
    id integer NOT NULL,
    nombre text NOT NULL,
    descripcion text,
    encargado_servicio character varying(200),
    jefe_inmediato character varying(200),
    activo boolean DEFAULT true,
    creado_en timestamp without time zone DEFAULT now(),
    subdireccion_id integer,
    puesto_funcional character varying(150)
);


ALTER TABLE public.servicio_encargado OWNER TO admin;

--
-- Name: servicio_encargado_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.servicio_encargado_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.servicio_encargado_id_seq OWNER TO admin;

--
-- Name: servicio_encargado_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.servicio_encargado_id_seq OWNED BY public.servicio_encargado.id;


--
-- Name: sexo; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.sexo (
    id integer NOT NULL,
    nombre character varying(20) NOT NULL
);


ALTER TABLE public.sexo OWNER TO admin;

--
-- Name: sexo_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.sexo_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.sexo_id_seq OWNER TO admin;

--
-- Name: sexo_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.sexo_id_seq OWNED BY public.sexo.id;


--
-- Name: subdireccion_perteneciente; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.subdireccion_perteneciente (
    id integer NOT NULL,
    nombre character varying(80) NOT NULL,
    descripcion text,
    activo boolean DEFAULT true,
    creado_en timestamp without time zone DEFAULT now(),
    persona_encargada character varying(150)
);


ALTER TABLE public.subdireccion_perteneciente OWNER TO admin;

--
-- Name: subdireccion_perteneciente_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.subdireccion_perteneciente_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.subdireccion_perteneciente_id_seq OWNER TO admin;

--
-- Name: subdireccion_perteneciente_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.subdireccion_perteneciente_id_seq OWNED BY public.subdireccion_perteneciente.id;


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
-- Name: users; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.users (
    id integer DEFAULT nextval('public.users_id_seq'::regclass) NOT NULL,
    nombre character varying(100) NOT NULL,
    username character varying(50) NOT NULL,
    email character varying(100) NOT NULL,
    password character varying(255),
    role character varying(50) NOT NULL,
    estado character(1),
    creado_en timestamp without time zone DEFAULT now(),
    actualizado_en timestamp without time zone DEFAULT now(),
    servicio_id integer,
    google_id character varying(100)
);


ALTER TABLE public.users OWNER TO admin;

--
-- Name: usuarios; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.usuarios (
    id integer NOT NULL,
    nombre character varying(100) NOT NULL,
    username character varying(50) NOT NULL,
    email character varying(100) DEFAULT NULL::character varying,
    password character varying(255) NOT NULL,
    role character varying(50) NOT NULL,
    estado character(1) DEFAULT 'A'::bpchar,
    creado_en timestamp without time zone DEFAULT now(),
    actualizado_en timestamp without time zone DEFAULT now(),
    CONSTRAINT usuarios_estado_check CHECK ((estado = ANY (ARRAY['A'::bpchar, 'I'::bpchar, 'S'::bpchar])))
);


ALTER TABLE public.usuarios OWNER TO admin;

--
-- Name: usuarios_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.usuarios_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.usuarios_id_seq OWNER TO admin;

--
-- Name: usuarios_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.usuarios_id_seq OWNED BY public.usuarios.id;


--
-- Name: vista_actividades_completa; Type: VIEW; Schema: public; Owner: admin
--

CREATE VIEW public.vista_actividades_completa AS
 SELECT a.id,
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
    (EXTRACT(year FROM a.fecha_programada))::integer AS anio,
    mo.nombre AS modalidad,
    a.modalidad_id,
    e.nombre AS estado,
    a.estado_id,
    a.detalles,
    a.metadatos
   FROM (((((((public.actividades a
     LEFT JOIN public.actividad act ON ((a.actividad_id = act.id)))
     LEFT JOIN public.servicio_encargado se ON ((a.servicio_id = se.id)))
     LEFT JOIN public.subdireccion_perteneciente s ON ((se.subdireccion_id = s.id)))
     LEFT JOIN public.modalidad mo ON ((a.modalidad_id = mo.id)))
     LEFT JOIN public.estado e ON ((a.estado_id = e.id)))
     LEFT JOIN public.meses m2 ON ((a.mes_id = m2.id)))
     LEFT JOIN public.lugares_de_realizacion ldr ON ((a.lugar_id = ldr.id)));


ALTER TABLE public.vista_actividades_completa OWNER TO admin;

--
-- Name: vista_ejecucion; Type: VIEW; Schema: public; Owner: admin
--

CREATE VIEW public.vista_ejecucion AS
 SELECT se.id AS servicio_id,
    se.nombre AS servicio_encargado,
    s.id AS subdireccion_id,
    s.nombre AS subdireccion,
    (EXTRACT(year FROM a.fecha_programada))::integer AS anio,
    count(*) FILTER (WHERE (e.id = 3)) AS completa,
    count(*) FILTER (WHERE (e.id = 1)) AS programada,
    count(*) FILTER (WHERE (e.id = 2)) AS reprogramada,
    count(*) FILTER (WHERE (e.id = 4)) AS suspendida,
    count(*) AS total,
        CASE
            WHEN (count(*) = 0) THEN (0)::numeric
            ELSE ((count(*) FILTER (WHERE (e.id = 3)))::numeric / (count(*))::numeric)
        END AS ejecutado
   FROM (((public.actividades a
     LEFT JOIN public.servicio_encargado se ON ((a.servicio_id = se.id)))
     LEFT JOIN public.subdireccion_perteneciente s ON ((se.subdireccion_id = s.id)))
     LEFT JOIN public.estado e ON ((a.estado_id = e.id)))
  WHERE (a.fecha_programada IS NOT NULL)
  GROUP BY se.id, se.nombre, s.id, s.nombre, ((EXTRACT(year FROM a.fecha_programada))::integer)
  ORDER BY ((EXTRACT(year FROM a.fecha_programada))::integer) DESC, s.id, se.id;


ALTER TABLE public.vista_ejecucion OWNER TO admin;

--
-- Name: vista_reporte; Type: VIEW; Schema: public; Owner: admin
--

CREATE VIEW public.vista_reporte AS
 SELECT a.id,
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
    se.jefe_inmediato,
    se.encargado_servicio,
    (EXTRACT(year FROM a.fecha_programada))::integer AS anio,
    mo.nombre AS modalidad,
    e.nombre AS estado,
    COALESCE((a.detalles ->> 'nota'::text), ''::text) AS nota
   FROM (((((((public.actividades a
     LEFT JOIN public.actividad act ON ((a.actividad_id = act.id)))
     LEFT JOIN public.servicio_encargado se ON ((a.servicio_id = se.id)))
     LEFT JOIN public.subdireccion_perteneciente su ON ((se.subdireccion_id = su.id)))
     LEFT JOIN public.modalidad mo ON ((a.modalidad_id = mo.id)))
     LEFT JOIN public.estado e ON ((a.estado_id = e.id)))
     LEFT JOIN public.lugares_de_realizacion ldr ON ((a.lugar_id = ldr.id)))
     LEFT JOIN public.meses m2 ON ((a.mes_id = m2.id)));


ALTER TABLE public.vista_reporte OWNER TO admin;

--
-- Name: actividad id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.actividad ALTER COLUMN id SET DEFAULT nextval('public.actividad_id_seq'::regclass);


--
-- Name: actividades id; Type: DEFAULT; Schema: public; Owner: mide
--

ALTER TABLE ONLY public.actividades ALTER COLUMN id SET DEFAULT nextval('public.actividades_id_seq1'::regclass);


--
-- Name: asistencia id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.asistencia ALTER COLUMN id SET DEFAULT nextval('public.asistencia_id_seq'::regclass);


--
-- Name: estado id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.estado ALTER COLUMN id SET DEFAULT nextval('public.estado_id_seq'::regclass);


--
-- Name: grupo_edad id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.grupo_edad ALTER COLUMN id SET DEFAULT nextval('public.grupo_edad_id_seq'::regclass);


--
-- Name: lugares_de_realizacion id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.lugares_de_realizacion ALTER COLUMN id SET DEFAULT nextval('public.lugares_de_realizacion_id_seq'::regclass);


--
-- Name: meses id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.meses ALTER COLUMN id SET DEFAULT nextval('public.meses_id_seq'::regclass);


--
-- Name: modalidad id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.modalidad ALTER COLUMN id SET DEFAULT nextval('public.modalidad_id_seq'::regclass);


--
-- Name: pertenencia_cultural id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.pertenencia_cultural ALTER COLUMN id SET DEFAULT nextval('public.pertenencia_cultural_id_seq'::regclass);


--
-- Name: servicio_encargado id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.servicio_encargado ALTER COLUMN id SET DEFAULT nextval('public.servicio_encargado_id_seq'::regclass);


--
-- Name: sexo id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.sexo ALTER COLUMN id SET DEFAULT nextval('public.sexo_id_seq'::regclass);


--
-- Name: subdireccion_perteneciente id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.subdireccion_perteneciente ALTER COLUMN id SET DEFAULT nextval('public.subdireccion_perteneciente_id_seq'::regclass);


--
-- Name: usuarios id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.usuarios ALTER COLUMN id SET DEFAULT nextval('public.usuarios_id_seq'::regclass);


--
-- Data for Name: actividad; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.actividad (id, nombre, descripcion, activo) FROM stdin;
1	Capacitación	Se aplica prueba de los conocimientos	t
2	Charla	No se realiza prueba de los conocimientos	t
\.


--
-- Data for Name: actividades; Type: TABLE DATA; Schema: public; Owner: mide
--

COPY public.actividades (id, tema, actividad_id, persona_responsable, tiempo_aproximado, fecha_programada, detalles, metadatos, subdireccion_id, servicio_id, modalidad_id, estado_id, mes_id, horario_programado, lugar_id) FROM stdin;
1	prueba de sistema	2	{"r0": {"nombre": "chatGpt", "puesto": "ia"}}	1 hora	2025-11-14	{"mes": 0, "nota": "charla", "bueno": 0, "regular": 0, "excelente": 0, "asistencia": 0, "deficiente": 0, "inasistencia": 0}	{"user": "sistema", "registro": "2025-11-14T19:18:12.033Z"}	4	49	3	1	11	\N	\N
2	digitales	2	{"r0": {"nombre": "", "puesto": ""}}	1 hora	2025-11-14	{"mes": 0, "nota": "", "bueno": 0, "regular": 0, "excelente": 0, "asistencia": 0, "deficiente": 0, "inasistencia": 0}	{"user": "sistema", "registro": "2025-11-17T18:58:04.324Z"}	4	49	3	1	11	13:21:00	3
\.


--
-- Data for Name: asistencia; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.asistencia (id, nombre_completo, sexo_id, grupo_edad_id, cui, puesto_funcional, pertenencia_cultural_id, telefono_email, datos_extras, capacitacion_id, fecha_registro) FROM stdin;
1	mario sauce	1	1	1704890120101	informatico	4	77881234	{"opinion": "Regular", "comentario": "prueba", "codigo_empleado": 9912012}	2	2025-11-18 01:07:06.356312
2	mario sauce	1	1	1704890120101	informatico	4	77881234	{"opinion": "Regular", "comentario": "prueba", "codigo_empleado": 9912012}	2	2025-11-18 01:07:32.324166
3	JUANA CHAMECO	2	2	799898989898	cocinera	1	89898912	{"opinion": "bueno", "comentario": "nada quedecir ", "codigo_empleado": 999230}	1	2025-11-18 01:09:58.638113
4	Mario sauce	1	1	1704890120101	informatico	4	77881234	{"opinion": "Regular", "comentario": "prueba", "codigo_empleado": 9912012}	2	2025-11-18 01:12:24.398519
5	MARIA SANZ	2	2	9898989	Auxiliar	2	prueba@mail.com	{"opinion": "bueno", "comentario": "todo bien", "codigo_empleado": 890000}	2	2025-11-18 04:25:50.922669
6	DANIELA CANO	2	2	12130000	secretraria	1	939391	{"idioma": 25, "opinion": "bueno", "comentario": "---", "discapacidad": 6, "codigo_empleado": 221}	2	2025-11-18 06:03:20.812431
\.


--
-- Data for Name: backup_users; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.backup_users (id, nombre, username, email, password, role, estado, creado_en, actualizado_en) FROM stdin;
1	Administrador	admin	chaknogf@gmail.com	$2b$12$ENHIoxPN5ValfeHbBrE.4uJ514utKTh61arCXuHmX0SXvevd3FvDi	admin	A	2025-05-13 21:27:09.208016	2025-05-13 21:27:09.208016
1	Administrador	admin	chaknogf@gmail.com	$2b$12$ENHIoxPN5ValfeHbBrE.4uJ514utKTh61arCXuHmX0SXvevd3FvDi	admin	A	2025-05-14 21:49:40.553347	2025-05-14 21:49:40.553347
4	Marylin Guajan	marylin	user@example.com	$2b$12$BfQ.E7xcND9LVriNPmKxzejNXz2gurte//IxEwSAKga7vA6SQ5kpa	estandar	A	2025-07-04 15:46:40.871239	2025-07-04 15:46:40.871239
1	Administrador	admin	chaknogf@gmail.com	$2b$12$ENHIoxPN5ValfeHbBrE.4uJ514utKTh61arCXuHmX0SXvevd3FvDi	admin	A	2025-05-14 21:49:40.553347	2025-05-14 21:49:40.553347
4	Marylin Guajan	marylin	user@example.com	$2b$12$BfQ.E7xcND9LVriNPmKxzejNXz2gurte//IxEwSAKga7vA6SQ5kpa	estandar	A	2025-07-04 15:46:40.871239	2025-07-04 15:46:40.871239
\.


--
-- Data for Name: estado; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.estado (id, codigo, nombre) FROM stdin;
1	P	Programado
2	R	Reprogramada
3	C	Completada
4	A	Anulada
\.


--
-- Data for Name: grupo_edad; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.grupo_edad (id, rango) FROM stdin;
1	18-30
2	31-49
3	50-70
4	71 o más
\.


--
-- Data for Name: lugares_de_realizacion; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.lugares_de_realizacion (id, nombre, descripcion) FROM stdin;
1	direccion	direccion
2	toldos	area de comedores toldos
3	lugar de trabajo	en el mismo lugar del trabajo del servicio
4	lavanderia	reunion del personal operativos
5	fuera de las instalaciones	restaurante o salon contratado
\.


--
-- Data for Name: meses; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.meses (id, nombre) FROM stdin;
1	Enero
2	Febrero
3	Marzo
4	Abril
5	Mayo
6	Junio
7	Julio
8	Agosto
9	Septiembre
10	Octubre
11	Noviembre
12	Diciembre
\.


--
-- Data for Name: modalidad; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.modalidad (id, codigo, nombre) FROM stdin;
1	P	Presencial
2	V	Virtual
3	H	Híbrida
\.


--
-- Data for Name: pertenencia_cultural; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.pertenencia_cultural (id, nombre) FROM stdin;
1	Maya
2	Garifuna
3	Xinca
4	Ladino/Mestizo
5	Otro
\.


--
-- Data for Name: servicio_encargado; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.servicio_encargado (id, nombre, descripcion, encargado_servicio, jefe_inmediato, activo, creado_en, subdireccion_id, puesto_funcional) FROM stdin;
1	IT	\N	\N	\N	t	2025-11-14 15:15:48.095265	\N	\N
2	docencia	\N	\N	\N	t	2025-11-14 15:15:48.095265	\N	\N
3	DIRECCIÓN	\N	\N	\N	t	2025-11-14 15:15:48.095265	1	\N
4	ASESORÍA JURÍDICA	\N	\N	\N	t	2025-11-14 15:15:48.095265	1	\N
5	GERENCIA ADMINISTRATIVA	\N	\N	\N	t	2025-11-14 15:15:48.095265	5	\N
6	COMPRAS	\N	\N	\N	t	2025-11-14 15:15:48.095265	5	\N
7	SERVICIOS GENERALES Y MENTENIMIENTO	\N	\N	\N	t	2025-11-14 15:15:48.095265	5	\N
8	ENCARGADO DE BODEGA DE SUMINISTROS	\N	\N	\N	t	2025-11-14 15:15:48.095265	5	\N
9	ENCARGADO DE BODEGA DE MATERIAL MÉDICO QUIRÚRGICO Y PRODUCTOS AFINES	\N	\N	\N	t	2025-11-14 15:15:48.095265	5	\N
10	ENCARGADO DE BODEGA DE MEDICAMENTOS	\N	\N	\N	t	2025-11-14 15:15:48.095265	5	\N
11	INVENTARIO	\N	\N	\N	t	2025-11-14 15:15:48.095265	5	\N
12	CONTABILIDAD	\N	\N	\N	t	2025-11-14 15:15:48.095265	5	\N
13	TESORERÍA	\N	\N	\N	t	2025-11-14 15:15:48.095265	5	\N
14	PRESUPUESTO	\N	\N	\N	t	2025-11-14 15:15:48.095265	5	\N
15	RECURSOS HUMANOS	\N	\N	\N	t	2025-11-14 15:15:48.095265	6	\N
16	SUBDIRECCIÓN DE ENFERMERÍA	\N	\N	\N	t	2025-11-14 15:15:48.095265	2	\N
17	SERVICIO DE CRN	\N	\N	\N	t	2025-11-14 15:15:48.095265	2	\N
18	SERVICIO DE PEDIATRÍA	\N	\N	\N	t	2025-11-14 15:15:48.095265	2	\N
19	COEX	\N	\N	\N	t	2025-11-14 15:15:48.095265	2	\N
20	MEDICINA	\N	\N	\N	t	2025-11-14 15:15:48.095265	2	\N
21	UCIN	\N	\N	\N	t	2025-11-14 15:15:48.095265	2	\N
22	UCIA	\N	\N	\N	t	2025-11-14 15:15:48.095265	2	\N
23	EMERGENCIA	\N	\N	\N	t	2025-11-14 15:15:48.095265	2	\N
24	MATERNIDAD	\N	\N	\N	t	2025-11-14 15:15:48.095265	2	\N
25	QUIROFANO	\N	\N	\N	t	2025-11-14 15:15:48.095265	2	\N
26	CIRUY TRAUMA	\N	\N	\N	t	2025-11-14 15:15:48.095265	2	\N
27	SUBDIRECCIÓN MÉDICA	\N	\N	\N	t	2025-11-14 15:15:48.095265	3	\N
28	MEDICINA INTERNA	\N	\N	\N	t	2025-11-14 15:15:48.095265	3	\N
29	CIRUGÍA	\N	\N	\N	t	2025-11-14 15:15:48.095265	3	\N
30	PEDIATRÍA	\N	\N	\N	t	2025-11-14 15:15:48.095265	3	\N
31	TRAUMATOLOGÍA	\N	\N	\N	t	2025-11-14 15:15:48.095265	3	\N
32	GINECOLOGÍA	\N	\N	\N	t	2025-11-14 15:15:48.095265	3	\N
33	ANESTESIA	\N	\N	\N	t	2025-11-14 15:15:48.095265	3	\N
34	MÉDICOS GENERALES	\N	\N	\N	t	2025-11-14 15:15:48.095265	3	\N
35	SUBDIRECCIÓN TÉCNICA	\N	\N	\N	t	2025-11-14 15:15:48.095265	4	\N
36	EPIDEMIOLOGÍA	\N	\N	\N	t	2025-11-14 15:15:48.095265	4	\N
37	ESTADÍSTICA	\N	\N	\N	t	2025-11-14 15:15:48.095265	4	\N
38	GESTOR AMBIENTAL	\N	\N	\N	t	2025-11-14 15:15:48.095265	4	\N
39	FARMACIA	\N	\N	\N	t	2025-11-14 15:15:48.095265	4	\N
40	PRODUCTOS AFINES	\N	\N	\N	t	2025-11-14 15:15:48.095265	4	\N
41	LABORATORIO	\N	\N	\N	t	2025-11-14 15:15:48.095265	4	\N
42	RAYOS X	\N	\N	\N	t	2025-11-14 15:15:48.095265	4	\N
43	REGISTROS MÉDICOS	\N	\N	\N	t	2025-11-14 15:15:48.095265	4	\N
44	TRABAJO SOCIAL	\N	\N	\N	t	2025-11-14 15:15:48.095265	4	\N
45	NUTRICIÓN	\N	\N	\N	t	2025-11-14 15:15:48.095265	4	\N
46	ALIMENTCIÓN	\N	\N	\N	t	2025-11-14 15:15:48.095265	4	\N
47	ATENCIÓN AL USUARIO	\N	\N	\N	t	2025-11-14 15:15:48.095265	4	\N
48	PSICOLOGÍA	psicologia clinica	Lcda Flor Eguizabal	Mgtr Ana Colon	t	2025-11-14 15:15:54.489565	4	\N
49	INFORMATICA	IT	CHAK	\N	t	2025-11-17 16:04:11.096386	4	\N
\.


--
-- Data for Name: sexo; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.sexo (id, nombre) FROM stdin;
1	Hombre
2	Mujer
\.


--
-- Data for Name: subdireccion_perteneciente; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.subdireccion_perteneciente (id, nombre, descripcion, activo, creado_en, persona_encargada) FROM stdin;
1	Dirección	No es subdirección	t	2025-10-12 01:22:01.11754	Dra. Erika Leticia Batzibal Tucubal
2	Subdirección de Enfermería	Solo enfermería	t	2025-10-12 01:22:29.532444	Mgtr. Ingrid Azucena Coy
3	Subdirección Médica	Solo médicos	t	2025-10-12 01:22:54.082553	Dra. 
4	Subdirección Técnica	Servicios de Apoyo	t	2025-10-12 01:23:16.945232	Mgtr. Ana Cecilia Colón Gaspar
5	Gerencia	Servicios Administrativos y Financieros	t	2025-10-12 01:23:45.555469	Mgtr. Cindy Alejandra Flores López
6	Recursos Humanos	Recursos Humanos	t	2025-10-12 01:27:42.780391	Silvana Paola Higueros de Leon
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.users (id, nombre, username, email, password, role, estado, creado_en, actualizado_en, servicio_id, google_id) FROM stdin;
7	admin	admin	chaknogf@outlook.com	$argon2id$v=19$m=65536,t=3,p=4$olSqlXIO4bzXuvdeK2Us5Q$UQqFWn25+Wi7manOVU2S6Xla8NBR6qB22Y4FZ705m6E	admin	A	2025-11-11 19:16:33.323888	2025-11-11 19:16:33.323888	1	\N
\.


--
-- Data for Name: usuarios; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.usuarios (id, nombre, username, email, password, role, estado, creado_en, actualizado_en) FROM stdin;
\.


--
-- Name: actividad_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.actividad_id_seq', 2, true);


--
-- Name: actividades_id_seq; Type: SEQUENCE SET; Schema: public; Owner: mide
--

SELECT pg_catalog.setval('public.actividades_id_seq', 1, false);


--
-- Name: actividades_id_seq1; Type: SEQUENCE SET; Schema: public; Owner: mide
--

SELECT pg_catalog.setval('public.actividades_id_seq1', 2, true);


--
-- Name: asistencia_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.asistencia_id_seq', 6, true);


--
-- Name: estado_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.estado_id_seq', 4, true);


--
-- Name: grupo_edad_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.grupo_edad_id_seq', 1, false);


--
-- Name: lugares_de_realizacion_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.lugares_de_realizacion_id_seq', 1, false);


--
-- Name: meses_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.meses_id_seq', 1, false);


--
-- Name: modalidad_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.modalidad_id_seq', 3, true);


--
-- Name: pertenencia_cultural_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.pertenencia_cultural_id_seq', 1, false);


--
-- Name: servicio_encargado_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.servicio_encargado_id_seq', 49, true);


--
-- Name: sexo_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.sexo_id_seq', 1, false);


--
-- Name: subdireccion_perteneciente_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.subdireccion_perteneciente_id_seq', 6, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: mide
--

SELECT pg_catalog.setval('public.users_id_seq', 7, true);


--
-- Name: usuarios_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.usuarios_id_seq', 1, false);


--
-- Name: actividad actividad_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.actividad
    ADD CONSTRAINT actividad_pkey PRIMARY KEY (id);


--
-- Name: actividades actividades_pkey; Type: CONSTRAINT; Schema: public; Owner: mide
--

ALTER TABLE ONLY public.actividades
    ADD CONSTRAINT actividades_pkey PRIMARY KEY (id);


--
-- Name: asistencia asistencia_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.asistencia
    ADD CONSTRAINT asistencia_pkey PRIMARY KEY (id);


--
-- Name: estado estado_codigo_key; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.estado
    ADD CONSTRAINT estado_codigo_key UNIQUE (codigo);


--
-- Name: estado estado_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.estado
    ADD CONSTRAINT estado_pkey PRIMARY KEY (id);


--
-- Name: grupo_edad grupo_edad_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.grupo_edad
    ADD CONSTRAINT grupo_edad_pkey PRIMARY KEY (id);


--
-- Name: grupo_edad grupo_edad_rango_key; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.grupo_edad
    ADD CONSTRAINT grupo_edad_rango_key UNIQUE (rango);


--
-- Name: lugares_de_realizacion lugares_de_realizacion_nombre_key; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.lugares_de_realizacion
    ADD CONSTRAINT lugares_de_realizacion_nombre_key UNIQUE (nombre);


--
-- Name: lugares_de_realizacion lugares_de_realizacion_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.lugares_de_realizacion
    ADD CONSTRAINT lugares_de_realizacion_pkey PRIMARY KEY (id);


--
-- Name: meses meses_nombre_key; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.meses
    ADD CONSTRAINT meses_nombre_key UNIQUE (nombre);


--
-- Name: meses meses_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.meses
    ADD CONSTRAINT meses_pkey PRIMARY KEY (id);


--
-- Name: modalidad modalidad_codigo_key; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.modalidad
    ADD CONSTRAINT modalidad_codigo_key UNIQUE (codigo);


--
-- Name: modalidad modalidad_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.modalidad
    ADD CONSTRAINT modalidad_pkey PRIMARY KEY (id);


--
-- Name: pertenencia_cultural pertenencia_cultural_nombre_key; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.pertenencia_cultural
    ADD CONSTRAINT pertenencia_cultural_nombre_key UNIQUE (nombre);


--
-- Name: pertenencia_cultural pertenencia_cultural_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.pertenencia_cultural
    ADD CONSTRAINT pertenencia_cultural_pkey PRIMARY KEY (id);


--
-- Name: servicio_encargado servicio_encargado_nombre_key; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.servicio_encargado
    ADD CONSTRAINT servicio_encargado_nombre_key UNIQUE (nombre);


--
-- Name: servicio_encargado servicio_encargado_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.servicio_encargado
    ADD CONSTRAINT servicio_encargado_pkey PRIMARY KEY (id);


--
-- Name: sexo sexo_nombre_key; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.sexo
    ADD CONSTRAINT sexo_nombre_key UNIQUE (nombre);


--
-- Name: sexo sexo_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.sexo
    ADD CONSTRAINT sexo_pkey PRIMARY KEY (id);


--
-- Name: subdireccion_perteneciente subdireccion_perteneciente_nombre_key; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.subdireccion_perteneciente
    ADD CONSTRAINT subdireccion_perteneciente_nombre_key UNIQUE (nombre);


--
-- Name: subdireccion_perteneciente subdireccion_perteneciente_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.subdireccion_perteneciente
    ADD CONSTRAINT subdireccion_perteneciente_pkey PRIMARY KEY (id);


--
-- Name: users users_google_id_key; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_google_id_key UNIQUE (google_id);


--
-- Name: usuarios usuarios_email_key; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT usuarios_email_key UNIQUE (email);


--
-- Name: usuarios usuarios_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT usuarios_pkey PRIMARY KEY (id);


--
-- Name: usuarios usuarios_username_key; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT usuarios_username_key UNIQUE (username);


--
-- Name: idx_actividades_detalles_gin; Type: INDEX; Schema: public; Owner: mide
--

CREATE INDEX idx_actividades_detalles_gin ON public.actividades USING gin (detalles);


--
-- Name: idx_actividades_estado; Type: INDEX; Schema: public; Owner: mide
--

CREATE INDEX idx_actividades_estado ON public.actividades USING btree (estado_id);


--
-- Name: idx_actividades_fecha; Type: INDEX; Schema: public; Owner: mide
--

CREATE INDEX idx_actividades_fecha ON public.actividades USING btree (fecha_programada);


--
-- Name: idx_actividades_fecha_programada; Type: INDEX; Schema: public; Owner: mide
--

CREATE INDEX idx_actividades_fecha_programada ON public.actividades USING btree (fecha_programada);


--
-- Name: idx_actividades_mes; Type: INDEX; Schema: public; Owner: mide
--

CREATE INDEX idx_actividades_mes ON public.actividades USING btree (mes_id);


--
-- Name: idx_actividades_metadatos_gin; Type: INDEX; Schema: public; Owner: mide
--

CREATE INDEX idx_actividades_metadatos_gin ON public.actividades USING gin (metadatos);


--
-- Name: idx_actividades_modalidad; Type: INDEX; Schema: public; Owner: mide
--

CREATE INDEX idx_actividades_modalidad ON public.actividades USING btree (modalidad_id);


--
-- Name: idx_actividades_persona_responsable_gin; Type: INDEX; Schema: public; Owner: mide
--

CREATE INDEX idx_actividades_persona_responsable_gin ON public.actividades USING gin (persona_responsable);


--
-- Name: idx_actividades_servicio; Type: INDEX; Schema: public; Owner: mide
--

CREATE INDEX idx_actividades_servicio ON public.actividades USING btree (servicio_id);


--
-- Name: idx_actividades_subdireccion; Type: INDEX; Schema: public; Owner: mide
--

CREATE INDEX idx_actividades_subdireccion ON public.actividades USING btree (subdireccion_id);


--
-- Name: idx_lugares_nombre; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_lugares_nombre ON public.lugares_de_realizacion USING btree (nombre);


--
-- Name: idx_usuarios_email; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_usuarios_email ON public.usuarios USING btree (email);


--
-- Name: idx_usuarios_username; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_usuarios_username ON public.usuarios USING btree (username);


--
-- Name: usuarios trigger_actualizar_timestamp; Type: TRIGGER; Schema: public; Owner: admin
--

CREATE TRIGGER trigger_actualizar_timestamp BEFORE UPDATE ON public.usuarios FOR EACH ROW EXECUTE FUNCTION public.actualizar_timestamp();


--
-- Name: actividades actividades_actividad_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: mide
--

ALTER TABLE ONLY public.actividades
    ADD CONSTRAINT actividades_actividad_id_fkey FOREIGN KEY (actividad_id) REFERENCES public.actividad(id) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: actividades actividades_estado_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: mide
--

ALTER TABLE ONLY public.actividades
    ADD CONSTRAINT actividades_estado_id_fkey FOREIGN KEY (estado_id) REFERENCES public.estado(id) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: actividades actividades_mes_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: mide
--

ALTER TABLE ONLY public.actividades
    ADD CONSTRAINT actividades_mes_id_fkey FOREIGN KEY (mes_id) REFERENCES public.meses(id) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: actividades actividades_modalidad_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: mide
--

ALTER TABLE ONLY public.actividades
    ADD CONSTRAINT actividades_modalidad_id_fkey FOREIGN KEY (modalidad_id) REFERENCES public.modalidad(id) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: actividades actividades_subdireccion_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: mide
--

ALTER TABLE ONLY public.actividades
    ADD CONSTRAINT actividades_subdireccion_id_fkey FOREIGN KEY (subdireccion_id) REFERENCES public.subdireccion_perteneciente(id) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: asistencia asistencia_capacitacion_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.asistencia
    ADD CONSTRAINT asistencia_capacitacion_id_fkey FOREIGN KEY (capacitacion_id) REFERENCES public.actividades(id) ON DELETE CASCADE;


--
-- Name: asistencia asistencia_grupo_edad_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.asistencia
    ADD CONSTRAINT asistencia_grupo_edad_id_fkey FOREIGN KEY (grupo_edad_id) REFERENCES public.grupo_edad(id) ON DELETE SET NULL;


--
-- Name: asistencia asistencia_pertenencia_cultural_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.asistencia
    ADD CONSTRAINT asistencia_pertenencia_cultural_id_fkey FOREIGN KEY (pertenencia_cultural_id) REFERENCES public.pertenencia_cultural(id) ON DELETE SET NULL;


--
-- Name: asistencia asistencia_sexo_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.asistencia
    ADD CONSTRAINT asistencia_sexo_id_fkey FOREIGN KEY (sexo_id) REFERENCES public.sexo(id) ON DELETE SET NULL;


--
-- Name: actividades fk_actividades_actividad; Type: FK CONSTRAINT; Schema: public; Owner: mide
--

ALTER TABLE ONLY public.actividades
    ADD CONSTRAINT fk_actividades_actividad FOREIGN KEY (actividad_id) REFERENCES public.actividad(id) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: actividades fk_mes; Type: FK CONSTRAINT; Schema: public; Owner: mide
--

ALTER TABLE ONLY public.actividades
    ADD CONSTRAINT fk_mes FOREIGN KEY (mes_id) REFERENCES public.meses(id) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: servicio_encargado fk_sub; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.servicio_encargado
    ADD CONSTRAINT fk_sub FOREIGN KEY (subdireccion_id) REFERENCES public.subdireccion_perteneciente(id) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: actividades fk_subdireccion; Type: FK CONSTRAINT; Schema: public; Owner: mide
--

ALTER TABLE ONLY public.actividades
    ADD CONSTRAINT fk_subdireccion FOREIGN KEY (subdireccion_id) REFERENCES public.subdireccion_perteneciente(id) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- PostgreSQL database dump complete
--

