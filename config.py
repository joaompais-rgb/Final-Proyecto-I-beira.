"""Valores fijos del proyecto «beira. en datos».

Todo lo que podría cambiar (carpetas, colores, años, umbrales y palabras de las reglas) está aquí,
para no escribirlo a mano dentro del notebook. Si cambia un valor, se cambia en este archivo y se
vuelve a ejecutar el notebook.
"""

# Carpetas (relativas a la carpeta notebooks)
DATOS = "../data/clean/"            # datos públicos ya limpios
INTERNO = "../data/interno/"        # facturación de la PAISAN y pedidos de la beira. (no se sube a GitHub)
CARPETA_SQL = "../data/sql/"        # tablas públicas para la base de datos
CARPETA_SQL_INTERNA = "../data/interno/sql/"
CARPETA_TABLEAU = "../tableau/"
RESULTADOS = "../resultados/"
ESQUEMA_SQL = "../sql/1_esquema.sql"
BASE_DE_DATOS = "beira"            # nombre de la base de datos en MySQL
USUARIO_MYSQL = "JMPais"           # usuario de MySQL de quien ejecuta el notebook (cambiarlo si es otro)

# Reproducibilidad
SEMILLA = 0

# Colores de la marca beira.
COLORES = {"verde_serra": "#404020", "terracota": "#96422C", "ambar": "#8F6226", "gris": "#9A958C"}

# Parte A
PRENDAS_EQUIPO = ["camisetas", "ropa deportiva", "polos", "sudaderas", "gorras"]   # lo que viste a un equipo o a un evento
KM_CERCA = 50                                                                         # radio de la región alrededor de la PAISAN
JUNTA_EXCLUIDA = "freguesia de alvoco das varzeas"                                   # conflicto de intereses: fuera de todas las tablas

# Parte B
ANOS_INCOMPLETOS = [2020, 2021]     # el e-fatura solo dejó descargar 300 facturas: faltan de enero a mayo de 2020 y parte de enero de 2021
MESES_INCOMPLETOS = [2020 * 12 + mes for mes in range(1, 6)] + [2021 * 12 + 1]   # los mismos meses, como año × 12 + mes
OBJETIVO_TRES_MAYORES = 0.80        # peso máximo que queremos para los tres mayores clientes

# Para normalizar textos (minúsculas, sin acentos ni signos)
ACENTOS = {"á": "a", "à": "a", "â": "a", "ã": "a", "é": "e", "ê": "e", "í": "i", "ó": "o", "ô": "o", "õ": "o", "ú": "u", "ç": "c"}
SIGNOS = "-–—_/.,;:()«»\"'´`’“”ºª\n\r\t"

# Regla «ropa o fardamento»: palabras que se buscan en el objeto y la descripción del contrato
ROPA = [" t shirt", " tshirt", " polos ", " polares", " parka", " fatos de treino", " fato de treino", " batas ", " avental",
        " aventais", " sweat", " camisol", " camisa", " vestuario", " fardament", " fardas ", " farda ", " uniforme",
        " equipamento desportivo", " equipamentos desportivos", " indumentaria", " bordad", " estampag", " bone ", " bones ",
        " casaco", " blusao", " blusoes", " colete", " jersey", " calcoes", " calcas ", "roupa de trabalho",
        " fatos de trabalho", " fato de trabalho", " corta ventos"]
FARDAMENTO = [" fardament", " fardas ", " farda ", " uniforme", "vestuario de trabalho", "vestuario profissional",
              "roupa de trabalho", " fatos de trabalho", " fato de trabalho"]
PROTECCION = [" epi ", " epis ", " protecao ", " proteccao ", " seguranca "]
NO_ES_ROPA = [" marrow ", "higienizacao", "lavagem", "lavandaria", "aluguer", "esplanada", "publicidade institucional",
              " certificacao ", "sistema de prensagem", "combustivel", "enfardamento", " combate ", " incendio", "ignifug",
              " hospitalar", " cirurg", " mascara", " covid", " reciclag", "economia circular", "fato seco"]
