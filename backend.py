# backend.py
"""Datos, filtros, resúmenes y gráficos de la app «beira. en datos».

La app (app.py) solo enseña lo que devuelven estas funciones, como en la lección de Streamlit.
Lee las mismas tablas que usa la base de datos: las guarda el notebook beira_en_datos.ipynb en data/sql/.
"""
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

DATOS = "../data/sql/"
INTERNOS = "../data/interno/sql/"
COLORES = {"verde_serra": "#404020", "terracota": "#96422C", "ambar": "#8F6226", "gris": "#9A958C"}
ANO_BASE = 2025        # último año completo de la facturación de la PAISAN
OBJETIVO = 0.80        # peso de los tres mayores clientes al que se quiere bajar


# ---------------------------------------------------------------- leer los datos

def leer(nombre, carpeta=DATOS):
    """Lee un CSV de la carpeta y pasa los nombres de las columnas a minúsculas."""
    tabla = pd.read_csv(carpeta + nombre + ".csv")
    tabla.columns = tabla.columns.str.lower()
    return tabla


def cargar_lista():
    """Las 63 entidades de la lista de la beira., con el nombre, el tipo y el municipio de cada una."""
    lista = leer("lista_beira").merge(leer("compradores"), on="comprador_nif").merge(leer("municipios"), on="municipio")
    return lista.sort_values(["grupo_compra", "km_a_la_base"]).reset_index(drop=True)


def cargar_contratos():
    """Los contratos públicos de ropa, con el nombre, el tipo y el municipio de su comprador."""
    contratos = leer("contratos").merge(leer("compradores"), on="comprador_nif")
    contratos["municipio"] = contratos["municipio"].fillna("")
    return contratos


def cargar_facturas():
    """Las facturas de la PAISAN (datos internos), con el cliente en código."""
    return leer("facturas_paisan", INTERNOS)


def cargar_pedidos():
    """Los pedidos de la beira. copiados de Airtable (datos internos)."""
    pedidos = leer("encomendas_beira", INTERNOS)
    pedidos["fecha_adjudicacion"] = pd.to_datetime(pedidos["fecha_adjudicacion"])
    pedidos["mes"] = pedidos["fecha_adjudicacion"].dt.month
    return pedidos


# ---------------------------------------------------------------- página 1: a quién dirigirse

def filtrar_lista(lista, grupos, tipos, km_max, solo_ropa):
    """Se queda con las entidades que cumplen los filtros de la barra lateral."""
    tabla = lista[lista["km_a_la_base"] <= km_max]
    if grupos:
        tabla = tabla[tabla["grupo_compra"].isin(grupos)]
    if tipos:
        tabla = tabla[tabla["tipo_comprador"].isin(tipos)]
    if solo_ropa:
        tabla = tabla[tabla["compra_ropa_fardamento"] == "sí"]
    return tabla


def para_ver(tabla):
    """Prepara una tabla para st.table: los números enteros sin decimales y los demás con un decimal y coma decimal."""
    tabla = tabla.copy()
    for columna in tabla.select_dtypes("number").columns:
        valores = tabla[columna]
        if valores.notna().all() and (valores % 1 == 0).all():
            tabla[columna] = valores.round(0).astype(int)
        else:
            tabla[columna] = valores.round(1).astype(str).str.replace(".", ",", regex=False)
    return tabla


def resumen_lista(tabla):
    """Una fila con lo principal de las entidades filtradas."""
    return pd.DataFrame({
        "entidades": [len(tabla)],
        "fieles": [(tabla["grupo_compra"] == "A. fiel").sum()],
        "compran ropa o fardamento": [(tabla["compra_ropa_fardamento"] == "sí").sum()],
        "por ajuste directo": [(tabla["procedimiento_habitual"] == "ajuste directo").sum()],
        "precio mediano (€)": [round(tabla["precio_mediano"].median())],
        "distancia mediana (km)": [round(tabla["km_a_la_base"].median())]})


def tabla_lista(tabla):
    """Las columnas que hacen falta para preparar cada contacto, con nombres para leer."""
    columnas = ["comprador", "tipo_comprador", "municipio", "km_a_la_base", "grupo_compra", "mes_habitual",
                "procedimiento_habitual", "precio_mediano", "contratos", "ultimo_ano", "proveedores_distintos",
                "compra_ropa_fardamento", "publica_concursos"]
    salida = tabla[columnas].copy()
    salida["precio_mediano"] = salida["precio_mediano"].round(0)
    salida.columns = ["entidad", "tipo", "municipio", "km", "grupo", "mes habitual", "cómo compra", "precio mediano (€)",
                      "contratos", "último año", "proveedores distintos", "ropa o fardamento", "publica concursos"]
    return salida


