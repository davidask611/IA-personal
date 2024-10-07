import json
from difflib import SequenceMatcher
from datetime import datetime
import unicodedata
import random
import re

import json

# Cache en memoria
respuestas_cache = {}

# Función para cargar el archivo JSON al inicio del programa
def cargar_datos(nombre_archivo='datos.json'):
    try:
        with open(nombre_archivo, 'r', encoding='utf-8') as archivo:
            datos = json.load(archivo)  # Cargar el contenido del archivo

            # Cargar signos zodiacales
            if "signos_zodiacales" in datos:
                for signo, detalles in datos["signos_zodiacales"].items():
                    respuestas_cache[f"signo_{signo}"] = detalles["descripcion"]  # Llenar el cache con la descripción

            # Puedes repetir el proceso para otras categorías, como música
            if "musica" in datos:
                for genero, detalles in datos["musica"].items():
                    # Llenar el cache con descripciones de música
                    respuestas_cache[f"cantante_{detalles['nombre_completo'].lower()}"] = detalles["descripcion"]

            return datos  # Retornar los datos cargados

    except FileNotFoundError:
        # Si el archivo no existe, devuelve un diccionario vacío
        return {}
    except json.JSONDecodeError:
        # Si el archivo está vacío o tiene un error, devuelve un diccionario vacío
        return {}

# Función para guardar el estado actual en el archivo JSON
def guardar_datos(datos, nombre_archivo='datos.json'):
    with open(nombre_archivo, 'w', encoding='utf-8') as archivo:
        json.dump(datos, archivo, indent=4, ensure_ascii=False)

# Cargar los conocimientos
conocimientos = cargar_datos('conocimientos.json')


UMBRAL_SIMILITUD = 0.85

# Diccionario para traducir los días de la semana al español
dias_semana = {
    "Monday": "lunes",
    "Tuesday": "martes",
    "Wednesday": "miércoles",
    "Thursday": "jueves",
    "Friday": "viernes",
    "Saturday": "sábado",
    "Sunday": "domingo"
}

# Función para eliminar acentos
def eliminar_acentos(texto):
    if isinstance(texto, list):
        # Si texto es una lista, aplicamos la función a cada elemento de la lista
        texto = [eliminar_acentos(t) for t in texto]  # Llamamos recursivamente a la función para cada string
    else:
        # Reemplazar la ñ temporalmente
        texto = texto.replace("ñ", "~")

        # Normalizar acentos
        texto = ''.join(
            c for c in unicodedata.normalize('NFD', texto)
            if unicodedata.category(c) != 'Mn'
        )

        # Devolver la ñ
        texto = texto.replace("~", "ñ")

    return texto


# Función para calcular la similitud entre dos cadenas
def similar(a, b):
    a = eliminar_acentos(a)  # Eliminamos acentos de ambas cadenas
    b = eliminar_acentos(b)
    return SequenceMatcher(None, a, b).ratio()

# Validar que una categoría exista
def validar_categoria(categoria):
    return categoria in conocimientos

# Validar campos obligatorios
def validar_campo_obligatorio(campo, mensaje):
    while not campo:
        campo = input(f"{mensaje} (Este campo es obligatorio): ")
    return campo

# Validar formato de fecha
def validar_fecha(fecha, formato):
    try:
        datetime.strptime(fecha, formato)
        return True
    except ValueError:
        return False



# Asegurarse de que los signos están en el diccionario 'conocimientos'
signos_zodiacales = conocimientos.get("signos_zodiacales", {})

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


# Busca la categoria y su lista, de no encontrar avisa del error
def obtener_chiste():
    try:
        lista_chistes = conocimientos["chiste"]["lista_chistes"]
        return random.choice(lista_chistes)
    except KeyError:
        return "Lo siento, no tengo chistes guardados."



# Buscar presidente y nombre clave y darlo
def buscar_por_claves(pregunta):
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

    return None  # Si no se encontró coincidencia

# Nueva función 'responder' que procesa la pregunta
def responder(pregunta):
    # Buscar si la frase contiene las palabras 'presidente' y un nombre
    respuesta_presidente = buscar_por_claves(pregunta)
    if respuesta_presidente:
        return respuesta_presidente

    # Verificar si la pregunta es sobre un chiste
    if "chiste" in eliminar_acentos(pregunta.lower()):
        chiste = obtener_chiste()
        return f"Aquí tienes un chiste: {chiste}"

    return "Lo siento, no entiendo la pregunta."


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



