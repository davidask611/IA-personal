import json
#from difflib import SequenceMatcher
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

# TODO: Carga de datos
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

# Definición de la función para cargar animales
def cargar_animales(nombre_archivo='animales.json'):
    try:
        with open(nombre_archivo, 'r', encoding='utf-8') as archivo:
            return json.load(archivo)  # Cargar datos del archivo JSON
    except FileNotFoundError:
        print("Error: Archivo no encontrado.")
        return {}  # Retorna un diccionario vacío si no se encuentra el archivo
    except json.JSONDecodeError:
        print("Error: Formato inválido en el archivo JSON.")
        return {}  # Retorna un diccionario vacío si hay un error de formato

# Cargar datos desde el json animales
animales_data = cargar_animales('animales.json')  # Cargar datos de animales

# Cargar datos desde el JSON al inicio de tu script
conocimientos = cargar_datos('conocimientos.json')

# Asegurarse de que los signos están en el diccionario 'conocimientos'
signos_zodiacales = conocimientos.get("signos_zodiacales", {})

# TODO Iniciar listas vacías
#respuestas_cache = {}
UMBRAL_SIMILITUD = 0.6
historial_preguntas = []
historial_conversacion = []  # Lista para almacenar el historial de conversación
MAX_HISTORIAL = 6  # Limitar el historial a los últimos 6 mensajes

# TODO Funciones acentos, limpieza, historial, etc
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

def guardar_datos(conocimientos, nombre_archivo='conocimientos.json'):
    try:
        with open(nombre_archivo, 'w', encoding='utf-8') as archivo:
            json.dump(conocimientos, archivo, ensure_ascii=False, indent=4)
        print(f"Datos guardados exitosamente en '{nombre_archivo}'.")
    except IOError as e:
        print(f"Error al guardar los datos en el archivo: {e}")
    return None

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


# TODO funciones de categoria
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

# Función para buscar palabras clave en la pregunta
def buscar_palabras_clave(pregunta, conocimientos):  # Cambiar datos por conocimientos
    for categoria, info in conocimientos["categorias"].items():
        if "palabrasClave" in info:  # Verificar si 'palabrasClave' existe
            for palabra in info["palabrasClave"]:
                if palabra in pregunta.lower():
                    return categoria
    return None


# Función para obtener una respuesta de la categoría
#def obtener_respuesta(categoria):
#    if categoria:
#        respuestas = conocimientos["categorias"][categoria]["respuesta"]
#        return random.choice(respuestas)  # Respuesta dinámica
#    return "No tengo suficiente información para responder."


# Función para obtener una respuesta más específica si hay relaciones
def obtener_relaciones(categoria, pregunta):
    if categoria:
        relaciones = conocimientos["categorias"][categoria].get("relaciones", {})
        for palabra in relaciones:
            if palabra in pregunta.lower():
                return relaciones[palabra]
    return None


# Función para actualizar el contexto
def actualizar_contexto(pregunta, conocimientos):
    conocimientos["contexto"]["ultimaPregunta"] = pregunta
    guardar_datos(conocimientos, 'conocimientos.json')  # Guarda los cambios en el archivo JSON


# Función para manejar el contexto
def manejar_contexto(pregunta, conocimientos):
    ultima_pregunta = conocimientos["contexto"]["ultimaPregunta"]
    if ultima_pregunta and "fuego" in ultima_pregunta.lower() and "como" in pregunta.lower():
        return "¿Te refieres a cómo apagar el fuego o cómo mantenerlo encendido?"
    return None


# Función para manejar preguntas vagas o amplias
def manejar_preguntas_ampias(categoria):
    if categoria and "respuestaIncompleta" in conocimientos["categorias"][categoria]:
        return conocimientos["categorias"][categoria]["respuestaIncompleta"]
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


# TODO Funciones complejas (saludo, datosdelaIA, charla, presidente, signoszodiacales, musica, chiste, animal)
# Función para buscar un saludo
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


