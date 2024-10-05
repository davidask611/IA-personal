import json
from difflib import SequenceMatcher
from datetime import datetime
import random  # Para elegir una respuesta aleatoria dentro de una categoría

# Diccionario que almacenará conocimientos organizados por categorías
conocimientos = {}
nombre_usuario = ""
historial_conversacion = []  # Lista para almacenar el historial de conversación

# Umbral de similitud para respuesta automática
UMBRAL_SIMILITUD = 0.85  # Puedes ajustar este valor para más o menos precisión
MAX_HISTORIAL = 5  # Limitar el historial a las últimas 5 interacciones

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

# Función para calcular la similitud entre dos cadenas
def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

# Función para solicitar entrada del usuario
def preguntar():
    return input("Tú: ")

# Función para mostrar categorías disponibles
def mostrar_categorias():
    if conocimientos:
        print("IA: Categorías disponibles:")
        for idx, categoria in enumerate(conocimientos, 1):
            print(f"{idx}. {categoria}")
    else:
        print("IA: No hay categorías disponibles actualmente.")

# Función para eliminar todas las categorías
def limpiar_categorias():
    confirmacion = input("IA: ¿Estás seguro de que deseas eliminar todas las categorías? Esto borrará toda la memoria. (sí/no): ").lower()
    if confirmacion in ["sí", "si", "s"]:
        conocimientos.clear()  # Borra todo el diccionario de conocimientos
        guardar_conocimientos()
        return "IA: Todas las categorías han sido eliminadas, la memoria está vacía."
    else:
        return "IA: La memoria no ha sido modificada."

# Función para recordar el contexto de la conversación
def recordar_contexto():
    if historial_conversacion:
        print("IA: Recordando el contexto de la conversación...")
        for idx, item in enumerate(historial_conversacion[-MAX_HISTORIAL:], 1):
            print(f"{idx}. Tú dijiste: '{item['pregunta']}' -> IA respondió: '{item['respuesta']}'")

