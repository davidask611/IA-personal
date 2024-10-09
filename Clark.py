import json
from difflib import SequenceMatcher
from datetime import datetime
import unicodedata
import random
import re

dias_semana = {
    "Monday": "lunes",
    "Tuesday": "martes",
    "Wednesday": "miércoles",
    "Thursday": "jueves",
    "Friday": "viernes",
    "Saturday": "sábado",
    "Sunday": "domingo"
}

# Definición de la función para cargar datos
def datos(nombre_archivo='conocimientos.json'):
    try:
        with open(nombre_archivo, 'r', encoding='utf-8') as archivo:
            return json.load(archivo)  # Cargar datos del archivo JSON
    except FileNotFoundError:
        print("Error: Archivo no encontrado.")
        return {}  # Retorna un diccionario vacío si no se encuentra el archivo
    except json.JSONDecodeError:
        print("Error: Formato inválido en el archivo JSON.")
        return {}  # Retorna un diccionario vacío si hay un error de formato

# Definición de la función para cargar datos
def cargar_datos(nombre_archivo='conocimientos.json'):
    try:
        with open(nombre_archivo, 'r', encoding='utf-8') as archivo:
            return json.load(archivo)  # Cargar datos del archivo JSON
    except FileNotFoundError:
        print("Error: Archivo no encontrado.")
        return {}  # Retorna un diccionario vacío si no se encuentra el archivo
    except json.JSONDecodeError:
        print("Error: Formato inválido en el archivo JSON.")
        return {}  # Retorna un diccionario vacío si hay un error de formato


# Cargar datos desde el JSON al inicio de tu script
conocimientos = cargar_datos('conocimientos.json')

# Iniciar listas vacías
respuestas_cache = {}
UMBRAL_SIMILITUD = 0.6
historial_preguntas = []
historial_conversacion = []  # Lista para almacenar el historial de conversación
MAX_HISTORIAL = 6  # Limitar el historial a los últimos 6 mensajes
signos_zodiacales = conocimientos.get("signos_zodiacales", {})  # Asegurarse de que los signos están en el diccionario 'conocimientos'

# Funciones
def eliminar_acentos(texto):
    # Reemplazar la 'ñ' por un símbolo temporal (por ejemplo, ~)
    texto = texto.replace('ñ', '~').replace('Ñ', '~')  # Reemplazar tanto minúscula como mayúscula
    # Normalizar el texto a una forma que separa los caracteres acentuados
    texto_normalizado = unicodedata.normalize('NFD', texto)
    # Filtrar solo los caracteres que no son acentos
    texto_sin_acentos = ''.join(c for c in texto_normalizado if unicodedata.category(c) != 'Mn')
    # Reemplazar el símbolo temporal por 'ñ'
    texto_final = texto_sin_acentos.replace('~', 'ñ')
    return texto_final


# Recordar el historial de la charla
def recordar_historial():
    if historial_conversacion:
        print("IA: Recordando el historial reciente...")
        # Limitar a los últimos MAX_HISTORIAL elementos
        for idx, item in enumerate(historial_conversacion[-MAX_HISTORIAL:], 1):
            print(f"{idx}. Tú dijiste: '{item['pregunta']}' -> IA respondió: '{item['respuesta']}'")
    else:
        print("IA: No hay historial de conversación disponible.")


# Actualizar el historial de conversación
def actualizar_historial(pregunta, respuesta):
    historial_conversacion.append({"pregunta": pregunta, "respuesta": respuesta})

    # Limitar el historial a los últimos MAX_HISTORIAL mensajes
    if len(historial_conversacion) > MAX_HISTORIAL:
        historial_conversacion.pop(0)  # Eliminar el mensaje más antiguo


def guardar_datos(datos, nombre_archivo='conocimientos.json'):
    try:
        with open(nombre_archivo, 'w', encoding='utf-8') as archivo:
            json.dump(datos, archivo, ensure_ascii=False, indent=4)
        print(f"Datos guardados exitosamente en '{nombre_archivo}'.")
    except IOError as e:
        print(f"Error al guardar los datos en el archivo: {e}")

