import json
from difflib import SequenceMatcher
from datetime import datetime
import unicodedata

# Diccionario que almacenará conocimientos organizados por categorías
conocimientos = {}

UMBRAL_SIMILITUD = 0.75

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
    return ''.join(
        c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn'
    ).lower()

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

    # Aquí continuarías con las demás verificaciones o lógica


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

# Función para agregar una nueva categoría o subcategoría
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
    else:
        conocimientos[nueva_categoria] = {}

    # Detalles adicionales
    nombre_completo = input("Nombre completo (opcional): ")
    if nombre_completo:
        conocimientos[nueva_categoria][nueva_subcategoria]["nombre_completo"] = nombre_completo

    # Validar formato y añadir fecha
    if obtener_respuesta_si_no("¿Deseas agregar una fecha?"):
        formato_fecha = pedir_formato_fecha()
        fecha = input(f"Introduce la fecha en formato {formato_fecha.replace('%D', '')}: ")
        while not validar_fecha(fecha, formato_fecha):
            print("Formato de fecha inválido.")
            fecha = input(f"Introduce la fecha en formato {formato_fecha.replace('%D', '')}: ")
        conocimientos[nueva_categoria][nueva_subcategoria]["fecha"] = fecha

    # Agregar más detalles
    descripcion = input("Descripción (opcional): ")
    logros = input("Logros (opcional): ")
    pais = input("País (opcional): ")
    provincia = input("Provincia (opcional): ")
    cargo = input("Cargo (opcional): ")

    # Añadir al diccionario solo los campos con valores
    if descripcion:
        conocimientos[nueva_categoria][nueva_subcategoria]["descripcion"] = descripcion
    if logros:
        conocimientos[nueva_categoria][nueva_subcategoria]["logros"] = logros
    if pais:
        conocimientos[nueva_categoria][nueva_subcategoria]["pais"] = pais
    if provincia:
        conocimientos[nueva_categoria][nueva_subcategoria]["provincia"] = provincia
    if cargo:
        conocimientos[nueva_categoria][nueva_subcategoria]["cargo"] = cargo

    # Guardar los conocimientos en un archivo JSON
    guardar_conocimientos()

    # Preguntar si quiere agregar más subcategorías
    if obtener_respuesta_si_no("¿Deseas agregar más subcategorías dentro de esta subcategoría?"):
        agregar_subcategoria(nueva_categoria, nueva_subcategoria)

# Función para agregar subcategoría dentro de una subcategoría
def agregar_subcategoria(categoria, subcategoria):
    nueva_subcategoria = input("Nombre de la subcategoría dentro de la subcategoría: ")
    conocimientos[categoria][subcategoria][nueva_subcategoria] = {}

    # Repetir el proceso para agregar detalles
    nombre_completo = input("Nombre completo (opcional): ")
    if nombre_completo:
        conocimientos[categoria][subcategoria][nueva_subcategoria]["nombre_completo"] = nombre_completo

    if obtener_respuesta_si_no("¿Deseas agregar una fecha a la subcategoría?"):
        formato_fecha = pedir_formato_fecha()
        fecha = input(f"Introduce la fecha en formato {formato_fecha.replace('%D', '')}: ")
        while not validar_fecha(fecha, formato_fecha):
            print("Formato de fecha inválido.")
            fecha = input(f"Introduce la fecha en formato {formato_fecha.replace('%D', '')}: ")
        conocimientos[categoria][subcategoria][nueva_subcategoria]["fecha"] = fecha

    descripcion = input("Descripción (opcional): ")
    logros = input("Logros (opcional): ")
    pais = input("País (opcional): ")
    provincia = input("Provincia (opcional): ")
    cargo = input("Cargo (opcional): ")

    # Guardar información adicional
    if descripcion:
        conocimientos[categoria][subcategoria][nueva_subcategoria]["descripcion"] = descripcion
    if logros:
        conocimientos[categoria][subcategoria][nueva_subcategoria]["logros"] = logros
    if pais:
        conocimientos[categoria][subcategoria][nueva_subcategoria]["pais"] = pais
    if provincia:
        conocimientos[categoria][subcategoria][nueva_subcategoria]["provincia"] = provincia
    if cargo:
        conocimientos[categoria][subcategoria][nueva_subcategoria]["cargo"] = cargo

    guardar_conocimientos()