def grafico_meses(tabla):
    """Barras con cuántas entidades tienen cada mes como mes habitual de compra."""
    conteo = tabla.groupby("mes_habitual").size().reset_index()
    conteo.columns = ["mes", "entidades"]
    meses = pd.DataFrame({"mes": range(1, 13)}).merge(conteo, on="mes", how="left").fillna(0)
    fig, ax = plt.subplots(figsize=(6, 3.2))
    sns.barplot(data=meses, x="mes", y="entidades", color=COLORES["verde_serra"], ax=ax)
    plt.xlabel("mes habitual de compra")
    plt.ylabel("entidades")
    plt.tight_layout()
    return fig


def grafico_mapa(tabla):
    """Los 66 municipios por su posición; el punto crece con las entidades filtradas que tiene."""
    municipios = leer("municipios")
    conteo = tabla.groupby("municipio").size().reset_index()
    conteo.columns = ["municipio", "entidades"]
    con_entidades = municipios.merge(conteo, on="municipio")
    base = municipios[municipios["municipio"] == "Oliveira do Hospital"]
    fig, ax = plt.subplots(figsize=(6, 3.2))
    sns.scatterplot(data=municipios, x="lon", y="lat", color=COLORES["gris"], s=15, ax=ax)
    sns.scatterplot(data=con_entidades, x="lon", y="lat", size="entidades", sizes=(40, 300), color=COLORES["verde_serra"], legend=False, ax=ax)
    sns.scatterplot(data=base, x="lon", y="lat", color=COLORES["terracota"], s=90, marker="s", label="PAISAN (Oliveira do Hospital)", ax=ax)
    plt.xlabel("longitud")
    plt.ylabel("latitud")
    plt.tight_layout()
    return fig


# ---------------------------------------------------------------- página 2: el mercado

def filtrar_contratos(contratos, lista, ano_min, ano_max, ambito, tipos, solo_ropa):
    """Se queda con los contratos de los años, el ámbito y los tipos de comprador elegidos."""
    tabla = contratos[(contratos["ano"] >= ano_min) & (contratos["ano"] <= ano_max)]
    if ambito == "la región":
        tabla = tabla[tabla["municipio"] != ""]
    if ambito == "la lista de la beira.":
        tabla = tabla[tabla["comprador_nif"].isin(lista["comprador_nif"])]
    if tipos:
        tabla = tabla[tabla["tipo_comprador"].isin(tipos)]
    if solo_ropa:
        tabla = tabla[tabla["ropa_fardamento"] == "sí"]
    return tabla


def resumen_mercado(tabla):
    """Una fila con el tamaño del mercado filtrado."""
    return pd.DataFrame({
        "contratos": [len(tabla)],
        "compradores": [tabla["comprador_nif"].nunique()],
        "proveedores": [tabla["proveedor_id"].nunique()],
        "gasto (M€)": [round(tabla["precio"].sum() / 1000000, 1)],
        "precio mediano (€)": [round(tabla["precio"].median())],
        "% de menos de 20.000 €": [round((tabla["precio"] < 20000).mean() * 100)],
        "% por ajuste directo": [round((tabla["procedimiento"] == "ajuste directo").mean() * 100)]})


def grafico_por_ano(tabla):
    """Barras con los contratos de cada año."""
    por_ano = tabla.groupby("ano").size().reset_index()
    por_ano.columns = ["ano", "contratos"]
    fig, ax = plt.subplots(figsize=(6, 3.2))
    sns.barplot(data=por_ano, x="ano", y="contratos", color=COLORES["verde_serra"], ax=ax)
    plt.xlabel("")
    plt.ylabel("contratos")
    plt.tight_layout()
    return fig


def grafico_calendario(tabla):
    """Barras con el % de los contratos que se firma cada mes."""
    por_mes = tabla.groupby("mes").size().reset_index()
    por_mes.columns = ["mes", "contratos"]
    por_mes = pd.DataFrame({"mes": range(1, 13)}).merge(por_mes, on="mes", how="left").fillna(0)
    por_mes["pct"] = por_mes["contratos"] / por_mes["contratos"].sum() * 100
    fig, ax = plt.subplots(figsize=(6, 3.2))
    sns.barplot(data=por_mes, x="mes", y="pct", color=COLORES["terracota"], ax=ax)
    plt.xlabel("mes de la firma")
    plt.ylabel("% de los contratos")
    plt.tight_layout()
    return fig