######################################################################################################
def buscar_saludo(pregunta_limpia, conocimientos):
    # Obtener la lista de saludos del archivo JSON
    saludos = conocimientos.get("saludos", {})

    # Intentar encontrar un saludo exacto
    for saludo in saludos:
        if saludo in pregunta_limpia:
            return saludos[saludo]

    # Si no encuentra el saludo, puedes intentar buscar coincidencias parciales
    palabras_pregunta = set(pregunta_limpia.split())  # Divide la pregunta en palabras
    for saludo, respuesta in saludos.items():
        palabras_saludo = set(saludo.split())  # Divide los saludos en palabras

        # Verifica si alguna palabra del saludo coincide con la pregunta
        if palabras_saludo & palabras_pregunta:  # El operador & busca intersección
            return respuesta

    return None

# Función para buscar palabras clave en la pregunta
def buscar_palabras_clave(pregunta, datos):  # Agregando datos como parámetro
    for categoria, info in datos["categorias"].items():
        if "palabrasClave" in info:  # Verificar si 'palabrasClave' existe
            for palabra in info["palabrasClave"]:
                if palabra in pregunta.lower():
                    return categoria
    return None

# Función para obtener una respuesta de la categoría
def obtener_respuesta(categoria):
    if categoria:
        respuestas = datos["categorias"][categoria]["respuesta"]
        return random.choice(respuestas)  # Respuesta dinámica
    return "No tengo suficiente información para responder."

# Función para obtener una respuesta más específica si hay relaciones
def obtener_relaciones(categoria, pregunta):
    if categoria:
        relaciones = datos["categorias"][categoria].get("relaciones", {})
        for palabra in relaciones:
            if palabra in pregunta.lower():
                return relaciones[palabra]
    return None

def actualizar_contexto(pregunta, conocimientos):
    conocimientos["contexto"]["ultimaPregunta"] = pregunta
    guardar_datos(conocimientos, 'conocimientos.json')  # Guarda los cambios en el archivo JSON

def manejar_contexto(pregunta, conocimientos):
    ultima_pregunta = conocimientos["contexto"]["ultimaPregunta"]
    if ultima_pregunta and "fuego" in ultima_pregunta.lower() and "como" in pregunta.lower():
        return "¿Te refieres a cómo apagar el fuego o cómo mantenerlo encendido?"
    return None

# Función para manejar preguntas vagas o amplias
def manejar_preguntas_ampias(categoria):
    if categoria and "respuestaIncompleta" in datos["categorias"][categoria]:
        return datos["categorias"][categoria]["respuestaIncompleta"]
    return None

# Función para manejar el fuego con más precisión
def manejar_fuego(pregunta_limpia):
    if "apagar" in pregunta_limpia or "extinguir" in pregunta_limpia:
        return "Si el fuego es pequeño, puedes apagarlo con una manta o cubriéndolo."

    elif "mantener encendido" in pregunta_limpia or "no se apague" in pregunta_limpia:
        return "Para mantener el fuego encendido, asegúrate de que tenga suficiente combustible y oxígeno."

    elif "necesita el fuego" in pregunta_limpia:
        return "El fuego necesita tres elementos principales para mantenerse: combustible, oxígeno y calor."

    return None  # Si no encuentra coincidencia, devolver None


# Variable global para almacenar las últimas preguntas

def actualizar_historial_preguntas(pregunta):
    if len(historial_preguntas) >= 3:  # Mantener las últimas 3 preguntas
        historial_preguntas.pop(0)
    historial_preguntas.append(pregunta)

def responder_con_contexto(pregunta_limpia):
    # Verificamos si hay historial de preguntas
    if len(historial_preguntas) > 0:
        # Si la pregunta anterior fue sobre fuego, priorizamos respuestas relacionadas con eso
        if "fuego" in historial_preguntas[-1] and ("mantener" in pregunta_limpia or "apagar" in pregunta_limpia):
            return manejar_fuego(pregunta_limpia)

        # Si la pregunta anterior fue sobre agua, priorizamos respuestas relacionadas con agua
        if "agua" in historial_preguntas[-1]:
            if "importante" in pregunta_limpia:
                return "El agua es esencial para la vida humana y para muchos procesos naturales."
            if "apagar fuego" in pregunta_limpia:
                return "El agua se utiliza para apagar fuegos, especialmente los que no involucran productos químicos inflamables."

    # Si no hay historial o no se encuentra una relación en el historial, devolvemos None
    return None