# Función para responder a una pregunta
def preguntar(pregunta):
    pregunta_limpia = eliminar_acentos(pregunta.lower())

    # Verificar en el cache primero para signos zodiacales
    if "signo" in pregunta_limpia:
        for signo in signos_zodiacales:
            if signo in pregunta_limpia:
                return respuestas_cache.get(f"signo_{signo}", "Lo siento, no tengo información sobre ese signo.")

    # Verificar si se pregunta por el día actual
    if pregunta_limpia in ["que dia es hoy", "que dia estamos", "que dia es hoy?", "dime el dia"]:
        dia_actual = datetime.now().strftime("%A")  # Nombre del día en inglés
        dia_actual_espanol = dias_semana.get(dia_actual, "un día desconocido")  # Traducir al español
        return f"Hoy es {dia_actual_espanol}."

    # Verificar si se pregunta por la hora actual
    elif pregunta_limpia in ["que hora es", "que hora es?", "que hora es??", "decime la hora", "me decis la hora"]:
        hora_actual = datetime.now().strftime("%H:%M")  # Formato de 24 horas
        return f"La hora actual es {hora_actual}."

    # Verificar si se pregunta por la fecha actual
    elif pregunta_limpia in ["que fecha es hoy", "dime la fecha", "que fecha es hoy?", "que fecha es hoy??"]:
        fecha_actual = datetime.now().strftime("%d-%m-%Y")  # Fecha en formato dd-mm-yyyy
        return f"La fecha de hoy es {fecha_actual}."

    # Verificar si se pregunta por el año actual
    elif pregunta_limpia in ["que año es", "en que año estamos", "en que año estamos?", "dime el año"]:
        anio_actual = datetime.now().strftime("%Y")  # Año actual
        return f"Estamos en el año {anio_actual}."

    # Verificar si se pregunta por información de un cantante o música
    respuesta_musica = buscar_musica_por_claves(pregunta)
    if respuesta_musica:
        return respuesta_musica

    # Buscar en los conocimientos almacenados
    for categoria, subcategorias in conocimientos.items():
        if similar(categoria, pregunta) > UMBRAL_SIMILITUD:
            return subcategorias

        for subcategoria, detalles in subcategorias.items():
            if similar(subcategoria, pregunta) > UMBRAL_SIMILITUD:
                return detalles

            # Validar si 'detalles' es un diccionario
            if isinstance(detalles, dict):
                for clave, valor in detalles.items():
                    if similar(clave, pregunta) > UMBRAL_SIMILITUD:
                        return valor
            else:
                # Si detalles no es un diccionario, devolverlo directamente
                if similar(detalles, pregunta) > UMBRAL_SIMILITUD:
                    return detalles

    return "Lo siento, no tengo información sobre eso."


# Función principal
def main():
    conocimientos.update(cargar_datos())  # Cargar los conocimientos desde el archivo

    while True:
        pregunta = input("Tú: ")
        pregunta_limpia = eliminar_acentos(pregunta.lower())

        if pregunta_limpia in ["salir", "adios", "adiós"]:
            # Guardar los conocimientos
            guardar_datos(conocimientos, 'conocimientos.json')
            print("IA: ¡Adiós!")
            break

        elif pregunta_limpia == "agregar categoria":
            agregar_categoria()

        elif pregunta_limpia in ["dime un chiste", "otro chiste", "sabes algun chiste", "me cuentas un chiste", "cuentame un chiste", "quiero un chiste"]:
            print("Buscando chiste...")
            chiste = obtener_chiste()
            print(f"IA: {chiste}")

        elif pregunta_limpia == "deseo borrar algo":
            tipo_borrado = input("¿Deseas borrar una categoría o una subcategoría? (categoria/subcategoria): ").lower()
            if tipo_borrado == "categoria":
                borrar_categoria()
            elif tipo_borrado == "subcategoria":
                borrar_subcategoria()
            else:
                print("IA: Opción no reconocida. Por favor, elige 'categoria' o 'subcategoria'.")

        else:
            # Primero, buscar si hay una respuesta relacionada con signos zodiacales
            respuesta_signo = detectar_signo(pregunta)
            if respuesta_signo:
                print(f"IA: {respuesta_signo}")
                continue  # Saltar a la siguiente iteración del bucle

            # Luego, buscar si hay una respuesta relacionada con música
            respuesta_musica = buscar_musica_por_claves(pregunta)
            if respuesta_musica:
                print(f"IA: {respuesta_musica}")
                continue  # Saltar a la siguiente iteración del bucle

            # Luego, buscar si hay una respuesta relacionada con presidentes
            respuesta_presidente = buscar_por_claves(pregunta)
            if respuesta_presidente:
                print(f"IA: {respuesta_presidente}")
                continue  # Saltar a la siguiente iteración del bucle

            # Si no se encuentra respuesta, utilizar la función preguntar
            respuesta = preguntar(pregunta)
            print(f"IA: {respuesta}")


# Ejecutar el programa
if __name__ == "__main__":
    main()
