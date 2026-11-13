# beira. en datos

Proyecto final · Case Study 2 (Data Analytics) · Ironhack Data Analytics · João Miguel Pais

La **beira.** es una marca de ropa personalizada que nace de la PAISAN Confecções, la empresa de mi familia en Oliveira do Hospital, que confecciona ropa desde 2011 (el oficio textil de la familia Pais viene de tres generaciones). Tiene tres ofertas: Equipas, Trabalho y Eventos. Está arrancando: pocos clientes y todavía sin histórico propio.

## Objetivo

> **La PAISAN depende de tres clientes. Decidir, con datos, a quién debe dirigirse la beira. para traerle clientes propios, cómo y cuándo llegar a ellos, y cuánto trabajo nuevo cabe en la fábrica.**

El plan está en [`OBJETIVO.md`](OBJETIVO.md) (en portugués, [`OBJETIVO_PT.md`](OBJETIVO_PT.md)). Versión en portugués de este archivo: [`README_PT.md`](README_PT.md).

## Las tres piezas

| Pieza | Dónde | Qué hace |
|---|---|---|
| 1. Análisis en Python y SQL | [`notebooks/beira_en_datos.ipynb`](notebooks/beira_en_datos.ipynb), con [`src/`](src/) y [`sql/`](sql/) | un solo notebook: limpia los datos, hace el análisis y las pruebas de hipótesis (H1 a H6), saca la lista de 63 entidades, prepara las tablas, crea la base `beira` en MySQL (11 tablas con claves primarias y foráneas), la carga y responde con SQL: básicas, joins, subconsultas, vista, tabla temporal, CTE y funciones de ventana. Las consultas también están en [`sql/2_consultas.sql`](sql/2_consultas.sql) para MySQL Workbench |
| 2. Dashboard | [`tableau/beira_en_datos.twb`](tableau/beira_en_datos.twb) | dos paneles de Tableau (el mercado público de ropa y la lista de la beira.) y una historia de tres puntos que los recorre |
| 3. App | [`app/app.py`](app/app.py), [`app/backend.py`](app/backend.py) | app de Streamlit con cinco páginas: cómo usarla, a quién dirigirse, el mercado, la PAISAN (con un «¿y si la beira. vende...?» y la cuenta en piezas) y los pedidos de la beira. Cada gráfico lleva «Cómo leerlo» y «Qué decidir con esto» |

Las tres trabajan con las mismas tablas: el notebook las guarda en `data/sql/` y en `tableau/`, y si cambia un dato basta con volver a ejecutarlo.

| El mercado público (Tableau) | A quién dirigirse (Tableau) | La app (Streamlit) |
|---|---|---|
| ![Panel 1 de Tableau](presentacion/capturas/tableau_1_mercado.png) | ![Panel 2 de Tableau](presentacion/capturas/tableau_2_quien.png) | ![Página «A quién dirigirse» de la app](presentacion/capturas/app_quien.jpg) |

## Resultados

| | Hipótesis | Resultado |
|---|---|---|
| H1 | Quien compra ropa un año vuelve a comprar el siguiente | **Se cumple:** 62 % frente a 29 % (chi2, p < 0,001; V = 0,32), todos los años. Solo con ropa y fardamento: 53 % frente a 27 % |
| H2 | Las prendas de equipo se compran sobre todo de mayo a septiembre | **Se cumple**, con efecto pequeño: 58 % frente a 43 % (V = 0,08) |
| H3 | Clubes y asociaciones publican menos contacto que las escuelas | **Se cumple:** 18 % frente a 85 % (V = 0,56) |
| H4 | La PAISAN depende de pocos clientes | **Se cumple:** los tres mayores suman de media el 86,6 % de la facturación de cada año (t de una muestra contra el 80 %, p = 0,001); en 2025, el 93 % |
| H5 | Los clientes de la PAISAN que compran un año vuelven al siguiente | **Se cumple:** 67 % frente a 4 % (V = 0,67) |
| H6 | La factura mediana subió menos que el salario mínimo | **Se cumple:** +65 % frente a +79 %; la factura mediana pasa de 1,67 a 1,55 salarios mínimos |

