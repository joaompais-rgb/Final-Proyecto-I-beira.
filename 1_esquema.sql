-- beira. en datos · esquema de la base de datos (MySQL 8)
--
-- QUÉ HACE
-- Borra la base beira si existe, la crea vacía y crea las 11 tablas con sus tipos de dato,
-- claves primarias (PRIMARY KEY), claves foráneas (FOREIGN KEY) y campos obligatorios (NOT NULL).
--
-- CÓMO SE EJECUTA Y CÓMO LLEGAN LOS DATOS
-- 1. Datos brutos: Portal BASE (contratos públicos), INE, PORDATA, OpenStreetMap, e-fatura de la PAISAN y Airtable.
-- 2. Limpieza y cálculo en pandas: secciones 2 a 7 del notebook notebooks/beira_en_datos.ipynb.
-- 3. Sección 8 del notebook: guarda una tabla por CSV en data/sql (y data/interno/sql, que no se sube a GitHub).
-- 4. Sección 9 del notebook: se conecta a MySQL con mysql.connector y ejecuta este script instrucción a instrucción.
-- 5. Sección 9 del notebook: lee cada CSV y lo inserta con INSERT INTO tabla (columnas) VALUES (...),
--    con executemany y commit (lección 4.7), en el mismo orden que este script.
-- 6. Sección 9 del notebook: SELECT COUNT(*) en cada tabla y assert para comprobar que MySQL tiene las mismas filas que el CSV.
-- También se puede abrir en MySQL Workbench (File > Open SQL Script) y ejecutar con el rayo: crea la base vacía.
--
-- TIPOS DE DATO QUE USO
--   VARCHAR(n)     texto. n queda por encima del valor más largo del CSV (el nombre de comprador más largo tiene 143 letras: VARCHAR(255)).
--   VARCHAR(2)     las columnas sí/no.
--   INT            números enteros: años, meses, días, habitantes, recuentos y los identificadores que numero yo (0, 1, 2...).
--   BIGINT         los identificadores numéricos que vienen de fuera: el NIF (9 cifras) y el idcontrato del Portal BASE.
--   DECIMAL(12,2)  dinero: guarda los céntimos exactos. DOUBLE guarda una aproximación y al sumar miles de contratos se nota.
--   DOUBLE         medidas con decimales que no son dinero: km, coordenadas, tasas, medianas e IPC.
--   DATE           fechas (AAAA-MM-DD). Guardo también ano y mes en INT para agrupar sin funciones de fecha.
--
-- RESTRICCIONES
--   PRIMARY KEY  una por tabla: el campo que identifica cada fila y no se repite (lo compruebo antes en pandas con duplicated).
--   FOREIGN KEY  une una tabla hija con su tabla madre. MySQL no deja insertar un contrato de un comprador que no existe.
--   NOT NULL     el campo es obligatorio. Dejo NULL solo donde el dato puede faltar (un municipio fuera de la región, un mes desconocido).
--
-- ORDEN
-- Primero las tablas madre (municipios, compradores, proveedores, clientes_paisan) y después las hijas,
-- porque una FOREIGN KEY solo puede apuntar a una tabla que ya existe. Los datos se insertan en el mismo orden.
--
-- RELACIONES (las líneas del diagrama EER)
--   municipios      1 a N  compradores, organizaciones y eventos   (por municipio)
--   compradores     1 a N  contratos                               (por comprador_nif)
--   proveedores     1 a N  contratos                               (por proveedor_id)
--   compradores     1 a 1  lista_beira                             (la lista es una parte de los compradores)
--   clientes_paisan 1 a N  facturas_paisan                         (por cliente)
--   indicadores_ano no tiene clave foránea: en las consultas se une a contratos por año (ano).
--   encomendas_beira va sola: son los pedidos de la beira., copiados de Airtable.

DROP DATABASE IF EXISTS beira;
CREATE DATABASE beira CHARACTER SET utf8mb4;
USE beira;

-- ---------------------------------------------------------------------------
-- Parte A · el mercado público (Portal BASE, OpenStreetMap, INE)
-- ---------------------------------------------------------------------------

