# app.py
"""App «beira. en datos»: qué dicen los datos, a quién dirigirse, el mercado público, la PAISAN y los pedidos de la beira.

Se ejecuta desde la carpeta app:   streamlit run app.py
Los datos, los filtros y los gráficos están en backend.py, como en la lección de Streamlit.
Cada página explica qué enseña, cómo leerla y qué decisión ayuda a tomar.
"""
import pandas as pd
import streamlit as st

import backend

PAGINAS = ["Inicio: cómo usar la app", "A quién dirigirse", "El mercado público", "La PAISAN", "La beira. hoy"]


def como_leer(texto):
    """Escribe una nota corta para leer un gráfico o una tabla."""
    st.write("**Cómo leerlo:** " + texto)


def que_decidir(texto):
    """Escribe la decisión que ayuda a tomar la página."""
    st.write("**Qué decidir con esto:** " + texto)


def pagina_inicio():
    """Página 0: el problema, las cuatro páginas y las palabras que hay que conocer."""
    st.title("beira. en datos")
    st.write("La **PAISAN** es una fábrica de ropa de Oliveira do Hospital que depende de tres clientes: "
             "en 2025 se llevaron el 93 % de lo que facturó. La **beira.** es su marca de ropa personalizada "
             "(equipos, trabajo y eventos) y nace para traerle clientes propios.")
    st.write("Esta app responde a cuatro preguntas, una por página. Se cambia de página en el menú de la izquierda "
             "y, en cada página, los filtros de la izquierda cambian todos los números y gráficos.")
    st.table(pd.DataFrame({
        "página": PAGINAS[1:],
        "pregunta": ["¿A qué entidades de la región escribir primero?",
                     "¿Hay mercado para una marca pequeña? ¿Cómo y cuándo se compra?",
                     "¿Cuánto tiene que vender la beira. y cuándo cabe en la fábrica?",
                     "¿Cuánto llevamos vendido frente al objetivo?"],
        "datos": ["Portal BASE, 2020-2025", "Portal BASE, 2020-2025", "facturas de la PAISAN (internas)", "pedidos de Airtable (internos)"]}))

    st.write("### Lo que hay que saber en un minuto")
    izquierda, derecha = st.columns(2)
    izquierda.write("- **63 entidades** públicas de la región compran ropa en dos años o más.\n"
                    "- **62 %** de quien compra un año vuelve a comprar al siguiente (29 % si no compró).\n"
                    "- **77 %** de los contratos son de menos de 20.000 €: pedidos del tamaño de la beira.")
    derecha.write("- **59 %** de las compras repetidas van a un proveedor nuevo: nadie tiene el cliente atado.\n"
                  "- **Unos 83.000 € al año** de la beira. bastan para que la PAISAN dependa menos (los tres mayores, al 80 %).\n"
                  "- La fábrica tiene **más sitio en junio y julio**, cuando se produce para las fiestas.")

    with st.expander("Palabras que conviene conocer"):
        st.write("- **Ajuste directo:** la entidad elige a una sola empresa y le pide precio. Se gana dándose a conocer antes.\n"
                 "- **Consulta previa:** la entidad invita a tres o más empresas. Hay que conseguir que te inviten.\n"
                 "- **Concurso:** cualquiera puede presentarse; son los contratos más grandes.\n"
                 "- **Grupo de compra:** *A. fiel* (compró en 2025 y lleva tres años o más), *B. repite* (lleva dos años), "
                 "*D. en pausa* (no compró en 2025, pero sí en dos años o más).\n"
                 "- **Tasa de vuelta:** de cada 100 entidades del grupo, cuántas compraron al año siguiente.\n"
                 "- **Hueco de la fábrica:** lo que le falta a cada mes para llegar al mejor mes de los últimos doce.")
    with st.expander("De dónde salen los datos"):
        st.write("Las tablas las guarda el notebook `beira_en_datos.ipynb` en `data/sql/` (públicas) y `data/interno/sql/` (internas). "
                 "Son las mismas que se cargan en MySQL y en Tableau. Las páginas de la PAISAN y de la beira. solo funcionan "
                 "en el ordenador que tiene los datos internos.")


