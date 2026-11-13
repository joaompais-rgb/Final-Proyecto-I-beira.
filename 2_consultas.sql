-- beira. en datos · consultas SQL (MySQL 8)
--
-- Son las mismas consultas de la sección 9 del notebook notebooks/beira_en_datos.ipynb, para ejecutarlas en MySQL Workbench.
-- Antes hay que crear y cargar la base de datos: lo hace esa sección 9 (ejecuta sql/1_esquema.sql e inserta los CSV de data/sql).
-- Las consultas del bloque 6 necesitan los datos internos (data/interno/sql).

USE beira;


-- ===========================================================================
-- 1. Consultas básicas: el tamaño del mercado
-- ===========================================================================

-- ¿Cuánto mercado público de ropa hay? COUNT, COUNT(DISTINCT), SUM, MIN y MAX.
SELECT COUNT(*) AS contratos,
       COUNT(DISTINCT comprador_nif) AS compradores,
       COUNT(DISTINCT proveedor_id) AS proveedores,
       ROUND(SUM(precio) / 1000000, 1) AS millones_eur,
       MIN(fecha) AS primera_fecha,
       MAX(fecha) AS ultima_fecha
FROM contratos;

-- ¿Crece? Contratos, compradores y gasto por año. GROUP BY y ORDER BY.
SELECT ano,
       COUNT(*) AS contratos,
       COUNT(DISTINCT comprador_nif) AS compradores,
       ROUND(SUM(precio) / 1000000, 1) AS millones_eur
FROM contratos
GROUP BY ano
ORDER BY ano;

-- ¿De qué tamaño son los contratos? CASE WHEN y una subconsulta para el porcentaje.
SELECT CASE WHEN precio < 5000 THEN '1. menos de 5.000 €'
            WHEN precio < 20000 THEN '2. de 5.000 a 20.000 €'
            WHEN precio < 75000 THEN '3. de 20.000 a 75.000 €'
            ELSE '4. 75.000 € o más' END AS tramo,
       COUNT(*) AS contratos,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM contratos), 1) AS pct
FROM contratos
GROUP BY tramo
ORDER BY tramo;

-- ¿Qué productos de ropa y fardamento se compran más? WHERE y HAVING.
SELECT producto,
       COUNT(*) AS contratos,
       ROUND(AVG(precio), 0) AS precio_medio
FROM contratos
WHERE ropa_fardamento = 'sí'
GROUP BY producto
HAVING COUNT(*) >= 50
ORDER BY contratos DESC;

-- ===========================================================================
-- 2. Joins: quién compra, dónde y cuándo
-- ===========================================================================