def tabla_procedimientos(tabla):
    """Cómo se compra: contratos, %, competidores medios y precio mediano de cada procedimiento."""
    grupo = tabla.groupby("procedimiento")
    salida = pd.concat([grupo.size(), grupo["competidores"].mean().round(1), grupo["precio"].median().round(0)], axis=1)
    salida.columns = ["contratos", "competidores medios", "precio mediano (€)"]
    salida["% de los contratos"] = (salida["contratos"] / len(tabla) * 100).round(0)
    return salida.sort_values("contratos", ascending=False)


def tabla_compradores(tabla):
    """Los compradores con más contratos entre los filtrados."""
    grupo = tabla.groupby(["comprador", "tipo_comprador", "municipio"])
    salida = pd.concat([grupo.size(), grupo["precio"].median().round(0), grupo["ano"].max()], axis=1).reset_index()
    salida.columns = ["entidad", "tipo", "municipio", "contratos", "precio mediano (€)", "último año"]
    return salida.sort_values("contratos", ascending=False).head(25).reset_index(drop=True)


# ---------------------------------------------------------------- página 3: la PAISAN

def concentracion(facturas):
    """Para cada año: facturación, lo que suman los tres mayores clientes y su peso en %."""
    cliente_ano = facturas.groupby(["ano", "cliente"])["base"].sum().reset_index()
    cliente_ano = cliente_ano.sort_values(["ano", "base"], ascending=[True, False])
    tres = cliente_ano.groupby("ano").head(3).groupby("ano")["base"].sum()
    tabla = pd.DataFrame({"facturacion": cliente_ano.groupby("ano")["base"].sum(), "tres_mayores": tres})
    tabla["pct_tres_mayores"] = (tabla["tres_mayores"] / tabla["facturacion"] * 100).round(0)
    return tabla.reset_index()


def grafico_concentracion(tabla):
    """Barras con el peso de los tres mayores clientes de cada año y la línea del 80 %."""
    fig, ax = plt.subplots(figsize=(8, 3.2))
    sns.barplot(data=tabla, x="ano", y="pct_tres_mayores", color=COLORES["verde_serra"], ax=ax)
    plt.plot([-0.5, len(tabla) - 0.5], [OBJETIVO * 100, OBJETIVO * 100], color=COLORES["terracota"], linestyle="--")
    plt.xlabel("")
    plt.ylabel("% en los tres mayores clientes")
    plt.tight_layout()
    return fig


def ultimos_doce(facturas):
    """La facturación de los últimos doce meses y lo que le falta a cada mes para llegar al mejor."""
    mensual = facturas.groupby(["ano", "mes"])["base"].agg(["sum", "size"]).reset_index()
    mensual.columns = ["ano", "mes", "facturacion", "facturas_mes"]
    mensual["periodo"] = mensual["ano"] * 12 + mensual["mes"]
    doce = mensual[mensual["periodo"] > mensual["periodo"].max() - 12].copy()
    doce["hueco"] = doce["facturacion"].max() - doce["facturacion"]
    doce["mes_ano"] = doce["mes"].astype(str) + "/" + doce["ano"].astype(str)
    return doce[["mes_ano", "facturacion", "facturas_mes", "hueco"]].round(0)


def grafico_doce(doce):
    """Barras con la facturación de los últimos doce meses y la línea del mejor mes."""
    fig, ax = plt.subplots(figsize=(8, 3.2))
    sns.barplot(data=doce, x="mes_ano", y="facturacion", color=COLORES["gris"], ax=ax)
    plt.plot([-0.5, len(doce) - 0.5], [doce["facturacion"].max(), doce["facturacion"].max()], color=COLORES["terracota"], linestyle="--")
    plt.xticks(rotation=45)
    plt.xlabel("")
    plt.ylabel("facturación del mes (€)")
    plt.tight_layout()
    return fig


def calendario_encaje(facturas):
    """% del año que cae en cada mes: facturación de la PAISAN (2022-2025), fiestas (en su mes de producción) y escuelas de la región."""
    completos = facturas[facturas["ano"].isin([2022, 2023, 2024, 2025])]
    fabrica = completos.groupby("mes")["base"].sum()
    tabla = pd.DataFrame({"mes": range(1, 13)})
    tabla["fabrica"] = tabla["mes"].map(fabrica / fabrica.sum() * 100).round(1)
    eventos = leer("eventos")
    produccion = (eventos["mes"].dropna() - 2) % 12 + 1   # se produce el mes antes de la fiesta
    tabla["fiestas"] = tabla["mes"].map(produccion.value_counts() / len(produccion) * 100).fillna(0).round(1)
    contratos = cargar_contratos()
    escuelas = contratos[(contratos["municipio"] != "") & (contratos["tipo_comprador"] == "escuela")]
    tabla["escuelas"] = tabla["mes"].map(escuelas["mes"].value_counts() / len(escuelas) * 100).fillna(0).round(1)
    return tabla