def validar_fecha(fecha_str, formato="%d-%m-%Y"):
    try:
        datetime.strptime(fecha_str, formato)
        return True
    except ValueError:
        return False

def validar_campo_obligatorio(valor, campo):
    while not valor.strip():  # Comprobar si está vacío
        valor = input(f"El {campo} es obligatorio. Introduce {campo}: ")
    return valor

####################################################################################################
# Función para obtener la descripción de un signo zodiacal desde el diccionario cargado
def obtener_signo(signo):
    signo = signo.lower()  # Convertimos a minúsculas para evitar errores de mayúsculas/minúsculas
    if signo in signos_zodiacales:
        # Construir la respuesta con la descripción y más detalles del signo
        info_signo = signos_zodiacales[signo]
        descripcion = (f"El signo {signo.capitalize()} cubre desde {info_signo['fecha-fecha']}. "
                       f"Su elemento es {info_signo['elemento']}. {info_signo['descripcion']}")
        return descripcion
    else:
        return "Lo siento, no tengo información sobre ese signo."


# Función para detectar signos zodiacales con 're'
def detectar_signo(pregunta):
    pregunta_limpia = eliminar_acentos(pregunta.lower())  # Eliminar acentos y convertir a minúsculas

    # Crear un patrón que busque "signo" seguido o precedido por un signo zodiacal
    signos = '|'.join(signos_zodiacales.keys())  # Crear un patrón para todos los signos (ej. 'aries|tauro|geminis')
    patron = rf"(signo.*\b({signos})\b|\b({signos})\b.*signo)"

    # Buscar el patrón en la pregunta
    coincidencia = re.search(patron, pregunta_limpia)

    if coincidencia:
        # Si se encuentra un signo en la pregunta, devolver la información del signo
        signo_encontrado = coincidencia.group(2) or coincidencia.group(3)
        return obtener_signo(signo_encontrado)

    return None  # Si no se encuentra ninguna coincidencia
# Revisar codigo de los signos

# Funcion datos la IA
def responder_sobre_ia(pregunta_limpia, conocimientos):
    if pregunta_limpia in conocimientos["datosdelaIA"]:
        return conocimientos["datosdelaIA"][pregunta_limpia]
    return None  # Si la pregunta no está en el JSON, devolvemos None

# Funcion charla cotidiana
def manejar_charla(pregunta, conocimientos):
    # Limpiar la pregunta para que coincida con las claves del diccionario
    pregunta_limpia = eliminar_acentos(pregunta.lower())

    # Buscar en el JSON de conocimientos
    return conocimientos.get('charla', {}).get(pregunta_limpia, None)


# Busca la categoria y su lista, de no encontrar avisa del error
def obtener_chiste():
    try:
        lista_chistes = conocimientos["chiste"]["lista_chistes"]
        return random.choice(lista_chistes)
    except KeyError:
        return "Lo siento, no tengo chistes guardados."



# Buscar presidente y nombre clave y darlo
def presidente(pregunta):
    # Convertir la pregunta a minúsculas sin acentos
    pregunta_limpia = eliminar_acentos(pregunta.lower())

    # Dividir la pregunta en palabras
    palabras_pregunta = pregunta_limpia.split()

    # Lista de presidentes en el diccionario
    presidentes = conocimientos.get("presidente", {})

    # Recorrer todos los presidentes para ver si sus nombres están en la pregunta
    for nombre_presidente, detalles in presidentes.items():
        # Limpiar el nombre del presidente para compararlo
        nombre_presidente_limpio = eliminar_acentos(nombre_presidente.lower())

        # Verificar si las palabras clave 'presidente' y el nombre del presidente están en la frase
        if "presidente" in palabras_pregunta and nombre_presidente_limpio in palabras_pregunta:
            return (f"{nombre_presidente}: {detalles['nombre_completo']} fue presidente entre {detalles['periodo']}. "
                    f"Descripción: {detalles['descripcion']}")

    return "Lo siento, no tengo información sobre ese presidente."  # Mensaje por defecto si no hay coincidencia

