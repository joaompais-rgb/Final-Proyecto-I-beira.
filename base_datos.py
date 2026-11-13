"""Funciones para crear la base de datos beira en MySQL, cargar las tablas y consultarla.

Las usa la sección 9 del notebook notebooks/beira_en_datos.ipynb. Todo sale de la lección 4.7 (Python y SQL):
mysql.connector con cursor, execute, executemany y commit para crear y cargar,
y SQLAlchemy con create_engine, text y pd.read_sql para consultar.
"""
import mysql.connector
import pandas as pd
from sqlalchemy import create_engine, text

from config import BASE_DE_DATOS


def ejecutar_script(cursor, ruta):
    """Ejecuta una a una las instrucciones de un script .sql y devuelve cuántas ha ejecutado.

    Las instrucciones van separadas por punto y coma. Las líneas que son solo comentario se quitan.
    """
    script = open(ruta, encoding="utf-8").read()
    ejecutadas = 0
    for trozo in script.split(";"):
        lineas = [linea for linea in trozo.split("\n") if not linea.strip().startswith("--")]
        instruccion = "\n".join(lineas).strip()
        if instruccion != "":
            cursor.execute(instruccion)
            ejecutadas += 1
    return ejecutadas


def cargar_tabla(conexion, nombre, tabla):
    """Inserta todas las filas de un DataFrame en la tabla de MySQL del mismo nombre y devuelve cuántas son.

    Los valores vacíos de pandas (NaN) se pasan como None, que MySQL guarda como NULL.
    """
    columnas = ", ".join(tabla.columns)
    huecos = ", ".join(["%s"] * len(tabla.columns))
    filas = []
    for fila in tabla.values.tolist():
        filas.append(tuple([None if pd.isna(valor) else valor for valor in fila]))
    cursor = conexion.cursor()
    cursor.executemany("INSERT INTO " + nombre + " (" + columnas + ") VALUES (" + huecos + ")", filas)
    conexion.commit()
    cursor.close()
    return len(filas)


def conectar(password, usuario="root", servidor="localhost"):
    """Crea el engine de SQLAlchemy para consultar la base de datos beira."""
    return create_engine("mysql+pymysql://" + usuario + ":" + password + "@" + servidor + "/" + BASE_DE_DATOS)


def consultar(engine, sql):
    """Ejecuta una consulta SQL y devuelve el resultado como DataFrame."""
    with engine.connect() as connection:
        return pd.read_sql(text(sql), connection)


def ejecutar(engine, sql):
    """Ejecuta una instrucción que no devuelve filas, como crear o borrar una vista."""
    with engine.connect() as connection:
        connection.execute(text(sql))
