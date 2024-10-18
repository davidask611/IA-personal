import json
from difflib import SequenceMatcher
from datetime import datetime
import unicodedata # Acento  normalizar
import random
import os # interactuar con archivos del SO
import re # Matematicas
import math # Matematicas

dias_semana = {
    "Monday": "lunes",
    "Tuesday": "martes",
    "Wednesday": "miércoles",
    "Thursday": "jueves",
    "Friday": "viernes",
    "Saturday": "sábado",
    "Sunday": "domingo"
}
# TODO Iniciar listas vacías
UMBRAL_SIMILITUD = 1
historial_preguntas = [] # Contexto/ultima pregunta/categoria
historial_conversacion = []
MAX_HISTORIAL = 10  # Limitar el historial a los últimos 10 mensajes

# TODO: Carga de datos
def cargar_datos_retroalimentacion():
    try:
        with open('retroalimentación.json', 'r', encoding='utf-8') as archivo:
            return json.load(archivo)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}  # Si el archivo no existe o está vacío, retornamos un diccionario vacío

def guardar_datos_retroalimentacion(retroalimentacion):
    with open('retroalimentación.json', 'w', encoding='utf-8') as archivo:
        json.dump(retroalimentacion, archivo, indent=4, ensure_ascii=False)


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

# Recuperar el historial desde el JSON si existe
if "historialConversacion" in conocimientos.get("contexto", {}):
    historial_conversacion = conocimientos["contexto"]["historialConversacion"]
else:
    historial_conversacion = []

# Asegurarse de que los signos están en el diccionario 'conocimientos'
signos_zodiacales = conocimientos.get("signos_zodiacales", {})


def eliminar_acentos(texto):
    texto = texto.replace('ñ', '~').replace('Ñ', '~')  # Reemplazar tanto minúscula como mayúscula
    texto_normalizado = unicodedata.normalize('NFD', texto)
    texto_sin_acentos = ''.join(c for c in texto_normalizado if unicodedata.category(c) != 'Mn')
    texto_final = texto_sin_acentos.replace('~', 'ñ')
    return texto_final


def guardar_datos(datos, nombre_archivo='conocimientos.json', mostrar_mensaje=False, verificar_existencia=True):
    if verificar_existencia and not os.path.exists(nombre_archivo):
        print(f"Advertencia: El archivo '{nombre_archivo}' no existe, se creará uno nuevo.")
    try:
        with open(nombre_archivo, 'w', encoding='utf-8') as archivo:
            json.dump(datos, archivo, ensure_ascii=False, indent=4)
        if mostrar_mensaje:
            print(f"Datos guardados exitosamente en '{nombre_archivo}'.")
    except IOError as e:
        print(f"Error al guardar los datos en el archivo '{nombre_archivo}': {e}")


# Guardar conocimientos en 'conocimientos.json' sin mostrar el mensaje
guardar_datos(conocimientos, 'conocimientos.json')

# Guardar datos de animales en 'animales.json' sin mostrar el mensaje
guardar_datos(animales_data, 'animales.json')


# Recordar el historial de la charla
def recordar_historial():
    if historial_conversacion:
        print("IA: Recordando el historial reciente...")
        for idx, item in enumerate(historial_conversacion[-MAX_HISTORIAL:], 1):
            print(f"{idx}. Tú dijiste: '{item['pregunta']}' -> IA respondió: '{item['respuesta']}'")
    else:
        print("IA: No hay historial de conversación disponible.")


def actualizar_historial(pregunta, respuesta, conocimientos, animales_data):
    historial_conversacion.append({"pregunta": pregunta, "respuesta": respuesta})

    if len(historial_conversacion) > MAX_HISTORIAL:
        historial_conversacion.pop(0)  # Eliminar el mensaje más antiguo

    if "historialConversacion" not in conocimientos["contexto"]:
        conocimientos["contexto"]["historialConversacion"] = []

    conocimientos["contexto"]["historialConversacion"].append({"pregunta": pregunta, "respuesta": respuesta})

    if len(conocimientos["contexto"]["historialConversacion"]) > MAX_HISTORIAL:
        conocimientos["contexto"]["historialConversacion"].pop(0)

    # Guardar en el archivo JSON
    guardar_datos(conocimientos, 'conocimientos.json')


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

# Función para obtener un chiste aleatorio
def obtener_chiste(conocimientos):
    try:
        lista_chistes = conocimientos["chiste"]["lista_chistes"]
        return random.choice(lista_chistes)
    except KeyError:
        return "Lo siento, no tengo chistes guardados."