##################
# Buscar perro y nombre o caracteristicas y darlo
def animales(pregunta, conocimientos):
    # Convertir la pregunta a minúsculas sin acentos
    pregunta_limpia = eliminar_acentos(pregunta.lower())

    # Dividir la pregunta en palabras
    palabras_pregunta = pregunta_limpia.split()

    # Lista de razas de perros en el diccionario
    perros = conocimientos.get("animal", {}).get("perro", {})

    # Recorrer todas las razas de perro en el diccionario
    for raza, detalles in perros.items():
        # Limpiar el nombre de la raza para compararlo
        raza_limpia = eliminar_acentos(raza.lower())

        # Verificar si la pregunta menciona la raza directamente o junto con "perro"
        if raza_limpia in palabras_pregunta or ("perro" in palabras_pregunta and raza_limpia in palabras_pregunta):
            # Responder con las características de la raza de perro
            return (f"{raza}: {detalles['nombre_completo']}. "
                    f"Descripción: {detalles['descripcion']} "
                    f"Docilidad: {detalles['caracteristicas']['docilidad']}. "
                    f"Amabilidad: {detalles['caracteristicas']['amabilidad']}")

    return "Lo siento, no tengo información sobre esa raza de perro."  # Mensaje por defecto si no hay coincidencia




# Función para buscar música o cantante por claves
def buscar_musica_por_claves(pregunta):
    # Convertir la pregunta a minúsculas sin acentos
    pregunta_limpia = eliminar_acentos(pregunta.lower())

    # Dividir la pregunta en palabras
    palabras_pregunta = pregunta_limpia.split()

    # Lista de géneros musicales en la categoría 'música'
    musica = conocimientos.get("musica", {})

    # Buscar por palabras clave relacionadas con 'musica', 'cantante' y 'información' junto con el nombre del cantante
    for genero, detalles in musica.items():
        nombre_cantante = eliminar_acentos(detalles["nombre_completo"].lower())

        # Verificar si la palabra 'musica', 'cantante', o 'informacion' y el nombre del cantante están en la pregunta
        if (("musica" in palabras_pregunta or "cantante" in palabras_pregunta or "informacion" in palabras_pregunta)
            and nombre_cantante in palabras_pregunta):

            # Construir la respuesta básica
            respuesta = (f"{nombre_cantante}: {detalles['nombre_completo']} es un {detalles['cargo']} de {detalles['genero_musical']}, "
                         f"nació el {detalles['fecha']} en {detalles['provincia']}, {detalles['pais']}.")

            # Si se pidió información y hay descripción, agregarla
            if "informacion" in palabras_pregunta and detalles.get("descripcion"):
                respuesta += f" Descripción: {detalles['descripcion']}"

            return respuesta

    return None  # Si no se encuentra coincidencia


# Solicitar el nombre del usuario al inicio de la conversación
def solicitar_nombre_usuario():
    nombre = ""
    while not nombre.strip():  # Mientras el nombre esté vacío o solo contenga espacios
        nombre = input("¡Hola! Soy tu Asistente Personal. ¿Cuál es tu nombre? (No puedes dejarlo en blanco): ")
        if not nombre.strip():
            print("Por favor, ingresa un nombre válido.")
    return nombre

nombre_usuario = solicitar_nombre_usuario()
print(f"¡Hola, {nombre_usuario}! Puedes preguntarme algo, agregar una categoría/subcategoría o borrar conocimiento.")


# Función para pedir un formato de fecha al usuario
def pedir_formato_fecha():
    print("IA: ¿En qué formato te gustaría agregar la fecha?")
    print("1. Día-Mes-Año")
    print("2. Solo año")

    eleccion = input("Elige una opción (1 o 2): ")

    if eleccion == "1":
        return "%d-%m-%Y"
    elif eleccion == "2":
        return "%Y"
    else:
        print("Opción inválida. Se usará el formato 'Día-Mes-Año'.")
        return "%d-%m-%Y"