# Función para borrar una categoría, subcategoría o un detalle específico
def borrar_conocimiento():
    categoria = input("¿Qué categoría deseas borrar?: ")
    if categoria in conocimientos:
        subcategoria = input("¿Deseas borrar una subcategoría dentro de esta categoría? (si/no): ").lower()
        if subcategoria == "si":
            nombre_subcategoria = input("Nombre de la subcategoría: ")
            if nombre_subcategoria in conocimientos[categoria]:
                detalle = input("¿Deseas borrar un detalle específico de esta subcategoría? (si/no): ").lower()
                if detalle == "si":
                    detalle_borrar = input("Nombre del detalle a borrar (ej. fecha, descripcion, etc.): ")
                    if detalle_borrar in conocimientos[categoria][nombre_subcategoria]:
                        del conocimientos[categoria][nombre_subcategoria][detalle_borrar]
                        print(f"Detalle '{detalle_borrar}' borrado con éxito.")
                    else:
                        print(f"El detalle '{detalle_borrar}' no existe.")
                else:
                    del conocimientos[categoria][nombre_subcategoria]
                    print(f"Subcategoría '{nombre_subcategoria}' borrada con éxito.")
            else:
                print(f"La subcategoría '{nombre_subcategoria}' no existe.")
        else:
            del conocimientos[categoria]
            print(f"Categoría '{categoria}' borrada con éxito.")
    else:
        print(f"La categoría '{categoria}' no existe.")

    guardar_conocimientos()

# Función para guardar los conocimientos en un archivo JSON
def guardar_conocimientos():
    with open("conocimientos.json", "w") as archivo:
        json.dump(conocimientos, archivo, indent=4)
    print("Conocimientos guardados con éxito.")

# Función para cargar los conocimientos desde un archivo JSON
def cargar_conocimientos():
    try:
        with open("conocimientos.json", "r") as archivo:
            return json.load(archivo)
    except FileNotFoundError:
        return {}

# Función para responder a una pregunta
def preguntar(pregunta):
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
"""def main():
    conocimientos.update(cargar_conocimientos())
    #nombre_usuario = solicitar_nombre_usuario()
    #print(f"¡Hola, {nombre_usuario}! Puedes preguntarme algo, agregar una categoría/subcategoría o borrar conocimiento.")

    while True:
        pregunta = input("Tú: ")
        pregunta_limpia = eliminar_acentos(pregunta.lower())

        if pregunta_limpia in ["salir", "adios", "adiós"]:
            guardar_conocimientos()
            print("IA: ¡Adiós!")
            break
        elif pregunta_limpia == "agregar categoria":
            agregar_categoria()
        elif pregunta_limpia == "deseo borrar algo":
            borrar_conocimiento()
        else:
            respuesta = preguntar(pregunta)
            print(f"IA: {respuesta}")
"""

# Función principal
def main():
    conocimientos.update(cargar_conocimientos())
    #nombre_usuario = solicitar_nombre_usuario()  # Asegurarse de que el nombre de usuario se pida al inicio
    #print(f"¡Hola, {nombre_usuario}! Puedes preguntarme algo, agregar una categoría/subcategoría o borrar conocimiento.")

    while True:
        pregunta = input("Tú: ")
        pregunta_limpia = eliminar_acentos(pregunta.lower())

        if pregunta_limpia in ["salir", "adios", "adiós"]:
            guardar_conocimientos()
            print("IA: ¡Adiós!")
            break
        elif pregunta_limpia == "agregar categoria":
            agregar_categoria()
        elif pregunta_limpia == "deseo borrar algo":
            borrar_conocimiento()
        else:
            # Primero, buscar si hay una respuesta relacionada con presidentes
            respuesta_presidente = buscar_por_claves(pregunta)

            if respuesta_presidente:
                print(f"IA: {respuesta_presidente}")
            else:
                # Si no se encuentra respuesta, utilizar la función preguntar
                respuesta = preguntar(pregunta)
                print(f"IA: {respuesta}")


# Ejecutar el programa
if __name__ == "__main__":
    main()