# Función para verificar si se ha solicitado un chiste
def verificar_chiste(pregunta, conocimientos):
    # Convertir la pregunta a minúsculas y eliminar acentos
    pregunta_limpia = eliminar_acentos(pregunta.lower())

    # Lista de palabras clave para identificar que se trata de un chiste
    palabras_clave_chiste = ["chiste", "cuentame un chiste", "otro chiste", "me cuentas un chiste"]

    # Verificar si alguna de las palabras clave está en la pregunta
    if any(palabra in pregunta_limpia for palabra in palabras_clave_chiste):
        return obtener_chiste(conocimientos)

    return None  # Retornar None si no es una pregunta sobre chistes


# TODO verificar_musica_animal
def verificar_musica_animal(pregunta, conocimientos, animales):
    # Convertir la pregunta a minúsculas y eliminar acentos
    pregunta_limpia = eliminar_acentos(pregunta.lower())

    # Verificar si la pregunta es sobre animales
    if "perro" in pregunta_limpia or "gato" in pregunta_limpia or "felino" in pregunta_limpia or "ave" in pregunta_limpia or "pajaro" in pregunta_limpia or "animal" in pregunta_limpia:
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
    elif "musica" in pregunta_limpia or "cantante" in pregunta_limpia or "informacion" in pregunta_limpia or "canciones" in pregunta_limpia or "temas" in pregunta_limpia or "exitos" in pregunta_limpia or "premios" in pregunta_limpia or "influencias" in pregunta_limpia:
        # Procesar la pregunta como una consulta sobre música
        musica = conocimientos.get("musica", {})
        palabras_pregunta = pregunta_limpia.split()

        # Lista de palabras clave a buscar
        palabras_cantante = ["musica", "cantante", "informacion"]
        palabras_canciones = ["canciones", "temas", "exitos"]
        palabras_premios = ["premios", "grammy", "golden globe", "mtv"]
        palabras_influencias = ["influencias"]

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

                # Verificar si la pregunta menciona explícitamente el nombre del cantante
                if nombre_cantante_limpio in pregunta_limpia:
                    if any(palabra in palabras_pregunta for palabra in palabras_cantante):
                        respuesta = (f"{nombre_cantante}: {detalles['nombre_completo']} es un cantante de {genero}. "
                                     f"Nació el {detalles['fecha_nacimiento']} en {detalles['nacionalidad']}. {detalles['descripcion']}")
                        return respuesta

                    elif any(palabra in palabras_pregunta for palabra in palabras_canciones):
                        if detalles.get("canciones"):
                            canciones = ', '.join(detalles["canciones"])
                            return f"Las canciones más exitosas de {nombre_cantante} son: {canciones}."
                        else:
                            return f"No tengo información sobre las canciones de {nombre_cantante}."

                    elif any(palabra in palabras_pregunta for palabra in palabras_premios):
                        premios = detalles.get("premios", {})
                        premios_str = ', '.join([f"{key.capitalize()}: {value}" for key, value in premios.items()])
                        return f"{nombre_cantante} ha ganado los siguientes premios: {premios_str}."

                    elif any(palabra in palabras_pregunta for palabra in palabras_influencias):
                        influencias = ', '.join(detalles.get("influencias", []))
                        return f"{nombre_cantante} ha sido influenciado por: {influencias}."

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