def pagina_lista():
    """Página 1: las 63 entidades de la lista, con filtros para preparar los contactos."""
    st.title("A quién dirigirse")
    st.write("Las 63 entidades públicas de la región que compran ropa en dos años o más. "
             "Quien compra varios años es quien más vuelve a comprar (H1), por eso la lista sale de su historia.")
    lista = backend.cargar_lista()

    st.sidebar.header("Filtros de la lista")
    grupos = st.sidebar.multiselect("Grupo de compra", options=list(lista["grupo_compra"].unique()), default=list(lista["grupo_compra"].unique()))
    tipos = st.sidebar.multiselect("Tipo de entidad", options=list(lista["tipo_comprador"].unique()), default=list(lista["tipo_comprador"].unique()))
    km_max = st.sidebar.slider("Distancia máxima a la PAISAN (km)", min_value=10, max_value=100, value=100, step=5)
    solo_ropa = st.sidebar.checkbox("Solo las que compran ropa o fardamento")
    st.sidebar.write("Prueba: deja solo **A. fiel**, baja la distancia a 40 km y marca «solo ropa». "
                     "Las que quedan son las primeras visitas.")

    filtradas = backend.filtrar_lista(lista, grupos, tipos, km_max, solo_ropa)
    if len(filtradas) == 0:
        st.write("No hay entidades con esos filtros. Amplía la distancia o añade grupos.")
        return

    st.write("### Resumen")
    st.table(backend.para_ver(backend.resumen_lista(filtradas)))
    como_leer("cada número cambia con los filtros. *Fieles* son las que más probablemente vuelvan a comprar (8 de cada 10). "
              "*Precio mediano* es el tamaño normal de un pedido de estas entidades.")

    izquierda, derecha = st.columns(2)
    izquierda.write("**Cuándo suelen comprar**")
    izquierda.pyplot(backend.grafico_meses(filtradas))
    izquierda.write("Cada barra cuenta las entidades cuyo mes habitual es ese. Hay que escribirles **antes** de ese mes.")
    derecha.write("**Dónde están**")
    derecha.pyplot(backend.grafico_mapa(filtradas))
    derecha.write("Cada punto es una entidad; el color es su grupo. Las más cercanas a Oliveira do Hospital son las más baratas de visitar.")

    st.write("### Las entidades")
    st.write("Ordenadas por grupo (primero las fieles) y por distancia.")
    st.dataframe(backend.tabla_lista(filtradas))
    que_decidir("a las de **ajuste directo**, visita y catálogo antes de su mes habitual; "
                "a las de **consulta previa**, pedir que inviten a la beira. a la próxima. "
                "Se empieza por las fieles que compran ropa, de la más cercana a la más lejana.")

    with st.expander("Qué significa cada columna"):
        st.write("- **grupo:** A. fiel (compró en 2025 y lleva tres años o más comprando; en su grupo vuelve a comprar el 80 %), "
                 "B. repite (compró en 2025 y lleva dos años; 64 %), D. en pausa (no compró en 2025, pero sí en dos años o más; 39 %).\n"
                 "- **mes habitual:** el mes en que más contratos ha firmado.\n"
                 "- **cómo compra:** el procedimiento que más usa. En el ajuste directo elige a una sola empresa.\n"
                 "- **precio mediano:** el tamaño normal de sus contratos de ropa.\n"
                 "- **proveedores distintos:** a cuántas empresas ha comprado en seis años.")