-- ¿Qué tipo de entidad compra más y cómo? JOIN con compradores.
SELECT com.tipo_comprador,
       COUNT(DISTINCT com.comprador_nif) AS compradores,
       COUNT(*) AS contratos,
       ROUND(SUM(con.precio) / 1000000, 1) AS millones_eur,
       ROUND(SUM(CASE WHEN con.procedimiento = 'ajuste directo' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 0) AS pct_ajuste_directo
FROM contratos AS con
JOIN compradores AS com ON com.comprador_nif = con.comprador_nif
GROUP BY com.tipo_comprador
ORDER BY contratos DESC;

-- Contratos de cada municipio, incluidos los que no tienen ninguno. LEFT JOIN e IFNULL.
SELECT mun.municipio,
       mun.piloto,
       mun.km_a_la_base,
       COUNT(DISTINCT com.comprador_nif) AS compradores,
       COUNT(con.idcontrato) AS contratos,
       ROUND(IFNULL(SUM(con.precio), 0), 0) AS importe_eur
FROM municipios AS mun
LEFT JOIN compradores AS com ON com.municipio = mun.municipio
LEFT JOIN contratos AS con ON con.comprador_nif = com.comprador_nif
GROUP BY mun.municipio, mun.piloto, mun.km_a_la_base
ORDER BY contratos DESC, mun.km_a_la_base;

-- ¿En qué meses firma cada tipo de comprador? JOIN y WHERE ... IN.
SELECT com.tipo_comprador,
       con.mes,
       COUNT(*) AS contratos
FROM contratos AS con
JOIN compradores AS com ON com.comprador_nif = con.comprador_nif
WHERE com.tipo_comprador IN ('escuela', 'camara', 'junta')
GROUP BY com.tipo_comprador, con.mes
ORDER BY com.tipo_comprador, con.mes;

-- H3: ¿qué organizaciones tienen contacto público? JOIN y SUM(CASE WHEN).
SELECT org.segmento,
       COUNT(*) AS organizaciones,
       SUM(CASE WHEN org.nivel_contacto = 'sin contacto' THEN 0 ELSE 1 END) AS con_contacto,
       ROUND(SUM(CASE WHEN org.nivel_contacto = 'sin contacto' THEN 0 ELSE 1 END) * 100.0 / COUNT(*), 0) AS pct_con_contacto,
       SUM(CASE WHEN mun.piloto = 'sí' THEN 1 ELSE 0 END) AS en_el_piloto
FROM organizaciones AS org
JOIN municipios AS mun ON mun.municipio = org.municipio
GROUP BY org.segmento
ORDER BY pct_con_contacto DESC;

-- ¿En qué meses hay fiestas y eventos? JOIN y WHERE ... IS NOT NULL.
SELECT eve.mes,
       COUNT(*) AS fiestas_y_eventos,
       SUM(CASE WHEN mun.piloto = 'sí' THEN 1 ELSE 0 END) AS en_el_piloto
FROM eventos AS eve
JOIN municipios AS mun ON mun.municipio = eve.municipio
WHERE eve.mes IS NOT NULL
GROUP BY eve.mes
ORDER BY eve.mes;

-- El precio medio de la región en salarios mínimos. JOIN de tres tablas.
SELECT con.ano,
       ind.salario_minimo,
       ROUND(AVG(con.precio), 0) AS precio_medio,
       ROUND(AVG(con.precio) / ind.salario_minimo, 1) AS precio_medio_en_salarios
FROM contratos AS con
JOIN compradores AS com ON com.comprador_nif = con.comprador_nif
JOIN indicadores_ano AS ind ON ind.ano = con.ano
WHERE com.municipio IS NOT NULL
GROUP BY con.ano, ind.salario_minimo
ORDER BY con.ano;

-- ===========================================================================
-- 3. Subconsultas: frente a quién compite la beira.
-- ===========================================================================

-- ¿Quién vende ya a las entidades de la lista? Subconsulta en el WHERE.
SELECT pro.tipo_proveedor,
       COUNT(DISTINCT con.proveedor_id) AS proveedores,
       COUNT(*) AS contratos,
       ROUND(SUM(con.precio), 0) AS importe_eur
FROM contratos AS con
JOIN proveedores AS pro ON pro.proveedor_id = con.proveedor_id
WHERE con.comprador_nif IN (SELECT comprador_nif FROM lista_beira)
GROUP BY pro.tipo_proveedor
ORDER BY contratos DESC;

-- ¿Domina algún proveedor la región? Subconsulta en el FROM.
SELECT COUNT(*) AS proveedores,
       SUM(contratos) AS contratos,
       MAX(contratos) AS contratos_del_mayor,
       ROUND(MAX(contratos) * 100.0 / SUM(contratos), 1) AS pct_del_mayor,
       SUM(CASE WHEN contratos = 1 THEN 1 ELSE 0 END) AS con_un_solo_contrato
FROM (SELECT con.proveedor_id,
             COUNT(*) AS contratos
      FROM contratos AS con
      JOIN compradores AS com ON com.comprador_nif = con.comprador_nif
      WHERE com.municipio IS NOT NULL
      GROUP BY con.proveedor_id) AS por_proveedor;

-- Contratos de la región por encima del precio medio del país. Subconsulta dentro de un CASE.
SELECT com.tipo_comprador,
       COUNT(*) AS contratos_de_la_region,
       SUM(CASE WHEN con.precio > (SELECT AVG(precio) FROM contratos) THEN 1 ELSE 0 END) AS por_encima_de_la_media_del_pais
FROM contratos AS con
JOIN compradores AS com ON com.comprador_nif = con.comprador_nif
WHERE com.municipio IS NOT NULL
GROUP BY com.tipo_comprador
ORDER BY contratos_de_la_region DESC;

-- ===========================================================================
-- 4. Vistas, tablas temporales y CTE: cómo compran y si vuelven
-- ===========================================================================

-- La vista contratos_region: los contratos de la región con su comprador y su municipio.
DROP VIEW IF EXISTS contratos_region;
CREATE VIEW contratos_region AS
SELECT con.idcontrato, con.fecha, con.ano, con.mes, con.precio, con.producto, con.grupo, con.procedimiento,
       con.plazo_dias, con.competidores, con.ropa_fardamento, con.proveedor_id,
       com.comprador_nif, com.comprador, com.tipo_comprador, com.en_lista,
       mun.municipio, mun.distrito, mun.piloto, mun.km_a_la_base
FROM contratos AS con
JOIN compradores AS com ON com.comprador_nif = con.comprador_nif
JOIN municipios AS mun ON mun.municipio = com.municipio;

-- ¿Cómo compran en la región? Consulta sobre la vista.
SELECT procedimiento,
       COUNT(*) AS contratos,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM contratos_region), 0) AS pct,
       ROUND(AVG(competidores), 1) AS competidores_medios,
       ROUND(AVG(precio), 0) AS precio_medio
