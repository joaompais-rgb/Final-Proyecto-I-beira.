# beira. en datos · Objetivo y plan

10 de noviembre de 2026 · João Miguel Pais · Case Study 2 (Data Analytics)

## Objetivo

**La PAISAN depende de tres clientes. Decidir, con datos, a quién debe dirigirse la beira. para traerle clientes propios, cómo y cuándo llegar a ellos, y cuánto trabajo nuevo cabe en la fábrica.**

| | A. A quién dirigirse | B. La PAISAN |
|---|---|---|
| Pregunta | ¿Qué entidades compran ropa, cómo, a quién y cuándo? | ¿Cuánto depende la PAISAN de pocos clientes, cuánto cabe en la fábrica y cuánto tiene que vender la beira.? |
| Datos | 6.382 contratos públicos de ropa 2020-2025 (Portal BASE), 1.596 organizaciones (OpenStreetMap), 66 municipios, fiestas y eventos | 3.375 facturas de la PAISAN 2013-2026 (e-fatura), salario mínimo, IPC de la ropa y los pedidos de la beira. (Airtable) |
| Para la beira. | la lista de 63 entidades, con su mes habitual y su forma de comprar | el objetivo de ventas (unos 83.000 € al año) y los meses con más sitio en la fábrica |

## Cómo se hace

| Paso | Herramienta | Dónde |
|---|---|---|
| 1. Limpiar y analizar los datos, con pruebas de hipótesis | Python (pandas, seaborn, scipy, scikit-learn) | `notebooks/beira_en_datos.ipynb` |
| 2. Guardar los datos en una base relacional y consultarlos | MySQL y SQL, con Python para conectar y dibujar | `notebooks/beira_en_datos.ipynb` (sección 9), `sql/`, `src/base_datos.py` |
| 3. Enseñar el mercado y la lista | Tableau | `tableau/beira_en_datos.twb` |
| 4. Dar a la beira. una herramienta para el día a día | Streamlit | `app/` |

## Hipótesis

| | Hipótesis | Parte | Prueba |
|---|---|---|---|
| H1 | Quien compra ropa un año vuelve a comprar el siguiente | A | chi-cuadrado y V de Cramér |
| H2 | Las prendas de equipo se compran sobre todo de mayo a septiembre | A | chi-cuadrado y V de Cramér |
| H3 | Clubes y asociaciones publican menos contacto que las escuelas | A | chi-cuadrado y V de Cramér |
| H4 | Los tres mayores clientes de la PAISAN suman más del 80 % de la facturación | B | t de una muestra |
| H5 | Los clientes de la PAISAN que compran un año vuelven al siguiente | B | chi-cuadrado y V de Cramér |
| H6 | La factura mediana subió menos que el salario mínimo | B | t de Welch |

## Reglas

- Solo se usa lo visto en clase; cada celda lleva su explicación antes («Cómo funciona») y su conclusión después («Qué nos llevamos»), en español y en portugués.
- La Junta de Freguesia de Alvoco das Várzeas se excluye de todas las listas (conflicto de intereses).
- Los datos internos (`data/interno`) no se suben. Los clientes de la PAISAN van en código, sin NIF ni número de factura.

## Entrega

Un notebook, la base de datos con sus consultas, el panel de Tableau, la app de Streamlit y la presentación de 8 minutos.