- **A quién dirigirse.** 63 entidades públicas de los 66 municipios compran ropa en dos años o más; 34 son fieles (en su grupo vuelve a comprar el 80 %). Abre la lista el Agrupamento de Escolas de Arganil, a 22 km. La lista está en [`resultados/lista_entidades_beira_ampliada.csv`](resultados/lista_entidades_beira_ampliada.csv).
- **Cómo.** En la región, el 48 % de los contratos es ajuste directo (la entidad elige a una sola empresa) y el 39 % consulta previa. Las escuelas y las juntas compran sobre todo por ajuste directo: hay que darse a conocer antes del pedido.
- **Frente a quién.** Nadie domina: 268 proveedores para 542 contratos, el mayor con el 5 %. En la lista, el 59 % de las compras repetidas va a un proveedor nuevo.
- **Cuándo.** Las escuelas de la región firman en abril y mayo (37 %) y de octubre a diciembre (48 %); las fiestas se concentran de junio a septiembre (71 %).
- **Qué pedidos.** El 77 % de los contratos es de menos de 20.000 €; las escuelas, 3.200 € de mediana.
- **Cuánto cabe.** Si todos los meses llegaran al nivel del mejor mes, en la PAISAN cabrían unos 194.000 € más al año.
- **Cuánto hace falta.** Para que los tres mayores clientes bajen al 80 %, la beira. tendría que facturar unos 83.000 € al año, cerca de 980 piezas al mes al precio típico de las empresas de personalización (7 €). Cabe en la fábrica.
- **Cuándo cabe.** La PAISAN factura menos en junio y julio, justo cuando se produce para las fiestas (el 71 %, de mayo a agosto): fiestas y asociaciones son el cliente que mejor encaja con su calendario.
- **Predicción.** En la parte A no hace falta un modelo: una regla simple (el grupo de compra) basta para ordenar la lista. Para la facturación mensual de la PAISAN, el gradient boosting falla 9.400 € de media, frente a 12.900 € de la mejor regla simple.

## Estructura

```text
beira-em-dados/
├── README.md / README_PT.md
├── OBJETIVO.md / OBJETIVO_PT.md      objetivo y plan
├── requirements.txt
├── notebooks/
│   └── beira_en_datos.ipynb          el notebook: análisis en Python, base de datos y consultas SQL
├── sql/
│   ├── 1_esquema.sql                 crea la base de datos y las 11 tablas (tipos, claves y NOT NULL comentados columna a columna)
│   ├── diagrama_eer.png              diagrama entidad-relación: columnas, tipos, PK, FK y relaciones 1 a N
│   └── 2_consultas.sql               las consultas, para MySQL Workbench
├── src/
│   ├── config.py                     valores fijos: carpetas, colores, umbrales y palabras de las reglas
│   ├── funciones.py                  las funciones del notebook (leer, revisar, limpiar...), para reutilizarlas
│   └── base_datos.py                 las funciones del notebook para crear, cargar y consultar la base
├── app/
│   ├── app.py                        la app de Streamlit
│   ├── backend.py                    datos, filtros y gráficos de la app
│   └── .streamlit/config.toml        colores de la marca
├── tableau/
│   ├── beira_en_datos.twb            los dos paneles y la historia
│   ├── GUIA_PANEL.md                 qué lleva cada hoja
│   └── contratos_tableau.csv, lista_tableau.csv
├── data/
│   ├── clean/      datos limpios de entrada (contratos, organizaciones, municipios, eventos, indicadores...)
│   ├── sql/        las ocho tablas públicas de la base de datos, en CSV (las guarda el notebook)
│   └── interno/    facturación de la PAISAN y pedidos de la beira. (no se sube a GitHub)
├── resultados/     la lista de 63 entidades
└── presentacion/   las diapositivas en PDF y capturas del panel y de la app
```

## Cómo ejecutarlo

1. `pip install -r requirements.txt`
2. **Notebook.** Arrancar MySQL, abrir `notebooks/beira_en_datos.ipynb` y ejecutar todas las celdas. Guarda las tablas en `data/sql/`, `tableau/` y `resultados/`; en la sección 9 pide la contraseña del usuario de MySQL que está en `src/config.py` (`USUARIO_MYSQL`), crea la base `beira`, la carga y hace las consultas. Las secciones 1 a 8 no necesitan MySQL. Las mismas consultas se pueden ejecutar en MySQL Workbench con `sql/2_consultas.sql`.
3. **Tableau.** Abrir `tableau/beira_en_datos.twb`. Si Tableau pregunta dónde están los datos, están en la misma carpeta (`contratos_tableau.csv` y `lista_tableau.csv`).
4. **App.** En una terminal, entrar en la carpeta `app` y ejecutar `streamlit run app.py`.