# Función para responder sobre la IA
def responder_sobre_ia(pregunta_limpia, conocimientos):
    if pregunta_limpia in conocimientos["datosdelaIA"]:
        return conocimientos["datosdelaIA"][pregunta_limpia]
    return None  # Si la pregunta no está en el JSON, devolvemos None


# Función para manejar la charla cotidiana
def manejar_charla(pregunta, conocimientos):
    # Limpiar la pregunta para que coincida con las claves del diccionario
    pregunta_limpia = eliminar_acentos(pregunta.lower())

    # Buscar en el JSON de conocimientos
    return conocimientos.get('charla', {}).get(pregunta_limpia, None)


# Función buscar presidente, nombre, año y pasarlo
def presidente(pregunta, conocimientos):
    # Convertir la pregunta a minúsculas sin acentos
    pregunta_limpia = eliminar_acentos(pregunta.lower())

    # Dividir la pregunta en palabras
    palabras_pregunta = pregunta_limpia.split()

    # Lista de presidentes en el diccionario
    presidentes = conocimientos.get("presidente", {})

    # Verificar si la pregunta contiene la palabra "presidente"
    if "presidente" in palabras_pregunta or "fue" in palabras_pregunta or "era" in palabras_pregunta:
        # Buscar si hay un año en la pregunta
        anio_encontrado = re.search(r"\b\d{4}\b", pregunta_limpia)  # Buscar un año de 4 cifras

        # Si se encuentra un año de 4 cifras
        if anio_encontrado:
            anio = int(anio_encontrado.group())

            # Recorrer todos los presidentes para verificar su periodo
            for nombre_presidente, detalles in presidentes.items():
                periodo = detalles['periodo'].split(' - ')
                anio_inicio = int(periodo[0])
                anio_fin = int(periodo[1]) if periodo[1] != "presente" else datetime.now().year

                # Verificar si el año está dentro del periodo del presidente
                if anio_inicio <= anio <= anio_fin:
                    return (f"{detalles['nombre_completo']} fue presidente entre {detalles['periodo']}.")

            # Si no se encuentra un presidente para ese año
            return f"No tengo información sobre quién fue presidente en el año {anio}. Intenta con 'quién fue presidente en el año 2022'."

        # Verificar si se encuentra un año de solo dos cifras
        anio_dos_cifras = re.search(r"\b\d{2}\b", pregunta_limpia)
        if anio_dos_cifras:
            return "No tengo información sobre ese presidente o esa fecha. Por favor, intenta con un año de cuatro cifras, como 'quién fue presidente en el año 2022'."

        # Si no se encontró un año, buscar por el nombre del presidente
        for nombre_presidente, detalles in presidentes.items():
            # Limpiar el nombre del presidente para compararlo con la pregunta
            nombre_presidente_limpio = eliminar_acentos(nombre_presidente.lower())

            # Verificar si el nombre del presidente está en la pregunta
            if nombre_presidente_limpio in palabras_pregunta:
                return (f"{detalles['nombre_completo']} fue presidente entre {detalles['periodo']}. "
                        f"Descripción: {detalles['descripcion']}")

    return "Lo siento, no tengo información sobre ese presidente."


# Función para obtener la descripción de un signo zodiacal desde el diccionario cargado
def obtener_signo(signo):
    signo = signo.lower()  # Convertimos a minúsculas para evitar errores de mayúsculas/minúsculas
    if signo in signos_zodiacales:
        # Construir la respuesta con la descripción y más detalles del signo
        info_signo = signos_zodiacales[signo]
        compatibilidad = ", ".join(info_signo['compatibilidad'])  # Convertir lista a cadena
        descripcion = (f"El signo {signo.capitalize()} cubre desde {info_signo['fecha-fecha']}. "
                       f"Su elemento es {info_signo['elemento']}. {info_signo['descripcion']} "
                       f"Es compatible con: {compatibilidad}.")
        return descripcion
    else:
        return "Lo siento, no tengo información sobre ese signo."