def pagina_mercado():
    """Página 2: los contratos públicos de ropa (Portal BASE, 2020-2025)."""
    st.title("El mercado público")
    st.write("Contratos públicos de ropa publicados en el Portal BASE entre 2020 y 2025. "
             "Sirve para ver si hay sitio para una marca pequeña y cómo se entra.")
    contratos = backend.cargar_contratos()
    lista = backend.cargar_lista()

    st.sidebar.header("Filtros del mercado")
    anos = st.sidebar.slider("Años", min_value=2020, max_value=2025, value=(2020, 2025), step=1)
    ambito = st.sidebar.radio("Ámbito", ("todo el país", "la región", "la lista de la beira."))
    tipos = st.sidebar.multiselect("Tipo de comprador", options=list(contratos["tipo_comprador"].unique()), default=list(contratos["tipo_comprador"].unique()))
    solo_ropa = st.sidebar.checkbox("Solo ropa o fardamento")
    st.sidebar.write("Prueba: cambia el ámbito a **la región** y deja solo **escuela**: "
                     "verás pedidos pequeños y casi todos por ajuste directo.")

    filtrados = backend.filtrar_contratos(contratos, lista, anos[0], anos[1], ambito, tipos, solo_ropa)
    if len(filtrados) == 0:
        st.write("No hay contratos con esos filtros.")
        return

    st.write("### Resumen")
    st.table(backend.para_ver(backend.resumen_mercado(filtrados)))
    como_leer("el *precio mediano* es el contrato típico (la media engaña: unos pocos contratos son enormes). "
              "El *% de menos de 20.000 €* dice cuántos pedidos están al alcance de la beira.")

    izquierda, derecha = st.columns(2)
    izquierda.write("**Contratos por año**")
    izquierda.pyplot(backend.grafico_por_ano(filtrados))
    izquierda.write("Si las barras se mantienen, el mercado es estable: no es una moda de un año.")
    derecha.write("**En qué mes se firman**")
    derecha.pyplot(backend.grafico_calendario(filtrados))
    derecha.write("Los meses altos son los de firmar; la propuesta tiene que llegar uno o dos meses antes.")

    st.write("### Cómo se compra")
    st.table(backend.para_ver(backend.tabla_procedimientos(filtrados)))
    como_leer("en el **ajuste directo** casi no hay competidores (la entidad invita a una empresa); "
              "en el **concurso** se presentan varias y los contratos son mayores.")

    st.write("### Quién compra más")
    st.dataframe(backend.tabla_compradores(filtrados))
    que_decidir("si en tu filtro domina el ajuste directo y los pedidos son pequeños, el camino es darse a conocer, no competir en concursos.")


def pagina_paisan():
    """Página 3: la facturación de la PAISAN (datos internos), cuánto tiene que vender la beira. y cuándo cabe."""
    st.title("La PAISAN")
    try:
        facturas = backend.cargar_facturas()
    except FileNotFoundError:
        st.write("Faltan los datos internos de la PAISAN (carpeta data/interno/sql). Esta página solo funciona en el ordenador que los tiene.")
        return

    st.write("Facturación de la PAISAN de 2013 a 2026 (e-fatura). Los clientes van en código. "
             "Los años 2020 y 2021 están incompletos en la descarga.")
    tabla = backend.concentracion(facturas)
    tres, total, necesario = backend.objetivo_beira(tabla)

    st.write("### 1. El problema: la PAISAN depende de tres clientes")
    st.pyplot(backend.grafico_concentracion(tabla))
    como_leer("cada barra es un año; la altura es la parte de la facturación que se llevaron los tres mayores clientes. "
              "La línea discontinua es el 80 %. En " + str(backend.ANO_BASE) + " fue el " + str(round(tres / total * 100)) + " %: "
              "si se va uno de ellos, se va una parte enorme del año.")

    st.write("### 2. ¿Y si la beira. vende...?")
    ventas = st.slider("Ventas de la beira. al año (€)", min_value=0, max_value=150000, value=30000, step=5000)
    peso = backend.peso_con_beira(tres, total, ventas)
    doce = backend.ultimos_doce(facturas)
    hueco = doce["hueco"].sum()
    st.table(backend.para_ver(backend.resumen_escenario(ventas, peso, necesario, hueco)))
    if ventas >= necesario:
        st.write("Con esas ventas los tres mayores clientes bajan del 80 %.")
    else:
        st.write("Todavía faltan " + str(round(necesario - ventas)) + " € al año para bajar al 80 %.")
    if ventas <= hueco:
        st.write("Cabe en la fábrica: es menos de lo que falta a los últimos doce meses para llegar al mejor mes.")
    else:
        st.write("No cabe con la capacidad que la fábrica ha demostrado en los últimos doce meses.")
    como_leer("mueve el control y mira cómo baja el peso de los tres mayores. Es una cuenta, no una previsión: "
              "supone que los tres mayores siguen comprando lo mismo.")

    st.write("### 3. ¿Cuántas piezas son?")
    precio = st.slider("Precio de venta por pieza (€)", min_value=4, max_value=15, value=7, step=1)
    st.table(backend.para_ver(pd.DataFrame({
        "": ["objetivo anual", "objetivo de un mes", "ventas elegidas arriba (al año)"],
        "euros": [round(necesario), round(necesario / 12), ventas],
        "piezas": [round(necesario / precio), round(necesario / 12 / precio), round(ventas / precio)]})))
    como_leer("las empresas de personalización publican precios de unos 5 € a 10 € por pieza (7 € la típica). "
              "Cambia el precio para ver cuántas piezas tendría que hacer la fábrica. Esta es la pregunta para la PAISAN: ¿caben?")

    st.write("### 4. ¿Cuándo cabe? La fábrica y el mercado")
    st.pyplot(backend.grafico_encaje(backend.calendario_encaje(facturas)))
    como_leer("las tres líneas están en % del año. Donde la línea de la PAISAN está baja, la fábrica tiene sitio. "
              "Las fiestas se producen sobre todo de mayo a agosto, justo cuando la PAISAN factura menos (junio y julio).")
    que_decidir("las fiestas y las asociaciones son el cliente que mejor encaja con el calendario de la fábrica: "
                "hay que cerrar sus pedidos en primavera para producirlos en verano.")

    st.write("### 5. Cuánto cabe: los últimos doce meses")
    st.pyplot(backend.grafico_doce(doce))
    como_leer("la línea es el mejor mes. Lo que le falta a cada mes para llegar a ella es el hueco para pedidos nuevos.")
    with st.expander("Ver la tabla"):
        st.dataframe(doce)
    with st.expander("Ver la facturación y los tres mayores clientes de cada año"):
        st.dataframe(tabla.round(0))