def grafico_encaje(tabla):
    """Tres líneas en % del año: cuándo factura la PAISAN, cuándo se produce para las fiestas y cuándo compran las escuelas."""
    largo = tabla.melt(id_vars="mes", value_vars=["fabrica", "fiestas", "escuelas"], var_name="serie", value_name="pct")
    largo["serie"] = largo["serie"].map({"fabrica": "facturación de la PAISAN", "fiestas": "fiestas (mes de producción)", "escuelas": "contratos de escuelas"})
    fig, ax = plt.subplots(figsize=(8, 3.2))
    sns.lineplot(data=largo, x="mes", y="pct", hue="serie", marker="o",
                 palette=[COLORES["verde_serra"], COLORES["terracota"], COLORES["ambar"]], ax=ax)
    plt.xticks(range(1, 13))
    plt.ylabel("% del año")
    plt.tight_layout()
    return fig


def objetivo_beira(tabla_concentracion):
    """Cuánto tendría que facturar la beira. al año para que los tres mayores clientes bajen al 80 %."""
    base = tabla_concentracion[tabla_concentracion["ano"] == ANO_BASE]
    tres = base["tres_mayores"].sum()
    total = base["facturacion"].sum()
    return tres, total, tres / OBJETIVO - total


def peso_con_beira(tres, total, ventas_beira):
    """El peso de los tres mayores clientes si la beira. añade esas ventas a la facturación."""
    return tres / (total + ventas_beira) * 100


def resumen_escenario(ventas_beira, peso, necesario, hueco):
    """Una fila con el escenario elegido en el deslizador."""
    return pd.DataFrame({
        "ventas de la beira. (€)": [ventas_beira],
        "peso de los tres mayores (%)": [round(peso, 1)],
        "hace falta para llegar al 80 % (€)": [round(necesario)],
        "hueco en la fábrica (€)": [round(hueco)]})


# ---------------------------------------------------------------- página 4: la beira. hoy

def filtrar_pedidos(pedidos, con_escenario):
    """Los registros reales y, si se pide, también el escenario de ventas."""
    if con_escenario:
        return pedidos
    return pedidos[pedidos["origen_dato"] == "registro real"]


def resumen_pedidos(tabla):
    """Una fila con lo vendido, el coste y el margen de los pedidos."""
    vendido = tabla["valor_vendido"].sum()
    coste = tabla["coste"].sum()
    return pd.DataFrame({
        "pedidos": [len(tabla)],
        "vendido (€)": [round(vendido, 2)],
        "coste (€)": [round(coste, 2)],
        "margen (€)": [round(vendido - coste, 2)],
        "margen (%)": [round((vendido - coste) / vendido * 100, 1)],
        "pedido medio (€)": [round(tabla["valor_vendido"].mean())]})


def pedidos_por(tabla, columna):
    """Pedidos, vendido y margen por oferta o por tipo de entidad."""
    grupo = tabla.groupby(columna)
    salida = pd.concat([grupo.size(), grupo["valor_vendido"].sum(), grupo["coste"].sum()], axis=1)
    salida.columns = ["pedidos", "vendido (€)", "coste (€)"]
    salida["margen (%)"] = ((salida["vendido (€)"] - salida["coste (€)"]) / salida["vendido (€)"] * 100).round(1)
    return salida.sort_values("vendido (€)", ascending=False)


def grafico_pedidos_mes(tabla):
    """Barras con lo vendido cada mes (solo los pedidos que tienen fecha de adjudicación)."""
    con_fecha = tabla[tabla["mes"].notna()]
    por_mes = con_fecha.groupby("mes")["valor_vendido"].sum().reset_index()
    por_mes = pd.DataFrame({"mes": range(1, 13)}).merge(por_mes, on="mes", how="left").fillna(0)
    fig, ax = plt.subplots(figsize=(8, 3.2))
    sns.barplot(data=por_mes, x="mes", y="valor_vendido", color=COLORES["ambar"], ax=ax)
    plt.xlabel("mes de la adjudicación (2026)")
    plt.ylabel("vendido (€)")
    plt.tight_layout()
    return fig