# Función para detectar signos zodiacales con 're'
def detectar_signo(pregunta):
    pregunta_limpia = eliminar_acentos(pregunta.lower())  # Eliminar acentos y convertir a minúsculas

    # Crear un patrón que busque signos zodiacales
    signos = '|'.join(signos_zodiacales.keys())  # Crear un patrón para todos los signos (ej. 'aries|tauro|geminis')
    patron = rf"\b({signos})\b"  # Solo buscar signos, sin necesidad de "signo" antes o después

    # Buscar el patrón en la pregunta
    coincidencia = re.search(patron, pregunta_limpia)

    if coincidencia:
        # Si se encuentra un signo en la pregunta, devolver la información del signo
        signo_encontrado = coincidencia.group(1)
        return obtener_signo(signo_encontrado)

    return None  # Si no se encuentra ninguna coincidencia

# TODO # Función para buscar música o cantante por claves
"""
def buscar_musica_por_claves(pregunta, conocimientos):
    # Convertir la pregunta a minúsculas sin acentos
    pregunta_limpia = eliminar_acentos(pregunta.lower())

    # Dividir la pregunta en palabras
    palabras_pregunta = pregunta_limpia.split()

    # Lista de géneros musicales en la categoría 'musica'
    musica = conocimientos.get("musica", {})

    # Palabras clave a buscar
    palabras_cantante = ["musica", "cantante", "informacion"]
    palabras_canciones = ["canciones", "temas", "exitos"]

    # Inicializar una variable para saber si se detectó un nombre pero no se encontró en el JSON
    nombre_detectado = None

    # Lista de todos los nombres de cantantes en el JSON para comparación
    nombres_cantantes_json = [eliminar_acentos(nombre.lower()) for genero in musica.values() for nombre in genero.keys()]

    # Verificar si algún nombre de cantante en el JSON aparece en la pregunta
    for palabra in palabras_pregunta:
        if palabra in nombres_cantantes_json:
            nombre_detectado = palabra
            break

    # Buscar por palabras clave relacionadas con 'cantante' y el nombre del cantante
    for genero, artistas in musica.items():
        for nombre_cantante, detalles in artistas.items():
            nombre_cantante_limpio = eliminar_acentos(nombre_cantante.lower())

            # Verificar si el nombre del cantante está en la pregunta
            if nombre_cantante_limpio in palabras_pregunta:
                # Si se detecta también la palabra 'cantante' o 'informacion'
                if any(palabra in palabras_pregunta for palabra in palabras_cantante):
                    # Construir la respuesta con información básica
                    respuesta = (f"{nombre_cantante}: {detalles['nombre_completo']} es un cantante de {genero}. "
                                 f"Nació el {detalles['fecha_nacimiento']}. {detalles['descripcion']}")
                    return respuesta

                # Si se detecta la palabra 'canciones', 'temas', o 'exitos'
                elif any(palabra in palabras_pregunta for palabra in palabras_canciones):
                    if detalles.get("canciones"):
                        canciones = ', '.join(detalles["canciones"])
                        return f"Las canciones más exitosas de {nombre_cantante} son: {canciones}."
                    else:
                        return f"No tengo información sobre las canciones de {nombre_cantante}."

    # If-else para manejar los mensajes de error:
    if nombre_detectado:
        # Si se detectó un nombre pero no se encontró información en el JSON
        return f"No tengo información sobre {nombre_detectado}. Intenta con otro nombre o verifica la ortografía."

    # Si no se encuentra coincidencia y no se detectó un nombre, devolvemos None
    return None
"""

# Función para obtener un chiste aleatorio
def obtener_chiste():
    try:
        lista_chistes = conocimientos["chiste"]["lista_chistes"]
        return random.choice(lista_chistes)
    except KeyError:
        return "Lo siento, no tengo chistes guardados."