# TODO Funcion matematica
def matematica(pregunta):
    # Reemplazar 'pi' por su valor aproximado (3.14)
    pregunta = pregunta.replace("pi", "3.14")

    # Reemplazar ^ por ** para potencias
    pregunta = pregunta.replace("^", "**")

    # Buscar y calcular todas las raíces cuadradas en la expresión
    def calcular_raiz_cuadrada(expresion):
        matches = re.findall(r'raiz cuadrada de (\d+)', expresion.lower())
        for match in matches:
            numero = int(match)
            raiz_cuadrada = round(math.sqrt(numero), 3)
            expresion = expresion.replace(f"raiz cuadrada de {match}", str(raiz_cuadrada))
        return expresion

    # Buscar y calcular todas las raíces cúbicas en la expresión
    def calcular_raiz_cubica(expresion):
        matches = re.findall(r'raiz cubica de (\d+)', expresion.lower())
        for match in matches:
            numero = int(match)
            raiz_cubica = round(math.pow(numero, 1/3), 3)
            expresion = expresion.replace(f"raiz cubica de {match}", str(raiz_cubica))
        return expresion

    # Buscar y calcular porcentajes en la expresión
    def calcular_porcentaje(expresion):
        # Buscar expresiones del tipo "20% de 50"
        matches = re.findall(r'(\d+)% de (\d+)', expresion.lower())
        for porcentaje, numero in matches:
            resultado = (int(porcentaje) / 100) * int(numero)
            expresion = expresion.replace(f"{porcentaje}% de {numero}", str(resultado))
        return expresion

    # Reemplazar log() por math.log(), esperando formato log(base, numero)
    def calcular_logaritmo(expresion):
        matches = re.findall(r'log\((\d+),\s*(\d+)\)', expresion)
        for base, numero in matches:
            logaritmo = round(math.log(int(numero), int(base)), 3)
            expresion = expresion.replace(f"log({base}, {numero})", str(logaritmo))
        return expresion

    # Buscar y reemplazar funciones trigonométricas por sus equivalentes en radianes
    def calcular_trigonometria(expresion):
        trig_functions = {"sin": math.sin, "cos": math.cos, "tan": math.tan}
        for func in trig_functions:
            matches = re.findall(rf'{func}\((\d+)\)', expresion)
            for match in matches:
                angulo_en_grados = int(match)
                angulo_en_radianes = math.radians(angulo_en_grados)  # Convertir a radianes
                resultado_trig = round(trig_functions[func](angulo_en_radianes), 3)
                expresion = expresion.replace(f"{func}({match})", str(resultado_trig))
        return expresion

    # Aplicar todas las funciones anteriores a la pregunta
    pregunta_limpia = calcular_raiz_cuadrada(pregunta.lower())
    pregunta_limpia = calcular_raiz_cubica(pregunta_limpia)
    pregunta_limpia = calcular_porcentaje(pregunta_limpia)  # Aquí calculamos porcentajes
    pregunta_limpia = calcular_logaritmo(pregunta_limpia)
    pregunta_limpia = calcular_trigonometria(pregunta_limpia)

    # Validar operaciones usando eval
    try:
        # Validar que solo contenga caracteres permitidos antes de usar eval
        if re.match(r'^[\d\.\+\-\*/\(\)%\^ ]+$', pregunta_limpia):
            resultado = eval(pregunta_limpia)

            # Formatear el resultado: sin decimales si es un número entero, o con tres decimales si tiene decimales.
            if isinstance(resultado, float) and resultado.is_integer():
                resultado = int(resultado)
            else:
                resultado = round(resultado, 3)

            return f"El resultado de {pregunta} es {resultado}."
        else:
            return "No pude entender la operación, intenta de nuevo con una operación simple."
    except (SyntaxError, ZeroDivisionError) as e:
        return f"Error en la operación: {e}. Por favor, revisa la sintaxis."

# TODO Funcion retroalimentacion opinion
# Función para recibir y guardar la retroalimentación
"""def guardar_retroalimentacion():
    # Solicitar el nombre de usuario (obligatorio)
    usuario = input("Por favor, ingresa tu nombre de usuario: ").strip()
    if not usuario:
        print("El nombre de usuario es obligatorio. Intenta de nuevo.")
        return

    # Solicitar la edad (opcional)
    edad = input("Ingresa tu edad (opcional, presiona Enter para omitir): ").strip()
    if edad and not edad.isdigit():
        print("Por favor, ingresa una edad válida o deja el campo vacío.")
        return

    # Solicitar la sugerencia u opinión
    opinion = input("Escribe tu opinión o sugerencia (máximo 100 caracteres): ").strip()
    if len(opinion) > 100:
        print("Tu opinión excede los 100 caracteres. Por favor, sé breve.")
        return

    # Crear la estructura de la opinión
    detalles = {
        "edad": edad if edad else "No especificada",
        "sugerencia": opinion
    }

    # Intentar cargar el archivo JSON existente o crear uno nuevo si no existe
    try:
        with open('retroalimentación.json', 'r', encoding='utf-8') as archivo:
            datos = json.load(archivo)
    except (FileNotFoundError, json.JSONDecodeError):
        datos = {}  # Si no existe o está vacío, se inicia un diccionario vacío

    # Agregar la nueva retroalimentación bajo la clave del usuario
    datos[usuario] = detalles

    # Guardar los datos actualizados en el archivo
    with open('retroalimentación.json', 'w', encoding='utf-8') as archivo:
        json.dump(datos, archivo, indent=4, ensure_ascii=False)

    print("Gracias por tu opinión. ¡Ha sido guardada!")
"""