# Controlar respuestas de sí/no
def obtener_respuesta_si_no(mensaje):
    respuesta = input(f"{mensaje} (si/no): ").lower()
    while respuesta not in ["si", "no"]:
        respuesta = input(f"Respuesta inválida. {mensaje} (si/no): ").lower()
    return respuesta == "si"

# Función para pedir un detalle opcional al usuario
def pedir_detalle_opcional(campo, tipo="texto"):
    if obtener_respuesta_si_no(f"¿Deseas agregar {campo}?"):
        if tipo == "fecha":
            while True:
                valor = input(f"Introduce {campo} (DD-MM-YYYY): ")
                if validar_fecha(valor, "%d-%m-%Y"):
                    return valor
                else:
                    print("Formato de fecha inválido. Intenta de nuevo.")
        elif tipo == "periodo":
            return input(f"Introduce el {campo} (ejemplo: 2020-2024): ")
        elif tipo == "texto":
            return input(f"Introduce {campo}: ")
    return None  # Si no se desea agregar, no devuelve nada

# Función para agregar detalles opcionales al conocimiento
def agregar_detalles(diccionario):
    campos = ["nombre_completo", "fecha", "periodo", "descripcion", "logros", "pais", "provincia", "cargo", "raza", "genero_musical"]
    for campo in campos:
        diccionario[campo] = pedir_detalle_opcional(campo)

# Función para agregar categoría
def agregar_categoria():
    nueva_categoria = input("Nombre de la nueva categoría: ")
    nueva_categoria = validar_campo_obligatorio(nueva_categoria, "Nombre de la nueva categoría")

    if nueva_categoria not in conocimientos:
        conocimientos[nueva_categoria] = {}

    # Preguntar si se va a crear una subcategoría
    if obtener_respuesta_si_no("¿Deseas agregar una subcategoría?"):
        nueva_subcategoria = input("Nombre de la subcategoría: ")
        nueva_subcategoria = validar_campo_obligatorio(nueva_subcategoria, "Nombre de la subcategoría")
        conocimientos[nueva_categoria][nueva_subcategoria] = {}

        # Llamar a la función para agregar detalles
        agregar_detalles(conocimientos[nueva_categoria][nueva_subcategoria])

    # Guardar los conocimientos
    guardar_datos(conocimientos, 'conocimientos.json')


# Función para borrar una categoría o subcategoría
def borrar_categoria():
    if not conocimientos:
        print("No hay categorías para borrar.")
        return

    # Mostrar lista de categorías con números
    print("Categorías disponibles:")
    categorias = list(conocimientos.keys())
    for idx, categoria in enumerate(categorias, start=1):
        print(f"{idx}. {categoria}")

    # Solicitar selección
    seleccion = input("Escribe el número o el nombre de la categoría que deseas borrar: ")

    # Verificar si la selección es un número
    if seleccion.isdigit():
        indice = int(seleccion) - 1
        if 0 <= indice < len(categorias):
            categoria_a_borrar = categorias[indice]
        else:
            print("Número inválido. Por favor intenta de nuevo.")
            return
    else:
        categoria_a_borrar = seleccion

    # Confirmar si existe la categoría
    if categoria_a_borrar in conocimientos:
        del conocimientos[categoria_a_borrar]
        print(f"La categoría '{categoria_a_borrar}' ha sido borrada.")
        # Guardar los conocimientos
        guardar_datos(conocimientos, 'conocimientos.json')
    else:
        print("Categoría no encontrada. Por favor intenta de nuevo.")