# TODO # Función buscar animales o características y devolverlo
"""def animales(pregunta, animales_data):
    # Convertir la pregunta a minúsculas y eliminar acentos
    pregunta_limpia = eliminar_acentos(pregunta.lower())

    # Detectar palabras clave (animal, raza o características)
    if "perro" in pregunta_limpia:
        subcategoria = "perro"
    elif "gato" in pregunta_limpia or "felino" in pregunta_limpia:
        subcategoria = "gato"
    elif "ave" in pregunta_limpia or "pajaro" in pregunta_limpia:
        subcategoria = "ave"
    else:
        return "No comprendo a qué animal te refieres. Intenta especificar 'perro', 'gato', 'ave', etc."

    # Buscar la raza específica dentro de la subcategoría
    razas = animales_data.get("animal", {}).get(subcategoria, {})

    # Buscar la raza o características en la pregunta
    for raza, info in razas.items():
        if raza in pregunta_limpia:
            return (f"{info['nombre_completo']}: {info['descripcion']} "
                    f"Características: Peligro: {info['caracteristicas']['peligro']}, "
                    f"Docilidad: {info['caracteristicas']['docilidad']}, "
                    f"Amabilidad: {info['caracteristicas']['amabilidad']}")

    # Si no se encuentra la raza o información
    return f"No tengo información sobre esa raza de {subcategoria}. Intenta reformular la pregunta."
"""
# TODO verificar_musica_animal
def verificar_musica_animal(pregunta, conocimientos, animales):
    # Convertir la pregunta a minúsculas y eliminar acentos
    pregunta_limpia = eliminar_acentos(pregunta.lower())

    # Verificar si la pregunta es sobre animales
    if "perro" in pregunta_limpia or "gato" in pregunta_limpia or "ave" in pregunta_limpia or "animal" in pregunta_limpia:
        # Procesar la pregunta como una consulta sobre animales
        subcategoria = None
        if "perro" in pregunta_limpia:
            subcategoria = "perro"
        elif "gato" in pregunta_limpia or "felino" in pregunta_limpia:
            subcategoria = "gato"
        elif "ave" in pregunta_limpia or "pajaro" in pregunta_limpia:
            subcategoria = "ave"

        # Buscar la raza específica dentro de la subcategoría
        if subcategoria:
            animales_data = animales.get("animal", {})
            razas = animales_data.get(subcategoria, {})

            # Buscar la raza o características en la pregunta
            for raza, info in razas.items():
                if raza in pregunta_limpia:
                    return (f"{info['nombre_completo']}: {info['descripcion']} "
                    f"Características: Peligro: {info['caracteristicas']['peligro']}, "
                    f"Docilidad: {info['caracteristicas']['docilidad']}, "
                    f"Amabilidad: {info['caracteristicas']['amabilidad']}")

            return f"No tengo información sobre esa raza de {subcategoria}. Intenta reformular la pregunta."

        return "No comprendo a qué animal te refieres. Intenta especificar 'perro', 'gato', 'ave', etc."

    # Verificar si la pregunta es sobre música
    elif "musica" in pregunta_limpia or "cantante" in pregunta_limpia or "canciones" in pregunta_limpia:
        # Procesar la pregunta como una consulta sobre música
        musica = conocimientos.get("musica", {})
        palabras_pregunta = pregunta_limpia.split()

        # Lista de palabras clave a buscar
        palabras_cantante = ["musica", "cantante", "informacion"]
        palabras_canciones = ["canciones", "temas", "exitos"]

        nombre_detectado = None
        nombres_cantantes_json = [eliminar_acentos(nombre.lower()) for genero in musica.values() for nombre in genero.keys()]

        # Verificar si algún nombre de cantante en el JSON aparece en la pregunta
        for palabra in palabras_pregunta:
            if palabra in nombres_cantantes_json:
                nombre_detectado = palabra
                break

        # Buscar por palabras clave relacionadas con el cantante y su información
        for genero, artistas in musica.items():
            for nombre_cantante, detalles in artistas.items():
                nombre_cantante_limpio = eliminar_acentos(nombre_cantante.lower())

                if nombre_cantante_limpio in palabras_pregunta:
                    if any(palabra in palabras_pregunta for palabra in palabras_cantante):
                        respuesta = (f"{nombre_cantante}: {detalles['nombre_completo']} es un cantante de {genero}. "
                                     f"Nació el {detalles['fecha_nacimiento']}. {detalles['descripcion']}")
                        return respuesta

                    elif any(palabra in palabras_pregunta for palabra in palabras_canciones):
                        if detalles.get("canciones"):
                            canciones = ', '.join(detalles["canciones"])
                            return f"Las canciones más exitosas de {nombre_cantante} son: {canciones}."
                        else:
                            return f"No tengo información sobre las canciones de {nombre_cantante}."

        if nombre_detectado:
            return f"No tengo información sobre {nombre_detectado}. Intenta con otro nombre o verifica la ortografía."

        return "No tengo suficiente información sobre ese artista o género musical. Intenta reformular la pregunta."

    # Si la pregunta no está relacionada con música ni con animales
    return "No tengo suficiente información para responder esta pregunta."


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


