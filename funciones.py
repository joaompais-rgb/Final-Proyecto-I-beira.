"""Funciones del proyecto «beira. en datos»: leer, revisar y limpiar los datos, y preparar el análisis.

Las usa el notebook notebooks/beira_en_datos.ipynb. Los valores fijos (carpetas, palabras de las
reglas, umbrales) vienen de config.py.
"""
import pandas as pd

from config import ACENTOS, DATOS, FARDAMENTO, JUNTA_EXCLUIDA, NO_ES_ROPA, PROTECCION, ROPA, SIGNOS


# ---------------------------------------------------------------- leer y revisar

def leer(nombre):
    """Lee un CSV de data/clean y pasa los nombres de las columnas a minúsculas."""
    tabla = pd.read_csv(DATOS + nombre + ".csv")
    tabla.columns = tabla.columns.str.lower()
    return tabla


def revisar(tabla, nombre):
    """Revisión de la semana 2: tamaño, columnas y tipos, nulos, duplicados, primeras y últimas filas y resumen."""
    print("====", nombre, "====")
    print(tabla.shape[0], "filas y", tabla.shape[1], "columnas | filas duplicadas:", tabla.duplicated().sum())
    tabla.info()
    nulos = tabla.isna().sum()
    print("columnas con nulos:")
    print(nulos[nulos > 0])
    print("primeras filas:")
    print(tabla.head())
    print("últimas filas:")
    print(tabla.tail())
    print("resumen:")
    print(tabla.describe().round(2))


def sin_junta_excluida(tabla, columna):
    """Quita la Junta de Freguesia de Alvoco das Várzeas: la beira. no trabaja con ella (conflicto de intereses)."""
    nombre = tabla[columna].fillna("").str.lower().str.replace("ô", "o").str.replace("á", "a")
    return tabla[nombre.apply(lambda texto: JUNTA_EXCLUIDA not in texto)]


# ---------------------------------------------------------------- textos y municipios

def normalizar(texto):
    """Minúsculas, sin acentos ni signos y con un espacio a cada lado, para buscar palabras enteras."""
    texto = str(texto).lower()
    for letra, cambio in ACENTOS.items():
        texto = texto.replace(letra, cambio)
    for signo in SIGNOS:
        texto = texto.replace(signo, " ")
    return " " + " ".join(texto.split()) + " "


def concelho_por_nombre(nombre, nombres_concelho):
    """El municipio que aparece en el nombre del comprador, si solo hay uno; si no, texto vacío.

    nombres_concelho es un diccionario {nombre normalizado: nombre del municipio}.
    """
    texto = normalizar(nombre)
    hallados = []
    for clave, municipio in nombres_concelho.items():
        if " de" + clave in texto or " da" + clave in texto or " do" + clave in texto or texto.endswith(clave):
            hallados.append(municipio)
    if len(hallados) == 1:
        return hallados[0]
    return ""


def lugar_del_contrato(lugar, nombres_concelho):
    """El municipio de la región que dice la columna municipio del contrato; «fuera» si es otro; texto vacío si no dice nada."""
    if lugar == "":
        return ""
    return nombres_concelho.get(normalizar(lugar.split("\n")[0]), "fuera")


def elegir_concelho(lugar, por_nombre):
    """Fuera si la mayoría de sus contratos está fuera; si no, manda el nombre y después el lugar."""
    if lugar == "fuera":
        return ""
    if por_nombre != "":
        return por_nombre
    return lugar


# ---------------------------------------------------------------- reglas sobre los contratos

def contiene(texto, palabras):
    """True si alguna de las palabras está en el texto."""
    for palabra in palabras:
        if palabra in texto:
            return True
    return False


def es_ropa_o_fardamento(objeto, descripcion):
    """«sí» si el contrato es de ropa o fardamento; «no» si no lo es o si es solo equipo de protección."""
    texto = normalizar(objeto) + normalizar(descripcion)
    if contiene(texto, NO_ES_ROPA) or not contiene(texto, ROPA):
        return "no"
    if contiene(texto, PROTECCION) and not contiene(texto, FARDAMENTO):
        return "no"
    return "sí"