# Luego puedes definir la lógica en una función separada para manejar la recolección.
def manejar_recoleccion_opinion(pregunta, conocimientos, retroalimentacion):
    # Si el nombre del usuario no está aún registrado
    if not conocimientos["contexto"]["nombre_usuario"]:
        conocimientos["contexto"]["nombre_usuario"] = pregunta.strip()
        guardar_datos(conocimientos, 'conocimientos.json')
        return f"Encantado de conocerte, {conocimientos['contexto']['nombre_usuario']}! ¿Cuántos años tienes?"

    # Si la edad del usuario no está registrada aún
    if not conocimientos["contexto"]["edad_usuario"]:
        conocimientos["contexto"]["edad_usuario"] = pregunta.strip()
        guardar_datos(conocimientos, 'conocimientos.json')
        return "Perfecto, ahora dime tu opinión o sugerencia (máximo 100 caracteres)."

    # Verificar si la opinión es válida y no contiene palabras clave que activen otras funciones
    opinion = pregunta.strip()
    if 0 < len(opinion) <= 100 and not any(kw in opinion.lower() for kw in ["presidente", "saludo", "matemática", "agregar", "borrar"]):
        retroalimentacion["opiniones"] = retroalimentacion.get("opiniones", [])
        nueva_opinion = {
            "nombre": conocimientos["contexto"]["nombre_usuario"],
            "edad": conocimientos["contexto"]["edad_usuario"],
            "opinion": opinion
        }
        retroalimentacion["opiniones"].append(nueva_opinion)
        guardar_datos_retroalimentacion(retroalimentacion)

        # Restablecer el contexto para futuras opiniones
        conocimientos["contexto"]["recolectando_opinion"] = False
        conocimientos["contexto"]["nombre_usuario"] = ""
        conocimientos["contexto"]["edad_usuario"] = ""
        guardar_datos(conocimientos, 'conocimientos.json')

        return "¡Gracias por tu opinión/sugerencia! La he guardado con tus datos."
    else:
        return "Por favor, tu opinión o sugerencia debe tener entre 1 y 100 caracteres y no contener palabras clave especiales."



# TODO Agregar clave/subclave
# Controlar respuestas de sí/no
def obtener_respuesta_si_no(mensaje):
    respuesta = input(f"{mensaje} (si/no): ").lower()
    while respuesta not in ["si", "no"]:
        respuesta = input(f"Respuesta inválida. {mensaje} (si/no): ").lower()
    return respuesta == "si"

# Función para agregar detalles opcionales al conocimiento
def agregar_detalles(diccionario):
    print("Ahora puedes agregar o actualizar los detalles.")
    for detalle, valor in diccionario.items():
        print(f"{detalle}: {valor}")

    while True:
        print("\n¿Qué deseas hacer?")
        print("1. Agregar o modificar un detalle.")
        print("2. Agregar una nueva subclave.")
        print("3. Agregar una lista (array).")
        print("4. Salir.")
        eleccion = input("Selecciona una opción (1, 2, 3, 4): ")

        if eleccion == "4":
            print("Saliendo de la edición de detalles.")
            break

        nueva_clave = input("Introduce el nombre del detalle o subclave: ")

        # Opción 1: Agregar o modificar un detalle.
        if eleccion == "1":
            if nueva_clave in diccionario:
                reemplazar = obtener_respuesta_si_no(f"El detalle '{nueva_clave}' ya existe con el valor '{diccionario[nueva_clave]}'. ¿Deseas reemplazarlo?")
                if reemplazar:
                    nuevo_valor = input(f"Introduce el nuevo valor para '{nueva_clave}': ")
                    diccionario[nueva_clave] = nuevo_valor
            else:
                nuevo_valor = input(f"Introduce el valor para '{nueva_clave}': ")
                diccionario[nueva_clave] = nuevo_valor
            print(f"Detalle '{nueva_clave}' actualizado.")

        # Opción 2: Agregar una nueva subclave.
        elif eleccion == "2":
            if nueva_clave not in diccionario:
                diccionario[nueva_clave] = {}
                print(f"Subclave '{nueva_clave}' creada.")
                agregar_detalles(diccionario[nueva_clave])
            else:
                print(f"La subclave '{nueva_clave}' ya existe. No se puede volver a crear.")

        # Opción 3: Agregar una lista (array).
        elif eleccion == "3":
            lista = []
            print(f"Vamos a crear una lista de valores para '{nueva_clave}'.")
            while True:
                valor = input(f"Introduce un valor para '{nueva_clave}' o 'salir' para terminar: ")
                if valor.lower() == 'salir':
                    break
                lista.append(valor)
            diccionario[nueva_clave] = lista
            print(f"Lista '{nueva_clave}' actualizada con {len(lista)} valores.")

        else:
            print("Opción inválida, por favor selecciona 1, 2, 3 o 4.")

    print("Detalles actualizados.")