# Función para borrar una subcategoría dentro de una categoría
def borrar_subcategoria():
    if not conocimientos:
        print("No hay categorías disponibles.")
        return

    # Mostrar lista de categorías con números
    print("Categorías disponibles:")
    categorias = list(conocimientos.keys())
    for idx, categoria in enumerate(categorias, start=1):
        print(f"{idx}. {categoria}")

    # Solicitar selección de categoría
    seleccion_categoria = input("Escribe el número o el nombre de la categoría que contiene la subcategoría que deseas borrar: ")

    # Verificar si la selección de categoría es un número
    if seleccion_categoria.isdigit():
        indice_categoria = int(seleccion_categoria) - 1
        if 0 <= indice_categoria < len(categorias):
            categoria_seleccionada = categorias[indice_categoria]
        else:
            print("Número de categoría inválido. Por favor intenta de nuevo.")
            return
    else:
        categoria_seleccionada = seleccion_categoria

    # Confirmar si existe la categoría seleccionada
    if categoria_seleccionada in conocimientos:
        subcategorias = conocimientos[categoria_seleccionada]
        if not isinstance(subcategorias, dict):
            print(f"La categoría '{categoria_seleccionada}' no tiene subcategorías.")
            return

        # Mostrar lista de subcategorías con números
        print(f"Subcategorías disponibles en '{categoria_seleccionada}':")
        subcategorias_lista = list(subcategorias.keys())
        for idx, subcategoria in enumerate(subcategorias_lista, start=1):
            print(f"{idx}. {subcategoria}")

        # Solicitar selección de subcategoría
        seleccion_subcategoria = input("Escribe el número o el nombre de la subcategoría que deseas borrar: ")

        # Verificar si la selección de subcategoría es un número
        if seleccion_subcategoria.isdigit():
            indice_subcategoria = int(seleccion_subcategoria) - 1
            if 0 <= indice_subcategoria < len(subcategorias_lista):
                subcategoria_a_borrar = subcategorias_lista[indice_subcategoria]
            else:
                print("Número de subcategoría inválido. Por favor intenta de nuevo.")
                return
        else:
            subcategoria_a_borrar = seleccion_subcategoria

        # Confirmar si existe la subcategoría
        if subcategoria_a_borrar in subcategorias:
            del conocimientos[categoria_seleccionada][subcategoria_a_borrar]
            print(f"La subcategoría '{subcategoria_a_borrar}' ha sido borrada de la categoría '{categoria_seleccionada}'.")
            # Guardar los conocimientos
            guardar_datos(conocimientos, 'conocimientos.json')
        else:
            print("Subcategoría no encontrada. Por favor intenta de nuevo.")
    else:
        print("Categoría no encontrada. Por favor intenta de nuevo.")