# TODO Agregar categoria
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



# TODO Función principal de preguntar
def preguntar(pregunta, conocimientos, animales_data):
    # Verificar si "contexto" está en "conocimientos"
    if "contexto" not in conocimientos:
        conocimientos["contexto"] = {"ultimaPregunta": ""}  # Inicializa el contexto

    pregunta_limpia = eliminar_acentos(pregunta.lower())

    # Primero, salir si se pide
    if pregunta_limpia in ["salir", "terminar", "me voy"]:
        return "¡Adiós! Espero verte pronto."

    # Revisar si la pregunta anterior puede ayudar con el contexto
    #respuesta_contexto = manejar_contexto(pregunta, conocimientos)
    #if respuesta_contexto:
    #    return respuesta_contexto

    # Verificar si es un saludo
    respuesta_saludo = buscar_saludo(pregunta_limpia, conocimientos)
    if respuesta_saludo:
        actualizar_historial(pregunta, respuesta_saludo)
        return respuesta_saludo

    # Verificar si se pregunta por el presidente
    respuesta_presidente = presidente(pregunta_limpia, conocimientos)  # Pasa los conocimientos aquí
    if respuesta_presidente != "Lo siento, no tengo información sobre ese presidente.":
        return respuesta_presidente

    # Verificar si se pregunta por signos zodiacales
    respuesta_signo = detectar_signo(pregunta_limpia)
    if respuesta_signo:
        return respuesta_signo

     # Verificar si la pregunta es sobre música o animales usando la nueva función
    respuesta_musica_animal = verificar_musica_animal(pregunta, conocimientos, animales_data)
    if respuesta_musica_animal != "No tengo suficiente información para responder esta pregunta.":
        return respuesta_musica_animal

    # Verificar si se pregunta por música o cantante
    #respuesta_musica = buscar_musica_por_claves(pregunta_limpia, conocimientos)

    # Solo retornamos si la respuesta NO es None
    #if respuesta_musica is not None:
    #    return respuesta_musica


    # Primero verificamos si es una pregunta sobre animales
    #respuesta_animal = animales(pregunta_limpia, animales_data)
    #if respuesta_animal:
    #    return respuesta_animal

    # Aquí puedes seguir revisando otras preguntas o información

    return "No tengo suficiente información para responder...intenta reformular o usar otros terminos."


# TODO Funcion MAIN principal
def main():
    conocimientos = cargar_datos('conocimientos.json')  # Cargar conocimientos
    animales_data = cargar_animales('animales.json')  # Cargar datos de animales

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

        # Aquí buscamos si la pregunta está en charla cotidiana
        respuesta_charla = manejar_charla(pregunta_limpia, conocimientos)
        if respuesta_charla:
            print(f"IA: {respuesta_charla}")
            actualizar_historial(pregunta, respuesta_charla)
            continue

        # Aquí se revisa si hay un saludo
        respuesta_saludo = buscar_saludo(pregunta_limpia, conocimientos)
        if respuesta_saludo:
            print(f"IA: {respuesta_saludo}")
            actualizar_historial(pregunta, respuesta_saludo)  # Actualizar el historial con la respuesta de saludo
            continue

        # Llamar a la función preguntar para manejar todas las preguntas
        respuesta = preguntar(pregunta, conocimientos, animales_data)  # Aquí llamas a preguntar
        print(f"IA: {respuesta}")
        actualizar_historial(pregunta, respuesta)  # Actualizar el historial con la nueva interacción



# TODO Ejecutar el programa
if __name__ == "__main__":
    main()