def pagina_beira():
    """Página 4: los pedidos de la beira. copiados de Airtable (datos internos)."""
    st.title("La beira. hoy")
    try:
        pedidos = backend.cargar_pedidos()
        facturas = backend.cargar_facturas()
    except FileNotFoundError:
        st.write("Faltan los datos internos (carpeta data/interno/sql). Esta página solo funciona en el ordenador que los tiene.")
        return

    st.write("Pedidos de la beira. copiados de Airtable. Los registros reales y el escenario de ventas van separados: "
             "el escenario sirve para ver cómo se seguirá el objetivo, no son ventas.")
    con_escenario = st.checkbox("Incluir el escenario de ventas (de abril a noviembre de 2026)")
    elegidos = backend.filtrar_pedidos(pedidos, con_escenario)

    st.write("### Resumen")
    st.table(backend.para_ver(backend.resumen_pedidos(elegidos)))
    como_leer("el *margen* es lo que queda de cada euro vendido después de pagar el coste.")

    tres, total, necesario = backend.objetivo_beira(backend.concentracion(facturas))
    vendido = elegidos["valor_vendido"].sum()
    st.write("El objetivo es facturar unos " + str(round(necesario)) + " € al año, para que los tres mayores clientes de la PAISAN bajen al 80 %. "
             "Estos pedidos son el " + str(round(vendido / necesario * 100, 1)) + " % de ese objetivo.")

    izquierda, derecha = st.columns(2)
    izquierda.write("**Por oferta**")
    izquierda.table(backend.para_ver(backend.pedidos_por(elegidos, "oferta")))
    derecha.write("**Por tipo de entidad**")
    derecha.table(backend.para_ver(backend.pedidos_por(elegidos, "tipo_entidad")))

    if elegidos["mes"].notna().sum() > 0:
        st.write("### Cuándo se vendió")
        st.pyplot(backend.grafico_pedidos_mes(elegidos))
    else:
        st.write("Los registros reales todavía no tienen fecha de adjudicación en Airtable: no se puede dibujar el calendario.")
    que_decidir("cada mes, comparar lo vendido con el objetivo y con los meses de más sitio en la fábrica.")

    with st.expander("Ver los pedidos"):
        st.dataframe(elegidos[["encomenda", "entidad", "tipo_entidad", "oferta", "valor_vendido", "coste", "origen_dato"]])


def main():
    st.sidebar.title("beira. en datos")
    pagina = st.sidebar.radio("Página", PAGINAS)
    try:
        if pagina == PAGINAS[0]:
            pagina_inicio()
        elif pagina == PAGINAS[1]:
            pagina_lista()
        elif pagina == PAGINAS[2]:
            pagina_mercado()
        elif pagina == PAGINAS[3]:
            pagina_paisan()
        else:
            pagina_beira()
    except FileNotFoundError:
        st.write("No encuentro los datos. La app se ejecuta desde la carpeta app (cd app y después streamlit run app.py), "
                 "y antes hay que ejecutar el notebook beira_en_datos.ipynb, que guarda las tablas en data/sql.")


if __name__ == "__main__":
    main()