-- Los 66 municipios de la región, con su distancia a la PAISAN. Tabla madre de compradores, organizaciones y eventos.
CREATE TABLE municipios (
    municipio      VARCHAR(60)  PRIMARY KEY,  -- el nombre del concelho no se repite: sirve de clave
    distrito       VARCHAR(40)  NOT NULL,     -- Coimbra, Guarda, Viseu o Castelo Branco
    piloto         VARCHAR(2)   NOT NULL,     -- sí/no: municipio de la zona piloto
    poblacion      INT          NOT NULL,     -- habitantes (INE)
    poblacion_5_24 INT          NOT NULL,     -- habitantes de 5 a 24 años, el público de equipos y escuelas
    km_a_la_base   DOUBLE       NOT NULL,     -- km hasta la PAISAN
    lat            DOUBLE       NULL,         -- coordenadas para el mapa de Tableau
    lon            DOUBLE       NULL
);

-- Las entidades públicas que compran ropa. El municipio va vacío (NULL) si no es de la región.
CREATE TABLE compradores (
    comprador_nif  BIGINT       PRIMARY KEY,  -- NIF de la entidad: 9 cifras, único
    comprador      VARCHAR(255) NOT NULL,     -- nombre oficial (el más largo tiene 143 letras)
    tipo_comprador VARCHAR(20)  NOT NULL,     -- camara, junta, escuela, bomberos u otro
    municipio      VARCHAR(60)  NULL,         -- clave foránea a municipios. NULL si la entidad no es de la región
    en_lista       VARCHAR(2)   NOT NULL,     -- sí/no: está en la lista de la beira.
    FOREIGN KEY (municipio) REFERENCES municipios (municipio)
);

-- Las empresas que les venden. El identificador es el NIF o, si no es público, un código (SN1, SN2...).
CREATE TABLE proveedores (
    proveedor_id   VARCHAR(20)  PRIMARY KEY,  -- texto y no número: mezcla NIF y códigos SN
    tipo_proveedor VARCHAR(30)  NOT NULL,     -- fardamento, bordados, estampagem, publicidad, otro...
    con_nif        VARCHAR(2)   NOT NULL      -- sí/no: el identificador es un NIF (si no, es un código SN)
);

-- Un contrato público de ropa (2020-2025). Es la tabla de hechos de la parte A: una fila por contrato.
CREATE TABLE contratos (
    idcontrato      BIGINT        PRIMARY KEY,  -- el número del contrato en el Portal BASE, único
    comprador_nif   BIGINT        NOT NULL,     -- quién compra: clave foránea a compradores
    proveedor_id    VARCHAR(20)   NOT NULL,     -- quién vende: clave foránea a proveedores
    fecha           DATE          NOT NULL,     -- fecha del contrato
    ano             INT           NOT NULL,     -- año y mes de la fecha, para agrupar
    mes             INT           NOT NULL,
    precio          DECIMAL(12,2) NOT NULL,     -- precio en euros, con céntimos exactos
    producto        VARCHAR(40)   NOT NULL,     -- ropa de trabajo, merchandising, camisetas, polos...
    grupo           VARCHAR(30)   NOT NULL,     -- prendas de equipo u otras prendas
    procedimiento   VARCHAR(30)   NOT NULL,     -- ajuste directo, consulta previa, concurso u otro
    plazo_dias      INT           NOT NULL,     -- plazo de ejecución en días
    competidores    INT           NOT NULL,     -- empresas concurrentes que publica el Portal BASE
    ropa_fardamento VARCHAR(2)    NOT NULL,     -- sí/no: el objeto del contrato es ropa o fardamento
    FOREIGN KEY (comprador_nif) REFERENCES compradores (comprador_nif),
    FOREIGN KEY (proveedor_id)  REFERENCES proveedores (proveedor_id)
);

-- La lista de la beira.: las 63 entidades de la región que compran ropa en dos años o más.
-- La clave primaria es también clave foránea: cada fila de la lista es un comprador (relación 1 a 1).
CREATE TABLE lista_beira (
    comprador_nif          BIGINT      PRIMARY KEY,  -- el mismo NIF que en compradores
    grupo_compra           VARCHAR(20) NOT NULL,     -- A. fiel, B. repite o D. en pausa
    tasa_vuelta            DOUBLE      NOT NULL,     -- parte de los casos en que el grupo vuelve a comprar al año siguiente (0 a 1)
    anos_con_compra        INT         NOT NULL,
    contratos              INT         NOT NULL,
    precio_mediano         DOUBLE      NOT NULL,     -- mediana calculada en pandas, no es un precio de factura
    ultimo_ano             INT         NOT NULL,
    mes_habitual           INT         NOT NULL,     -- el mes en que más compra (1 a 12)
    contratos_ropa         INT         NOT NULL,
    compra_ropa_fardamento VARCHAR(2)  NOT NULL,     -- sí/no
    procedimiento_habitual VARCHAR(30) NOT NULL,
    plazo_mediano_dias     DOUBLE      NOT NULL,
    proveedores_distintos  INT         NOT NULL,
    ya_compraba_2013_2015  VARCHAR(2)  NOT NULL,     -- sí/no
    publica_concursos      VARCHAR(2)  NOT NULL,     -- sí/no
    FOREIGN KEY (comprador_nif) REFERENCES compradores (comprador_nif)
);