# Función principal de preguntas
def preguntar(pregunta, conocimientos):
    # Verificar si "contexto" está en "conocimientos"
    if "contexto" not in conocimientos:
        conocimientos["contexto"] = {"ultimaPregunta": ""}  # Inicializa el contexto

    pregunta_limpia = eliminar_acentos(pregunta.lower())

    # Primero, salir si se pide
    if pregunta_limpia in ["salir", "terminar", "me voy"]:
        return "¡Adiós! Espero verte pronto."

    # Revisar si la pregunta anterior puede ayudar con el contexto
    respuesta_contexto = manejar_contexto(pregunta, conocimientos)  # Ahora pasa ambos argumentos
    if respuesta_contexto:
        return respuesta_contexto


    # Verificar si es un saludo
    respuesta_saludo = buscar_saludo(pregunta_limpia, conocimientos)
    if respuesta_saludo:
        actualizar_historial(pregunta, respuesta_saludo)
        return respuesta_saludo

    # Verificar si se pregunta por la hora actual
    if pregunta_limpia in ["que hora es", "que hora es?", "que hora es??", "decime la hora", "me decis la hora"]:
        hora_actual = datetime.now().strftime("%H:%M")
        respuesta = f"La hora actual es {hora_actual}."
        actualizar_historial(pregunta, respuesta)
        return respuesta

    # Verificar si se pregunta por la fecha actual
    elif pregunta_limpia in ["que fecha es hoy", "dime la fecha", "que fecha es hoy?", "que fecha es hoy??"]:
        fecha_actual = datetime.now().strftime("%d-%m-%Y")
        respuesta = f"La fecha de hoy es {fecha_actual}."
        actualizar_historial(pregunta, respuesta)
        return respuesta

    # Verificar si se pregunta por el día actual
    elif pregunta_limpia in ["que dia es hoy", "que dia estamos", "que dia es hoy?", "dime el dia"]:
        dia_actual = datetime.now().strftime("%A")
        dia_actual_espanol = dias_semana.get(dia_actual, "un día desconocido")
        respuesta = f"Hoy es {dia_actual_espanol}."
        actualizar_historial(pregunta, respuesta)
        return respuesta

    # Verificar si se pregunta por el año actual
    elif pregunta_limpia in ["que año es", "en que año estamos", "en que año estamos?", "dime el año"]:
        anio_actual = datetime.now().strftime("%Y")
        respuesta = f"Estamos en el año {anio_actual}."
        actualizar_historial(pregunta, respuesta)
        return respuesta

    # Verificar en el archivo conocimientos para signos zodiacales
    if "signo" in pregunta_limpia:
        for signo in signos_zodiacales:
            if signo in pregunta_limpia:
                respuesta = conocimientos.get(f"signo_{signo}", "Lo siento, no tengo información sobre ese signo.")
                actualizar_historial(pregunta, respuesta)
                return respuesta

    # Llamar a la función de animales, pasarle "conocimientos" también
    respuesta_animales = animales(pregunta, conocimientos)
    if respuesta_animales:
        actualizar_historial(pregunta, respuesta_animales)
        return respuesta_animales

    # Verificar si se pregunta por el presidente
    if "presidente" in pregunta_limpia:
        respuesta_presidente = conocimientos.get("presidente_actual", "No tengo información sobre el presidente.")
        actualizar_historial(pregunta, respuesta_presidente)
        return respuesta_presidente

    # Verificar si se pregunta por información de un cantante o música
    respuesta_musica = buscar_musica_por_claves(pregunta)
    if respuesta_musica:
        actualizar_historial(pregunta, respuesta_musica)
        return respuesta_musica

    # Buscar categoría relacionada con las palabras clave
    categoria = buscar_palabras_clave(pregunta_limpia)

    # Si no se encuentra una categoría, devolver un mensaje genérico
    if not categoria:
        return "No tengo suficiente información para responder."

    # Si la categoría tiene relaciones y coincide con la pregunta, devolver esa relación
    respuesta_relacion = obtener_relaciones(categoria, pregunta_limpia)
    if respuesta_relacion:
        return respuesta_relacion

    # Manejar preguntas amplias
    respuesta_incompleta = manejar_preguntas_ampias(categoria)
    if respuesta_incompleta:
        return respuesta_incompleta

    # Obtener una respuesta aleatoria de la categoría
    respuesta = obtener_respuesta(categoria)

    # Actualizar el contexto con la nueva pregunta
    actualizar_contexto(pregunta)

    # Retornar la respuesta obtenida
    actualizar_historial(pregunta, respuesta)
    return respuesta