FROM contratos_region
GROUP BY procedimiento
ORDER BY contratos DESC;

-- El calendario de las escuelas y las cámaras de la región. Consulta sobre la vista.
SELECT tipo_comprador,
       mes,
       COUNT(*) AS contratos
FROM contratos_region
WHERE tipo_comprador IN ('escuela', 'camara')
GROUP BY tipo_comprador, mes
ORDER BY tipo_comprador, mes;

-- Tabla temporal con las compras por comprador y año.
DROP TABLE IF EXISTS compras_ano;
CREATE TEMPORARY TABLE compras_ano AS
SELECT comprador_nif,
       ano,
       COUNT(*) AS contratos,
       SUM(precio) AS importe
FROM contratos
GROUP BY comprador_nif, ano;

-- ¿En cuántos años compra cada entidad? Consulta sobre la tabla temporal.
SELECT anos_con_compra,
       COUNT(*) AS compradores
FROM (SELECT comprador_nif,
             COUNT(*) AS anos_con_compra
      FROM compras_ano
      GROUP BY comprador_nif) AS por_comprador
GROUP BY anos_con_compra
ORDER BY anos_con_compra;

-- H1: quien compra un año, ¿vuelve al siguiente? Cuatro CTE encadenadas.
WITH anos AS (
    SELECT DISTINCT ano FROM contratos WHERE ano <= 2024
), primera AS (
    SELECT comprador_nif, MIN(ano) AS primer_ano FROM contratos GROUP BY comprador_nif
), compras AS (
    SELECT DISTINCT comprador_nif, ano FROM contratos
), pares AS (
    SELECT pri.comprador_nif,
           anos.ano,
           CASE WHEN este.comprador_nif IS NULL THEN 0 ELSE 1 END AS compra_este_ano,
           CASE WHEN sig.comprador_nif IS NULL THEN 0 ELSE 1 END AS compra_el_siguiente
    FROM primera AS pri
    JOIN anos ON anos.ano >= pri.primer_ano
    LEFT JOIN compras AS este ON este.comprador_nif = pri.comprador_nif AND este.ano = anos.ano
    LEFT JOIN compras AS sig ON sig.comprador_nif = pri.comprador_nif AND sig.ano = anos.ano + 1
)
SELECT compra_este_ano,
       COUNT(*) AS casos,
       SUM(compra_el_siguiente) AS vuelven,
       ROUND(SUM(compra_el_siguiente) * 100.0 / COUNT(*), 0) AS pct_vuelven
FROM pares
GROUP BY compra_este_ano
ORDER BY compra_este_ano;

-- ===========================================================================
-- 5. Funciones de ventana: fidelidad, proveedor nuevo y medianas
-- ===========================================================================