# Función para responder preguntas y gestionar las categorías
def responder(pregunta):
    # Recordar contexto al iniciar una nueva pregunta
    recordar_contexto()

    # Verificar si se pregunta por la hora o fecha actual
    if pregunta.lower() in ["¿que hora es?", "que hora es", "dime la hora","que hora es??","que hora es?"]:
        hora_actual = datetime.now().strftime("%H:%M")
        return f"La hora actual es {hora_actual}."
    elif pregunta.lower() in ["¿que fecha es hoy?", "que fecha es hoy??", "dime la fecha", "que fecha es hoy?", "que fecha es hoy",]:
        fecha_actual = datetime.now().strftime("%Y-%m-%d")
        return f"La fecha de hoy es {fecha_actual}."
    elif pregunta.lower() in ["¿que día es hoy?", "que día es hoy", "dime el dia", "que día es"]:
        dia_actual = datetime.now().strftime("%A")
        dia_actual_es = dias_semana.get(dia_actual, "día desconocido")
        return f"Hoy es {dia_actual_es}."

    # Si se desea borrar algo de la memoria
    if pregunta.lower() == "deseo borrar algo":
        nombre_ingresado = input("IA: Para confirmar, dime tu nombre: ")
        if nombre_ingresado.lower() == nombre_usuario.lower():
            tipo_borrado = input("IA: ¿Deseas borrar una categoría completa, una frase específica o limpiar todas las categorías? (categoría/frase/todas): ").lower()
            if tipo_borrado == "categoría":
                mostrar_categorias()
                categoria_a_borrar = input("IA: ¿Qué categoría deseas que olvide? ")
                if categoria_a_borrar.isdigit():
                    categoria_a_borrar = list(conocimientos.keys())[int(categoria_a_borrar) - 1]
                if categoria_a_borrar in conocimientos:
                    del conocimientos[categoria_a_borrar]
                    guardar_conocimientos()
                    return f"He olvidado todo lo que me enseñaste sobre la categoría: '{categoria_a_borrar}'"
                else:
                    return "No encuentro esa categoría en mi memoria."
            elif tipo_borrado == "frase":
                item_a_borrar = input("IA: ¿Qué frase deseas que olvide? ")
                for categoria in conocimientos:
                    if item_a_borrar in conocimientos[categoria]:
                        conocimientos[categoria].remove(item_a_borrar)
                        guardar_conocimientos()
                        return f"He olvidado la frase: '{item_a_borrar}' en la categoría '{categoria}'"
                return "No encuentro esa frase en mi memoria."
            elif tipo_borrado == "todas":
                return limpiar_categorias()
            else:
                return "No entendí tu elección."

    # Verificar si la pregunta es el nombre de una categoría y devolver una respuesta aleatoria
    if pregunta in conocimientos:
        respuestas_categoria = list(conocimientos[pregunta].values())  # Obtiene todas las respuestas dentro de la categoría
        if respuestas_categoria:
            return random.choice(respuestas_categoria)  # Devuelve una respuesta aleatoria
        else:
            return "IA: No tengo respuestas en esa categoría."

    # Intentar encontrar una respuesta similar en cualquier categoría con prioridad a respuestas conocidas
    for categoria, frases in conocimientos.items():
        for conocida, respuesta in frases.items():
            similitud = similar(pregunta, conocida)
            if similitud > UMBRAL_SIMILITUD:
                # Si la similitud es alta, responde automáticamente
                print(f"IA: Respondiendo automáticamente por similitud con '{conocida}' (similitud: {similitud:.2f})")
                historial_conversacion.append({"pregunta": pregunta, "respuesta": respuesta})  # Añadir al historial
                if len(historial_conversacion) > MAX_HISTORIAL:
                    historial_conversacion.pop(0)  # Limitar el historial
                return respuesta
            elif 0.7 < similitud <= UMBRAL_SIMILITUD:
                # Si la similitud es moderada, preguntar si son iguales
                confirmacion = input(f"IA: ¿La frase '{pregunta}' significa lo mismo que '{conocida}'? (sí/no): ").lower()
                if confirmacion in ["sí", "si", "s"]:
                    historial_conversacion.append({"pregunta": pregunta, "respuesta": respuesta})  # Añadir al historial
                    if len(historial_conversacion) > MAX_HISTORIAL:
                        historial_conversacion.pop(0)  # Limitar el historial
                    return respuesta

    # Si no se encuentra la pregunta, aprender una nueva
    nueva_respuesta = input("IA: No lo sé, ¿qué debería responder? ")

    # Mostrar categorías disponibles y permitir crear una nueva si es necesario
    mostrar_categorias()
    eleccion_categoria = input("IA: Elige una categoría o escribe 'nueva' para crear una nueva: ").lower()

    if eleccion_categoria == "nueva":
        nueva_categoria = input("IA: ¿Cómo se llamará la nueva categoría? ")
        conocimientos[nueva_categoria] = {}
        conocimientos[nueva_categoria][pregunta] = nueva_respuesta
    elif eleccion_categoria.isdigit():
        eleccion_categoria = list(conocimientos.keys())[int(eleccion_categoria) - 1]
        conocimientos[eleccion_categoria][pregunta] = nueva_respuesta
    elif eleccion_categoria in conocimientos:
        conocimientos[eleccion_categoria][pregunta] = nueva_respuesta
    else:
        return "Categoría no válida."

    guardar_conocimientos()
  # Guardar inmediatamente después de aprender algo nuevo

    # Añadir la nueva pregunta y respuesta al historial
    historial_conversacion.append({"pregunta": pregunta, "respuesta": nueva_respuesta})
    if len(historial_conversacion) > MAX_HISTORIAL:
        historial_conversacion.pop(0)  # Limitar el historial

    return "Gracias, he aprendido algo nuevo!"

# Función para guardar los conocimientos en un archivo JSON
def guardar_conocimientos():
    with open("conocimientos.json", "w") as archivo:
        json.dump(conocimientos, archivo, indent=4)
    print("IA: Conocimientos guardados exitosamente.")

# Intentar cargar los conocimientos desde el archivo JSON
try:
    with open("conocimientos.json", "r") as archivo:
        conocimientos = json.load(archivo)
except FileNotFoundError:
    conocimientos = {}

# Solicitar el nombre del usuario al inicio de la conversación
nombre_usuario = input("¡Hola! Soy tu IA. ¿Cuál es tu nombre? ")

print(f"¡Hola, {nombre_usuario}! Puedes preguntarme algo, pedirme la fecha/hora o decir 'deseo borrar algo' para eliminar conocimientos.")
while True:
    pregunta = preguntar()
    if pregunta.lower() in ["salir", "adiós"]:
        guardar_conocimientos()
        print("IA: ¡Adiós!")
        break
    respuesta = responder(pregunta)
    print("IA:", respuesta)