def main():
    conocimientos = cargar_datos('conocimientos.json')  # Cargar conocimientos

    while True:
        pregunta = input("Tú: ")
        pregunta_limpia = eliminar_acentos(pregunta.lower())

        if pregunta_limpia in ["salir", "adios", "adiós"]:
            # Guardar los conocimientos
            guardar_datos(conocimientos, 'conocimientos.json')
            print("IA: ¡Adiós!")
            break

        # Aquí buscamos si la pregunta es sobre la IA
        respuesta_sobre_ia = responder_sobre_ia(pregunta_limpia, conocimientos)
        if respuesta_sobre_ia:
            print(f"IA: {respuesta_sobre_ia}")
            continue

        # Aqui buscamos si la pregunta esta en charla cotidiana
        respuesta_charla = manejar_charla(pregunta_limpia, conocimientos)
        if respuesta_charla:
            print(f"IA: {respuesta_charla}")
            actualizar_historial(pregunta, respuesta_charla)
            continue

        # Aquí se revisa si hay un saludo
        respuesta_saludo = buscar_saludo(pregunta_limpia, conocimientos)
        if respuesta_saludo:
            print(f"IA: {respuesta_saludo}")
            continue

        # Verificar si se pregunta por el día actual
        if pregunta_limpia in ["que dia es hoy", "que dia estamos", "que dia es hoy?", "dime el dia"]:
            dia_actual = datetime.now().strftime("%A")
            dia_actual_espanol = dias_semana.get(dia_actual, "un día desconocido")
            respuesta = f"Hoy es {dia_actual_espanol}."
            actualizar_historial(pregunta, respuesta)
            print(f"IA: {respuesta}")
            continue

        # Verificar si se pregunta por la hora actual
        elif pregunta_limpia in ["que hora es", "que hora es?", "que hora es??", "decime la hora", "me decis la hora"]:
            hora_actual = datetime.now().strftime("%H:%M")
            respuesta = f"La hora actual es {hora_actual}."
            actualizar_historial(pregunta, respuesta)
            print(f"IA: {respuesta}")
            continue

        # Verificar si se pregunta por la fecha actual
        elif pregunta_limpia in ["que fecha es hoy", "dime la fecha", "que fecha es hoy?", "que fecha es hoy??"]:
            fecha_actual = datetime.now().strftime("%d-%m-%Y")
            respuesta = f"La fecha de hoy es {fecha_actual}."
            actualizar_historial(pregunta, respuesta)
            print(f"IA: {respuesta}")
            continue

        # Verificar si se pregunta por el año actual
        elif pregunta_limpia in ["que año es", "en que año estamos", "en que año estamos?", "dime el año"]:
            anio_actual = datetime.now().strftime("%Y")
            respuesta = f"Estamos en el año {anio_actual}."
            actualizar_historial(pregunta, respuesta)
            print(f"IA: {respuesta}")
            continue

        # Verificar signos zodiacales
        if "signo" in pregunta_limpia:
            for signo in signos_zodiacales:
                if signo in pregunta_limpia:
                    respuesta = conocimientos.get(f"signo_{signo}", "Lo siento, no tengo información sobre ese signo.")
                    actualizar_historial(pregunta, respuesta)
                    print(f"IA: {respuesta}")
                    continue

       # Llamar a la función presidente
        respuesta_presidente = presidente(pregunta)
        if respuesta_presidente != "Lo siento, no tengo información sobre ese presidente.":
            print(f"IA: {respuesta_presidente}")
            continue

        # Verificar información de cantantes o música
        respuesta_musica = buscar_musica_por_claves(pregunta_limpia)
        if respuesta_musica:
            actualizar_historial(pregunta, respuesta_musica)
            print(f"IA: {respuesta_musica}")
            continue

        # 1. Manejar el contexto con una función personalizada
        respuesta_fuego = manejar_fuego(pregunta_limpia)
        if respuesta_fuego:
            print(f"IA: {respuesta_fuego}")
            actualizar_historial(pregunta, respuesta_fuego)
            continue

        # 2. Responder con contexto, si aplica
        respuesta_contexto = responder_con_contexto(pregunta_limpia)
        if respuesta_contexto:
            print(f"IA: {respuesta_contexto}")
            actualizar_historial(pregunta, respuesta_contexto)
            continue

        # 3. Buscar palabras clave o sinónimos y encontrar una categoría
        categoria = buscar_palabras_clave(pregunta_limpia, conocimientos)
        if categoria:
            # Verificar si la pregunta es amplia y requiere más información
            respuesta_amplia = manejar_preguntas_ampias(categoria)
            if respuesta_amplia:
                print(f"IA: {respuesta_amplia}")
                actualizar_historial(pregunta, respuesta_amplia)
                continue

            # Buscar relaciones dentro de la categoría
            respuesta_relacionada = obtener_relaciones(categoria, pregunta_limpia)
            if respuesta_relacionada:
                print(f"IA: {respuesta_relacionada}")
                actualizar_historial(pregunta, respuesta_relacionada)
                continue

            # Obtener una respuesta de la categoría
            respuesta_categoria = obtener_respuesta(categoria)
            print(f"IA: {respuesta_categoria}")
            actualizar_historial(pregunta, respuesta_categoria)
            continue

        # Si no se encuentra ninguna respuesta en los pasos anteriores, usar la función preguntar
        respuesta = preguntar(pregunta, conocimientos)
        actualizar_historial(pregunta, respuesta)  # Actualizar el historial con la nueva interacción
        print(f"IA: {respuesta}")


# Ejecutar el programa
if __name__ == "__main__":
    main()