-- H1 año a año, con LEAD.
WITH compras AS (
    SELECT DISTINCT comprador_nif, ano FROM contratos
), con_siguiente AS (
    SELECT comprador_nif,
           ano,
           LEAD(ano) OVER (PARTITION BY comprador_nif ORDER BY ano) AS siguiente_compra
    FROM compras
)
SELECT ano,
       COUNT(*) AS compradores,
       SUM(CASE WHEN siguiente_compra = ano + 1 THEN 1 ELSE 0 END) AS vuelven,
       ROUND(SUM(CASE WHEN siguiente_compra = ano + 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 0) AS pct_vuelven
FROM con_siguiente
WHERE ano <= 2024
GROUP BY ano
ORDER BY ano;

-- ¿Repiten proveedor o prueban uno nuevo? Dos ROW_NUMBER.
WITH numerados AS (
    SELECT con.comprador_nif,
           com.en_lista,
           ROW_NUMBER() OVER (PARTITION BY con.comprador_nif ORDER BY con.fecha, con.idcontrato) AS compra_numero,
           ROW_NUMBER() OVER (PARTITION BY con.comprador_nif, con.proveedor_id ORDER BY con.fecha, con.idcontrato) AS vez_con_ese_proveedor
    FROM contratos AS con
    JOIN compradores AS com ON com.comprador_nif = con.comprador_nif
)
SELECT en_lista,
       COUNT(*) AS compras_despues_de_la_primera,
       SUM(CASE WHEN vez_con_ese_proveedor = 1 THEN 1 ELSE 0 END) AS a_un_proveedor_nuevo,
       ROUND(SUM(CASE WHEN vez_con_ese_proveedor = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 0) AS pct_proveedor_nuevo
FROM numerados
WHERE compra_numero > 1
GROUP BY en_lista
ORDER BY en_lista DESC;

-- Precio mediano por tipo de comprador. ROW_NUMBER y COUNT(*) OVER.
WITH ordenados AS (
    SELECT com.tipo_comprador,
           con.precio,
           ROW_NUMBER() OVER (PARTITION BY com.tipo_comprador ORDER BY con.precio) AS posicion,
           COUNT(*) OVER (PARTITION BY com.tipo_comprador) AS total
    FROM contratos AS con
    JOIN compradores AS com ON com.comprador_nif = con.comprador_nif
)
SELECT tipo_comprador,
       total AS contratos,
       ROUND(AVG(precio), 0) AS precio_mediano
FROM ordenados
WHERE posicion * 2 BETWEEN total AND total + 2
GROUP BY tipo_comprador, total
ORDER BY precio_mediano;

-- Las tres entidades fieles más cercanas de cada distrito. RANK.
WITH ordenadas AS (
    SELECT mun.distrito,
           com.comprador,
           com.tipo_comprador,
           mun.municipio,
           mun.km_a_la_base,
           lis.grupo_compra,
           lis.mes_habitual,
           lis.procedimiento_habitual,
           RANK() OVER (PARTITION BY mun.distrito ORDER BY mun.km_a_la_base, lis.contratos DESC) AS posicion
    FROM lista_beira AS lis
    JOIN compradores AS com ON com.comprador_nif = lis.comprador_nif
    JOIN municipios AS mun ON mun.municipio = com.municipio
    WHERE lis.grupo_compra = 'A. fiel'
)
SELECT distrito, posicion, comprador, tipo_comprador, municipio, km_a_la_base, mes_habitual, procedimiento_habitual
FROM ordenadas
WHERE posicion <= 3
ORDER BY distrito, posicion;

-- ===========================================================================
-- 6. La PAISAN y la beira. (datos internos)
-- ===========================================================================

-- H4: la vista concentracion_paisan, con el peso de los tres mayores clientes de cada año.
DROP VIEW IF EXISTS concentracion_paisan;
CREATE VIEW concentracion_paisan AS
WITH cliente_ano AS (
    SELECT ano, cliente, SUM(base) AS facturado
    FROM facturas_paisan
    GROUP BY ano, cliente
), ordenados AS (
    SELECT ano,
           cliente,
           facturado,
           ROW_NUMBER() OVER (PARTITION BY ano ORDER BY facturado DESC) AS posicion,
           SUM(facturado) OVER (PARTITION BY ano) AS facturacion_ano
    FROM cliente_ano
)
SELECT ano,
       MAX(facturacion_ano) AS facturacion,
       SUM(facturado) AS tres_mayores,
       ROUND(SUM(facturado) * 100.0 / MAX(facturacion_ano), 0) AS pct_tres_mayores
FROM ordenados
WHERE posicion <= 3
GROUP BY ano;
SELECT ano,
       ROUND(facturacion, 0) AS facturacion,
       ROUND(tres_mayores, 0) AS tres_mayores,
       pct_tres_mayores
FROM concentracion_paisan
ORDER BY ano;

-- La facturación mes a mes: acumulado del año (SUM OVER) y variación con el mes anterior (LAG).
WITH mensual AS (
    SELECT ano, mes, SUM(base) AS facturacion, COUNT(*) AS facturas_mes
    FROM facturas_paisan
    GROUP BY ano, mes
), con_ventanas AS (
    SELECT ano,
           mes,
           facturacion,
           facturas_mes,
           SUM(facturacion) OVER (PARTITION BY ano ORDER BY mes) AS acumulado_del_ano,
           LAG(facturacion) OVER (ORDER BY ano, mes) AS mes_anterior
    FROM mensual
)
SELECT ano,
       mes,
       ROUND(facturacion, 0) AS facturacion,
       facturas_mes,
       ROUND(acumulado_del_ano, 0) AS acumulado_del_ano,
       ROUND((facturacion - mes_anterior) * 100.0 / mes_anterior, 0) AS variacion_pct
FROM con_ventanas
WHERE ano >= 2025
ORDER BY ano, mes;

-- ¿Cuánto cabe en la fábrica? Lo que le falta a cada mes para llegar al mejor de los últimos doce. MAX() OVER ().
WITH mensual AS (
    SELECT ano, mes, SUM(base) AS facturacion
    FROM facturas_paisan
    GROUP BY ano, mes
), doce AS (
    SELECT ano, mes, facturacion
    FROM mensual
    WHERE ano * 12 + mes > (SELECT MAX(ano * 12 + mes) FROM mensual) - 12
)
SELECT ano,
       mes,
       ROUND(facturacion, 0) AS facturacion,
       ROUND(MAX(facturacion) OVER (), 0) AS mejor_mes,
       ROUND(MAX(facturacion) OVER () - facturacion, 0) AS hueco
FROM doce
ORDER BY ano, mes;

-- H5: ¿qué clientes vuelven al año siguiente, por tipo? LEAD y JOIN.
WITH compras AS (
    SELECT DISTINCT cliente, ano FROM facturas_paisan
), con_siguiente AS (
    SELECT cliente,
           ano,
           LEAD(ano) OVER (PARTITION BY cliente ORDER BY ano) AS siguiente_compra
    FROM compras
)
SELECT cli.tipo_cliente,
       COUNT(*) AS clientes_ano,
       SUM(CASE WHEN sig.siguiente_compra = sig.ano + 1 THEN 1 ELSE 0 END) AS vuelven,
       ROUND(SUM(CASE WHEN sig.siguiente_compra = sig.ano + 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 0) AS pct_vuelven
FROM con_siguiente AS sig
JOIN clientes_paisan AS cli ON cli.cliente = sig.cliente
WHERE sig.ano IN (2013, 2014, 2015, 2016, 2017, 2018, 2022, 2023, 2024)
GROUP BY cli.tipo_cliente
ORDER BY clientes_ano DESC;

-- Los pedidos de la beira., separando los registros reales del escenario.
SELECT origen_dato,
       COUNT(*) AS pedidos,
       ROUND(SUM(valor_vendido), 2) AS vendido,
       ROUND(SUM(coste), 2) AS coste,
       ROUND((SUM(valor_vendido) - SUM(coste)) * 100.0 / SUM(valor_vendido), 1) AS margen_pct,
       ROUND(AVG(valor_vendido), 0) AS pedido_medio
FROM encomendas_beira
GROUP BY origen_dato
ORDER BY origen_dato DESC;

-- ¿Qué parte del objetivo anual lleva la beira.? Subconsulta sobre la vista y CROSS JOIN.
SELECT ped.origen_dato,
       ROUND(SUM(ped.valor_vendido), 0) AS vendido,
       ROUND(MAX(obj.objetivo), 0) AS objetivo_anual,
       ROUND(SUM(ped.valor_vendido) * 100.0 / MAX(obj.objetivo), 1) AS pct_del_objetivo
FROM encomendas_beira AS ped
CROSS JOIN (SELECT tres_mayores / 0.80 - facturacion AS objetivo
            FROM concentracion_paisan
            WHERE ano = 2025) AS obj
GROUP BY ped.origen_dato
ORDER BY ped.origen_dato DESC;