# TODO Función para agregar clave/subclave/pregunta-respuesta
def agregar_clave(conocimientos, animales_data):
    print("Claves disponibles en conocimientos:")
    for idx, clave in enumerate(conocimientos.keys()):
        print(f"{idx + 1}. {clave}")

    print("Claves disponibles en animales:")
    for idx, clave in enumerate(animales_data.keys()):
        print(f"{idx + 1 + len(conocimientos)}. {clave}")

    # Agregar opción para nueva clave al final de la lista
    print(f"{len(conocimientos) + len(animales_data) + 1}. Agregar nueva clave")

    eleccion = input("Selecciona una clave (número) o escribe una nueva: ")

    # Opción para agregar una nueva clave
    if eleccion.isdigit() and int(eleccion) == len(conocimientos) + len(animales_data) + 1:
        nueva_clave = input("Introduce el nombre de la nueva clave: ")
        tipo_clave = input("¿Esta clave es de tipo 'texto' (S/N)? ").lower()

        if nueva_clave not in conocimientos and nueva_clave not in animales_data:
            if tipo_clave == 's':
                conocimientos[nueva_clave] = {}
                print(f"Nueva clave de texto '{nueva_clave}' agregada a conocimientos.")
            else:
                conocimientos[nueva_clave] = {}
                print(f"Nueva clave con subclaves '{nueva_clave}' agregada a conocimientos.")

            # Preguntar si desea agregar detalles
            if obtener_respuesta_si_no("¿Deseas agregar detalles para esta clave?"):
                agregar_detalles(conocimientos[nueva_clave])

    # Lógica para seleccionar una clave de conocimientos
    elif eleccion.isdigit() and 1 <= int(eleccion) <= len(conocimientos):
        clave_seleccionada = list(conocimientos.keys())[int(eleccion) - 1]
        print(f"Has seleccionado la clave de conocimientos: {clave_seleccionada}")

        # Ofrecer opciones para crear subclave o agregar pregunta y respuesta
        print("¿Qué deseas hacer con esta clave?")
        print("1. Agregar pregunta y respuesta.")
        print("2. Crear una nueva subclave.")
        eleccion_tipo = input("Selecciona una opción (1 o 2): ")

        if eleccion_tipo == "1":
            pregunta_usuario = input("Indica la pregunta: ")
            respuesta_ia = input("Indica la respuesta: ")
            conocimientos[clave_seleccionada][pregunta_usuario] = respuesta_ia
            print(f"Pregunta y respuesta agregadas a la clave '{clave_seleccionada}'.")
        elif eleccion_tipo == "2":
            subclave = input("Introduce el nombre de la nueva subclave: ")
            conocimientos[clave_seleccionada][subclave] = {}
            print(f"Nueva subclave '{subclave}' agregada a '{clave_seleccionada}'.")
            agregar_detalles(conocimientos[clave_seleccionada][subclave])

    # Lógica para seleccionar una clave de animales (similar a conocimientos)
    elif eleccion.isdigit() and len(conocimientos) < int(eleccion) <= len(conocimientos) + len(animales_data):
        clave_seleccionada = list(animales_data.keys())[int(eleccion) - len(conocimientos) - 1]
        print(f"Has seleccionado la clave de animales: {clave_seleccionada}")

        print("¿Qué deseas hacer con esta clave?")
        print("1. Agregar pregunta y respuesta.")
        print("2. Crear una nueva subclave.")
        eleccion_tipo = input("Selecciona una opción (1 o 2): ")

        if eleccion_tipo == "1":
            pregunta_usuario = input("Indica la pregunta: ")
            respuesta_ia = input("Indica la respuesta: ")
            animales_data[clave_seleccionada][pregunta_usuario] = respuesta_ia
            print(f"Pregunta y respuesta agregadas a la clave '{clave_seleccionada}'.")
        elif eleccion_tipo == "2":
            subclave = input("Introduce el nombre de la nueva subclave: ")
            animales_data[clave_seleccionada][subclave] = {}
            print(f"Nueva subclave '{subclave}' agregada a '{clave_seleccionada}'.")
            agregar_detalles(animales_data[clave_seleccionada][subclave])

    else:
        print("Selección inválida. Por favor intenta de nuevo.")

    # Guardar los datos después de cualquier cambio
    guardar_datos(conocimientos, 'conocimientos.json', mostrar_mensaje=True)  # Esto mostrará el mensaje.
    guardar_datos(animales_data, 'animales.json', mostrar_mensaje=True) # Esto mostrará el mensaje.