def procedimiento(texto):
    """Junta los procedimientos del Portal BASE en cuatro grupos."""
    texto = texto.lower()
    if "ajuste" in texto:
        return "ajuste directo"
    if "consulta" in texto:
        return "consulta previa"
    if "concurso" in texto:
        return "concurso"
    return "otro"


# ---------------------------------------------------------------- historia de cada comprador

def filas_del_ano(tabla, ano):
    """Una fila por comprador que ya había comprado alguna vez hasta ese año, con lo que había hecho hasta entonces."""
    grupo = tabla[tabla["ano"] <= ano].groupby("comprador_nif")   # hasta ese año
    filas = pd.concat([grupo.size(), grupo["precio"].sum(), grupo["ano"].nunique(),
                       grupo["ano"].min(), grupo["ano"].max(), grupo["es_equipo"].mean()], axis=1)
    filas.columns = ["contratos_acum", "gasto_acum", "anos_con_compra", "primer_ano", "ultimo_ano", "pct_equipo"]
    filas = filas.reset_index()

    este = tabla[tabla["ano"] == ano].groupby("comprador_nif")   # solo ese año
    este_ano = pd.concat([este.size(), este["precio"].sum()], axis=1)
    este_ano.columns = ["contratos_este_ano", "gasto_este_ano"]
    este_ano = este_ano.reset_index()
    filas = filas.merge(este_ano, on="comprador_nif", how="left")
    filas["contratos_este_ano"] = filas["contratos_este_ano"].fillna(0)
    filas["gasto_este_ano"] = filas["gasto_este_ano"].fillna(0)
    filas["compro_este_ano"] = filas["contratos_este_ano"].apply(lambda n: 1 if n > 0 else 0)
    filas["anos_desde_ultima"] = ano - filas["ultimo_ano"]
    filas["antiguedad"] = ano - filas["primer_ano"]
    filas["ano"] = ano
    if ano < 2025:   # en 2025 no hay respuesta: 2026 todavía no ha terminado
        siguiente = tabla[tabla["ano"] == ano + 1]["comprador_nif"].unique()
        filas["compra_siguiente"] = filas["comprador_nif"].isin(siguiente).astype(int)
    return filas.drop(columns=["primer_ano", "ultimo_ano"])


def poner_grupo(compro, anos):
    """Grupo del comprador según si compró este año y cuántos años lleva comprando."""
    if compro == 1 and anos >= 3:
        return "A. fiel"
    if compro == 1 and anos == 2:
        return "B. repite"
    if compro == 1:
        return "C. nuevo"
    if anos >= 2:
        return "D. en pausa"
    return "E. puntual"


def por_mes(meses):
    """% de cada mes, de 1 a 12, en una columna de meses."""
    conteo = []
    for mes in range(1, 13):
        conteo.append((meses == mes).sum())
    total = sum(conteo)
    return [round(n / total * 100) for n in conteo]


# ---------------------------------------------------------------- facturas de la PAISAN

def a_numero(texto):
    """Pasa «1.215,24 €» a 1215.24."""
    return float(texto.replace("€", "").replace(".", "").replace(",", ".").strip())


def tipo_cliente(nif, iva):
    """Tipo de cliente por el NIF: el primer número dice si es una persona, una empresa o una entidad pública."""
    if nif == "" and iva == 0:
        return "extranjero"          # sin NIF portugués y sin IVA: exportación
    if nif == "":
        return "consumidor final"
    if nif[0] not in "0123456789" or nif.startswith("98"):
        return "extranjero"          # NIF de otro país o no residente
    if nif[0] in "123":
        return "persona física"
    if nif[0] == "5":
        return "empresa o asociación"
    if nif[0] == "6":
        return "entidad pública"
    return "otro"