Sin la carpeta `data/interno/` (que no se sube a GitHub) no se puede ejecutar la sección 7 del notebook, la de la PAISAN; las salidas guardadas en el notebook y en `presentacion/` enseñan el resultado. La app funciona en sus tres primeras páginas y avisa en las otras dos.

## La base de datos

```text
municipios (municipio)
   ├── compradores (comprador_nif) ──┬── contratos (idcontrato) ── proveedores (proveedor_id)
   │                                 └── lista_beira (comprador_nif)
   ├── organizaciones (id_organizacion)
   └── eventos (id_evento)
indicadores_ano (ano)

clientes_paisan (cliente) ── facturas_paisan (id_factura)        datos internos
encomendas_beira (encomenda)                                     datos internos
```

![Diagrama entidad-relación de la base de datos](sql/diagrama_eer.png)

**Cómo llegan los datos a MySQL.** [`sql/1_esquema.sql`](sql/1_esquema.sql) crea la base y las 11 tablas: cada tabla tiene su PRIMARY KEY, las FOREIGN KEY hacia su tabla madre, NOT NULL en los campos obligatorios y un comentario que explica el tipo de cada columna (BIGINT para el NIF, DECIMAL(12,2) para el dinero, DATE para las fechas...). En la sección 9 del notebook, `ejecutar_script` ejecuta ese archivo con `mysql.connector` y `cargar_tabla` inserta cada CSV de `data/sql/` con `INSERT INTO ... VALUES` (`executemany` y `commit`), primero las tablas madre y después las hijas. Al final, `SELECT COUNT(*)` y un `assert` comprueban que cada tabla tiene en MySQL las mismas filas que su CSV. El diagrama se generó a partir del propio `1_esquema.sql`, porque MySQL Workbench 26 ya no trae el modelador EER; las mismas relaciones se ven en Workbench (Foreign Keys de cada tabla o `SHOW CREATE TABLE`).

Los proveedores sin NIF público llevan un código (SN1, SN2...) en lugar de su nombre, y los clientes de la PAISAN van en código (C1, C2...): en el proyecto no hay NIF de clientes ni números de factura.

## Datos

| Fuente | Qué aporta | Licencia |
|---|---|---|
| [Portal BASE, contratos](https://dados.gov.pt/datasets/contratos-publicos-portal-base-impic-contratos-de-2012-a-2026) | 6.382 contratos públicos de ropa de todo el país, 2020-2025; contratos de 2013-2015 y anuncios de concursos de la región | other-pd, según dados.gov.pt |
| [OpenStreetMap](https://www.openstreetmap.org) (proyecto 1) | 1.596 organizaciones de la región con su contacto público | ODbL (© colaboradores de OpenStreetMap) |
| Proyecto 1 de la Unit 4 | 66 municipios con su distancia a la PAISAN, competencia por municipio y 136 fiestas y eventos | ver el README del proyecto 1 |
| [INE](https://www.ine.pt) | alumnos por municipio, empresas por municipio e IPC de la ropa | condiciones del INE |
| [PORDATA](https://www.pordata.pt/en/Portugal/National+minimum+wage-74) | salario mínimo nacional | condiciones de PORDATA |
| Precios de personalización | 32 precios públicos de 7 fuentes portuguesas, como referencia de mercado | páginas públicas citadas en el archivo |
| Facturación de la PAISAN | 3.375 facturas de 2013 a 2026 (e-fatura), con los clientes en código | interna, no se sube |
| Pedidos de la beira. | pedidos copiados de Airtable: 3 registros reales y un escenario de 19 ventas, marcados en la columna `origen_dato` | interna, no se sube |

**Regla fija:** la Junta de Freguesia de Alvoco das Várzeas se excluye de todas las listas (conflicto de intereses).

## Límites

- El Portal BASE solo tiene compras públicas, y muchas compras pequeñas no se publican: el mercado pequeño está infravalorado.
- En la región los números son pequeños (113 compradores, 542 contratos): las conclusiones regionales son orientativas.
- La regla que separa la ropa y el fardamento todavía no se ha medido con etiquetas puestas a mano.
- El e-fatura no trae líneas de factura: la parte de la PAISAN mide euros facturados, no piezas ni margen. Las descargas de 2020 y 2021 están incompletas.
- Los pedidos de la beira. son tres registros reales y un escenario: sirven para enseñar cómo se seguirá el objetivo, no para sacar conclusiones.

## Presentación

8 minutos, con demostración en directo de la historia de Tableau y de la app.

- Copia en PDF: [`presentacion/beira_en_datos_presentacion.pdf`](presentacion/beira_en_datos_presentacion.pdf)