# Función para borrar clave/subclave/subclave
def borrar_clave(conocimientos, animales_data):
    # Función para mostrar y borrar claves y subclaves de ambos JSON
    def mostrar_y_borrar_combinado(conocimientos, animales_data):
        claves_conocimientos = list(conocimientos.keys())
        claves_animales = list(animales_data.keys())
        claves_combinadas = [(clave, 'conocimientos') for clave in claves_conocimientos] + \
                            [(clave, 'animales_data') for clave in claves_animales]

        if not claves_combinadas:
            print("No hay claves disponibles para borrar en ninguno de los archivos.")
            return False

        # Mostrar la lista combinada de claves
        print("\nSelecciona una clave para borrar (de ambos archivos):")
        for i, (clave, origen) in enumerate(claves_combinadas, 1):
            print(f"{i}. {clave} ({origen})")

        seleccion = input("Ingresa el número de la clave que deseas borrar: ")
        try:
            seleccion = int(seleccion)
            if seleccion < 1 or seleccion > len(claves_combinadas):
                print("Selección no válida. Debes elegir un número en la lista.")
                return False
        except ValueError:
            print("Entrada no válida. Debes ingresar un número.")
            return False

        # Obtener la clave y su origen (conocimientos o animales_data)
        clave_a_borrar, origen = claves_combinadas[seleccion - 1]
        diccionario = conocimientos if origen == 'conocimientos' else animales_data

        # Verificar si la clave tiene subclaves
        if isinstance(diccionario[clave_a_borrar], dict):
            subclaves = list(diccionario[clave_a_borrar].keys())
            if subclaves:
                while True:
                    print(f"\nSubclaves disponibles en '{clave_a_borrar}':")
                    for j, subclave in enumerate(subclaves, 1):
                        print(f"{j}. {subclave}")

                    seleccion_subclave = input("¿Quieres borrar una subclave, detalle o elemento de lista? (s/n): ")
                    if seleccion_subclave.lower() != 's':
                        break

                    sub_seleccion = input("Ingresa el número de la subclave que deseas borrar o modificar: ")
                    try:
                        sub_seleccion = int(sub_seleccion)
                        if sub_seleccion < 1 or sub_seleccion > len(subclaves):
                            print("Selección no válida. Debes elegir un número en la lista.")
                            continue
                    except ValueError:
                        print("Entrada no válida. Debes ingresar un número.")
                        continue

                    subclave_a_borrar = subclaves[sub_seleccion - 1]

                    # Confirmar antes de borrar una subclave completa
                    confirmacion = input(f"¿Estás seguro de que deseas borrar la subclave '{subclave_a_borrar}'? (s/n): ")
                    if confirmacion.lower() == 's':
                        del diccionario[clave_a_borrar][subclave_a_borrar]
                        print(f"Subclave '{subclave_a_borrar}' borrada de '{clave_a_borrar}' en '{origen}'.")

                        # Guardar inmediatamente después de la eliminación
                        if origen == 'conocimientos':
                            guardar_datos(conocimientos, 'conocimientos.json')
                        else:
                            guardar_datos(animales_data, 'animales.json')

                        subclaves = list(diccionario[clave_a_borrar].keys())  # Actualizar lista de subclaves
                        if not subclaves:
                            print(f"No quedan más subclaves en '{clave_a_borrar}'.")
                            break
                    else:
                        print("Operación cancelada.")
                        return False
            else:
                print(f"La clave '{clave_a_borrar}' no tiene subclaves.")
        else:
            # Confirmar antes de borrar la clave completa
            confirmacion = input(f"¿Estás seguro de que deseas borrar la clave '{clave_a_borrar}' completa? (s/n): ")
            if confirmacion.lower() == 's':
                del diccionario[clave_a_borrar]
                print(f"Clave '{clave_a_borrar}' borrada en '{origen}'.")

                # Guardar inmediatamente después de la eliminación
                if origen == 'conocimientos':
                    guardar_datos(conocimientos, 'conocimientos.json')
                else:
                    guardar_datos(animales_data, 'animales.json')
                return True
            else:
                print("Operación cancelada.")
                return False

    return mostrar_y_borrar_combinado(conocimientos, animales_data)