-- Clubes, asociaciones, escuelas y otras organizaciones de la región (OpenStreetMap).
CREATE TABLE organizaciones (
    id_organizacion INT          PRIMARY KEY,  -- número que pongo yo (0, 1, 2...): los datos no traen identificador
    nombre          VARCHAR(150) NOT NULL,
    segmento        VARCHAR(30)  NOT NULL,     -- escuela, autarquia, club, asociacion, bomberos...
    municipio       VARCHAR(60)  NOT NULL,     -- clave foránea a municipios
    nivel_contacto  VARCHAR(20)  NOT NULL,     -- email, solo telefono, solo web o sin contacto
    km_a_la_base    DOUBLE       NULL,         -- NULL en las 44 que no tienen coordenadas
    FOREIGN KEY (municipio) REFERENCES municipios (municipio)
);

-- Fiestas y eventos de la región (proyecto 1).
CREATE TABLE eventos (
    id_evento INT          PRIMARY KEY,  -- número que pongo yo (0, 1, 2...)
    evento    VARCHAR(120) NOT NULL,
    tipo      VARCHAR(30)  NOT NULL,     -- festa religiosa, festa de aldeia, feira...
    municipio VARCHAR(60)  NOT NULL,     -- clave foránea a municipios
    mes       INT          NULL,         -- NULL en los 4 eventos sin fecha fija
    FOREIGN KEY (municipio) REFERENCES municipios (municipio)
);

-- Un año: salario mínimo (PORDATA) e IPC de la ropa (INE). Sin clave foránea: se une a contratos por ano.
CREATE TABLE indicadores_ano (
    ano            INT    PRIMARY KEY,  -- un año por fila (2011-2025)
    salario_minimo DOUBLE NOT NULL,     -- euros al mes
    ipc_ropa       DOUBLE NULL          -- índice de precios de la ropa
);

-- ---------------------------------------------------------------------------
-- Parte B · la PAISAN y la beira. (datos internos: no se suben a GitHub)
-- ---------------------------------------------------------------------------

-- Los clientes de la PAISAN, en código: C1 es el que más ha facturado. Nunca el nombre ni el NIF.
CREATE TABLE clientes_paisan (
    cliente         VARCHAR(10) PRIMARY KEY,  -- C1, C2... (texto porque lleva la letra C)
    tipo_cliente    VARCHAR(30) NOT NULL,     -- empresa o asociación, extranjero, otro...
    vende_al_estado VARCHAR(2)  NOT NULL      -- sí/no
);

-- Una factura emitida por la PAISAN (e-fatura, 2013-2026). Las notas de crédito llevan la base en negativo.
CREATE TABLE facturas_paisan (
    id_factura INT           PRIMARY KEY,  -- número que pongo yo: no uso el número real de la factura
    cliente    VARCHAR(10)   NOT NULL,     -- clave foránea a clientes_paisan
    fecha      DATE          NOT NULL,
    ano        INT           NOT NULL,
    mes        INT           NOT NULL,
    tipo       VARCHAR(20)   NOT NULL,     -- Fatura o Nota de crédito
    base       DECIMAL(12,2) NOT NULL,     -- base imponible en euros, negativa en las notas de crédito
    FOREIGN KEY (cliente) REFERENCES clientes_paisan (cliente)
);

-- Los pedidos de la beira. (copiados de Airtable). origen_dato separa los registros reales del escenario.
CREATE TABLE encomendas_beira (
    encomenda          VARCHAR(20)   PRIMARY KEY,  -- código del pedido (ENC-2026-001, SIM-2026-001...)
    entidad            VARCHAR(120)  NOT NULL,
    tipo_entidad       VARCHAR(40)   NOT NULL,
    localidad          VARCHAR(60)   NULL,
    oferta             VARCHAR(20)   NOT NULL,     -- Equipas, Eventos o Trabalho
    fecha_adjudicacion DATE          NULL,         -- NULL si todavía no está adjudicado
    fecha_entrega      DATE          NULL,
    valor_vendido      DECIMAL(10,2) NOT NULL,     -- euros
    coste              DECIMAL(10,2) NOT NULL,     -- euros
    origen_dato        VARCHAR(20)   NOT NULL      -- registro real o escenario
);