# TODO: Función principal de preguntar (lógica de preguntas)
def preguntar(pregunta, conocimientos, animales_data, retroalimentacion):
    pregunta_limpia = eliminar_acentos(pregunta.lower())

    # Verificar si "contexto" está en "conocimientos" y asegurarse de que las claves necesarias estén presentes
    if "contexto" not in conocimientos:
        conocimientos["contexto"] = {
            "ultimaPregunta": "",
            "recolectando_opinion": False,
            "nombre_usuario": "",
            "edad_usuario": ""
        }
    else:
        # Asegurar que las claves necesarias estén en el contexto
        conocimientos["contexto"].setdefault("recolectando_opinion", False)
        conocimientos["contexto"].setdefault("nombre_usuario", "")
        conocimientos["contexto"].setdefault("edad_usuario", "")

    # Si está recolectando una opinión, manejarlo directamente sin analizar otras palabras clave.
    if conocimientos["contexto"]["recolectando_opinion"]:
        return manejar_recoleccion_opinion(pregunta, conocimientos, retroalimentacion)

    # Verificar si el usuario quiere dejar una opinión o sugerencia y no está ya en proceso de recolección
    if not conocimientos["contexto"]["recolectando_opinion"] and (
        pregunta_limpia.startswith("te dejo una opinion") or pregunta_limpia.startswith("te dejo una sugerencia")
    ):
        conocimientos["contexto"]["recolectando_opinion"] = True
        guardar_datos(conocimientos, 'conocimientos.json')
        return "¡Gracias por querer compartir! ¿Cuál es tu nombre?"

    # (El resto de la lógica de la función 'preguntar' sigue aquí)

    # Verificar si es un saludo
    respuesta_saludo = buscar_saludo(pregunta_limpia, conocimientos)
    if respuesta_saludo:
        actualizar_historial(pregunta, respuesta_saludo)
        conocimientos["contexto"]["ultimaPregunta"] = pregunta_limpia
        guardar_datos(conocimientos, 'conocimientos.json')
        return respuesta_saludo

    # Verificar si se pregunta por el presidente
    respuesta_presidente = presidente(pregunta_limpia, conocimientos)
    if respuesta_presidente != "Lo siento, no tengo información sobre ese presidente.":
        conocimientos["contexto"]["ultimaPregunta"] = pregunta_limpia
        guardar_datos(conocimientos, 'conocimientos.json')
        return respuesta_presidente

    # Verificar si se pregunta por signos zodiacales
    respuesta_signo = detectar_signo(pregunta_limpia)
    if respuesta_signo:
        conocimientos["contexto"]["ultimaPregunta"] = pregunta_limpia
        guardar_datos(conocimientos, 'conocimientos.json')
        return respuesta_signo

    # Verificar si la pregunta es sobre música o animales usando la nueva función
    respuesta_musica_animal = verificar_musica_animal(pregunta, conocimientos, animales_data)
    if respuesta_musica_animal != "No tengo suficiente información para responder esta pregunta.":
        conocimientos["contexto"]["ultimaPregunta"] = pregunta_limpia
        guardar_datos(conocimientos, 'conocimientos.json')
        return respuesta_musica_animal

    # Verificar si la pregunta es sobre chistes
    respuesta_chiste = verificar_chiste(pregunta, conocimientos)
    if respuesta_chiste:
        conocimientos["contexto"]["ultimaPregunta"] = pregunta_limpia
        guardar_datos(conocimientos, 'conocimientos.json')
        return respuesta_chiste

    # Verificar si el usuario desea agregar una clave o subclave
    if "agregar" in pregunta_limpia and "clave" in pregunta_limpia:
        exito = agregar_clave(conocimientos)
        if exito:
            guardar_datos(conocimientos, 'conocimientos.json')
            return "La clave o subclave ha sido agregada exitosamente."
        else:
            return "Hubo un problema al agregar la clave o subclave. Por favor, inténtalo de nuevo."

    # Verificar si el usuario desea borrar una clave o subclave
    if "borrar" in pregunta_limpia and "clave" in pregunta_limpia:
        exito = borrar_clave(conocimientos, animales_data)
        if exito:
            guardar_datos(conocimientos, 'conocimientos.json', mostrar_mensaje=True)
            guardar_datos(animales_data, 'animales.json', mostrar_mensaje=True)
            return "La clave o subclave ha sido eliminada exitosamente."
        else:
            return "Hubo un problema al eliminar la clave o subclave. Por favor, inténtalo de nuevo."

    # Verificar si la pregunta es una operación matemática
    respuesta_matematica = matematica(pregunta)
    if respuesta_matematica and "No pude entender la operación" not in respuesta_matematica:
        conocimientos["contexto"]["ultimaPregunta"] = pregunta_limpia
        guardar_datos(conocimientos, 'conocimientos.json')
        return respuesta_matematica

    # Respuesta predeterminada si no se encuentra una coincidencia
    return "No tengo suficiente información para responder... intenta reformular o usar otros términos."



def main():
    conocimientos = cargar_datos('conocimientos.json')  # Cargar conocimientos
    animales_data = cargar_animales('animales.json')  # Cargar datos de animales
    retroalimentacion = cargar_datos_retroalimentacion()  # Cargar retroalimentación

    while True:
        pregunta = input("Tú: ")
        pregunta_limpia = eliminar_acentos(pregunta.lower())

        if pregunta_limpia in ["salir", "adios", "adiós"]:
            # Guardar los conocimientos y animales
            guardar_datos(conocimientos, 'conocimientos.json')
            guardar_datos(animales_data, 'animales.json')
            guardar_datos_retroalimentacion(retroalimentacion)  # Guardar retroalimentación
            print("IA: ¡Adiós!")
            break

        # Opción para borrar clave
        if pregunta_limpia == "borrar clave":
            exito_borrado = borrar_clave(conocimientos, animales_data)
            if exito_borrado:
                guardar_datos(conocimientos, 'conocimientos.json')
                guardar_datos(animales_data, 'animales.json')
                print("IA: La clave o subclave ha sido eliminada exitosamente.")
            continue

        # Opción para agregar clave
        if pregunta_limpia == "agregar clave":
            exito_agregar = agregar_clave(conocimientos, animales_data)
            if exito_agregar:
                guardar_datos(conocimientos, 'conocimientos.json')
                guardar_datos(animales_data, 'animales.json')
                print("IA: La clave o subclave ha sido agregada exitosamente.")
            continue

        # Aquí buscamos si la pregunta es sobre la IA
        respuesta_sobre_ia = responder_sobre_ia(pregunta_limpia, conocimientos)
        if respuesta_sobre_ia:
            print(f"IA: {respuesta_sobre_ia}")
            # Actualizar el historial de conversación
            actualizar_historial(pregunta, respuesta_sobre_ia, conocimientos, animales_data)
            continue

        # Aquí buscamos si la pregunta está en charla cotidiana
        respuesta_charla = manejar_charla(pregunta_limpia, conocimientos)
        if respuesta_charla:
            print(f"IA: {respuesta_charla}")
            # Actualizar el historial de conversación
            actualizar_historial(pregunta, respuesta_charla, conocimientos, animales_data)
            continue

        # Aquí se revisa si hay un saludo
        respuesta_saludo = buscar_saludo(pregunta_limpia, conocimientos)
        if respuesta_saludo:
            print(f"IA: {respuesta_saludo}")
            # Actualizar el historial de conversación
            actualizar_historial(pregunta, respuesta_saludo, conocimientos, animales_data)
            continue

        # Verificar si es una pregunta sobre chistes
        respuesta_chiste = verificar_chiste(pregunta_limpia, conocimientos)
        if respuesta_chiste:
            print(f"IA: {respuesta_chiste}")
            # Actualizar el historial de conversación
            actualizar_historial(pregunta, respuesta_chiste, conocimientos, animales_data)
            continue

        # Llamar a la función preguntar para manejar todas las preguntas
        respuesta = preguntar(pregunta, conocimientos, animales_data, retroalimentacion)
        print(f"IA: {respuesta}")
        # Actualizar el historial de conversación
        actualizar_historial(pregunta, respuesta, conocimientos, animales_data)



# TODO Ejecutar el programa
if __name__ == "__main__":
    main()
