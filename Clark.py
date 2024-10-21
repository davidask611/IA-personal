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
# Función para cargar sinónimos desde un archivo JSON
def cargar_sinonimos():
    try:
        with open('sinonimos.json', 'r', encoding='utf-8') as archivo:
            sinonimos = json.load(archivo)
        #print(f"Sinónimos cargados: {sinonimos}")  # Verificar si los sinónimos se están cargando
        return sinonimos
    except (FileNotFoundError, json.JSONDecodeError):
        print("Error al cargar el archivo de sinónimos.")  # Mensaje en caso de error
        return {}


# Cargar los sinónimos al inicio del programa
sinonimos = cargar_sinonimos()

def reemplazar_palabras(opinion):
    palabras = opinion.split()
    palabras_reemplazadas = []

    for palabra in palabras:
        # Verificar si la palabra tiene un sinónimo, usando minúsculas
        palabra_reemplazada = sinonimos.get(palabra.lower(), palabra)

        # Depuración para ver qué palabras se están reemplazando
        #print(f"Palabra original: {palabra}, Reemplazada por: {palabra_reemplazada}")

        # Si la palabra original tenía mayúscula inicial, conservamos la capitalización
        if palabra.istitle():
            palabra_reemplazada = palabra_reemplazada.capitalize()

        palabras_reemplazadas.append(palabra_reemplazada)

    return " ".join(palabras_reemplazadas)


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
        nombre = input("¡Hola! Me llamo Clark. ¿Cuál es tu nombre? (No puedes dejarlo en blanco): ")
        if not nombre.strip():
            print("Por favor, ingresa un nombre válido.")
    return nombre

nombre_usuario = solicitar_nombre_usuario()
print(f"¡Un placer, {nombre_usuario}! Puedes preguntarme algo o dejarme una idea diciendo 'te dejo una opinion'o'te dejo una sugerencia'.")


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

# TODO: Función retroalimentación opinión
def manejar_recoleccion_opinion(pregunta, conocimientos, retroalimentacion):
    # Limpiar la opinión y asegurar que no esté vacía
    opinion = pregunta.strip()

    # Reemplazar palabras clave en la opinión
    opinion_reemplazada = reemplazar_palabras(opinion)

    # Depuración: Verificar el reemplazo de sinónimos
    #print(f"Opinión original: {opinion}")
    #print(f"Opinión con sinónimos: {opinion_reemplazada}")

    # Si el nombre del usuario no está registrado
    if not conocimientos["contexto"]["nombre_usuario"]:
        conocimientos["contexto"]["nombre_usuario"] = opinion_reemplazada
        guardar_datos(conocimientos, 'conocimientos.json')
        return f"Encantado de conocerte, {conocimientos['contexto']['nombre_usuario']}! ¿Cuántos años tienes?"

    # Si la edad del usuario no está registrada aún
    if not conocimientos["contexto"]["edad_usuario"]:
        if opinion.isdigit() and 0 < int(opinion) <= 120:  # Validar edad
            conocimientos["contexto"]["edad_usuario"] = opinion
            guardar_datos(conocimientos, 'conocimientos.json')
            return "Perfecto, ahora dime tu opinión o sugerencia (máximo 100 caracteres)."
        else:
            return "Por favor, ingresa una edad válida."

    # Verificar si la opinión es válida
    if 0 < len(opinion_reemplazada) <= 100 and not any(kw in opinion_reemplazada.lower() for kw in ["presidente", "saludo", "matemática", "agregar", "borrar"]):
        retroalimentacion["opiniones"] = retroalimentacion.get("opiniones", [])
        nueva_opinion = {
            "nombre": conocimientos["contexto"]["nombre_usuario"],
            "edad": conocimientos["contexto"]["edad_usuario"],
            "opinion": opinion_reemplazada  # Guardar la opinión con sinónimos
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

# Funcion para recetas
def comida(consulta, conocimientos, eleccion_automatica=None):
    # Detectar palabras clave para mostrar la lista de recetas
    if "recetas" in consulta.lower() or "receta" in consulta.lower():
        recetas = list(conocimientos["recetario"].keys())
        if recetas:
            # Preparar la respuesta con la lista de recetas
            respuesta = "Recetas disponibles:\n"
            respuesta += "\n".join([f"{idx}. {receta}" for idx, receta in enumerate(recetas, start=1)])
            respuesta += "\nElige el número de la receta que quieres ver:"

            # Solo mostrar la lista de recetas cuando no es automático
            if eleccion_automatica is None:
                print(respuesta)

            # Modo automático: se usa si eleccion_automatica tiene un valor
            if eleccion_automatica is not None:
                eleccion = eleccion_automatica
            else:
                # Modo manual: pedir al usuario que ingrese un número
                try:
                    eleccion = int(input())
                except ValueError:
                    return "Por favor, ingresa un número válido."

            # Validar la elección y mostrar la receta
            if isinstance(eleccion, int) and 1 <= eleccion <= len(recetas):
                nombre_comida = recetas[eleccion - 1]
                receta = conocimientos["recetario"][nombre_comida]
                detalles = f"\nReceta de {nombre_comida}:\n"
                detalles += f"Ingredientes: {', '.join(receta['ingredientes'])}\n"
                detalles += f"Paso a paso: {' -> '.join(receta['paso_a_paso'])}"
                return detalles
            else:
                return "Número fuera de rango. Inténtalo nuevamente."
        else:
            return "No hay recetas disponibles en el recetario."
    else:
        return "No entendí tu solicitud. Si quieres ver las recetas, usa una consulta que incluya 'receta' o 'recetas'."

# Función para obtener información detallada de una opción seleccionada
def obtener_detalle_planta(tipo, seleccion, conocimientos):
    seleccion = seleccion.lower()

    if tipo == 'suculentas':
        suculentas = conocimientos.get('planta', {}).get('suculentas', {})
        for clave, info in suculentas.items():
            if seleccion == info['nombre'].lower():
                return (f"{info['nombre']}:\n"
                        f"{info.get('descripcion', 'Descripción no disponible')}.\n"
                        f"Se debe regar cada {info.get('riego', 'frecuencia de riego no especificada')}.")
        return "Lo siento, no tengo información sobre esa suculenta. Intenta reformular la pregunta."

    elif tipo == 'arboles':
        arboles = conocimientos.get('planta', {}).get('arboles', {})
        for clave, info in arboles.items():
            if seleccion == info['nombre'].lower():
                return (f"{info['nombre']}:\n"
                        f"Fruta: {info.get('fruta', 'No especificada')}.\n"
                        f"Epoca: {info.get('epoca', 'No especificada')}.\n"  # Se mantiene la epoca aquí
                        f"Altura máxima: {info.get('altura', 'Altura no especificada')} metros.")
        return "Lo siento, no tengo información sobre ese árbol frutal. Intenta reformular la pregunta."

    elif tipo == 'huerta':
        huerta = conocimientos.get('planta', {}).get('huerta', {})
        for clave, info in huerta.items():
            if seleccion == info['nombre'].lower():
                return (f"{info['nombre']}:\n"
                        f"Descripción: {info.get('descripcion', 'Descripción no disponible')}.\n"
                        f"Epoca: {info.get('epoca', 'epoca no disponible')}.\n"  # Se mantiene la epoca aquí
                        f"Se debe regar cada {info.get('riego', 'frecuencia de riego no especificada')}.")
        return "Lo siento, no tengo información sobre esa verdura. Intenta reformular la pregunta."

    return "No se encontró información sobre la selección."


# Función para manejar las preguntas sobre plantas, ahora interactiva y automatizada
def manejar_planta(pregunta, conocimientos, seleccion_automatica=None):
    palabras_clave = ['suculenta', 'suculentas','arbol', 'arboles', 'arbustos', 'frutas', 'verdura', 'verduras', 'huerta', 'plantas']

    # Normalizar la pregunta para evitar problemas con acentos
    pregunta_normalizada = eliminar_acentos(pregunta.lower())

    # Detectamos si alguna palabra clave está en la pregunta normalizada
    if any(palabra in pregunta_normalizada for palabra in palabras_clave):
        # Preguntas sobre suculentas
        if 'suculenta' in pregunta.lower() or 'suculentas' in pregunta.lower():
            suculentas = conocimientos.get('planta', {}).get('suculentas', {})
            if suculentas:
                respuesta = "Las suculentas que conozco son:\n"
                lista_suculentas = [f"{idx + 1}. {info['nombre']}" for idx, info in enumerate(suculentas.values())]
                respuesta += "\n".join(lista_suculentas)

                # Si hay selección automática, usamos esa selección para obtener detalles
                if seleccion_automatica:
                    return obtener_detalle_planta('suculentas', seleccion_automatica, conocimientos), 'suculentas'

                # En modo manual, devolvemos la lista para que el usuario elija
                return respuesta, 'suculentas'

        # Preguntas sobre árboles
        elif 'arbol' in pregunta.lower() or 'arboles' in pregunta.lower() or 'arbustos' in pregunta.lower() or 'frutas' in pregunta.lower():
            arboles = conocimientos.get('planta', {}).get('arboles', {})
            if arboles:
                respuesta = "Los árboles frutales que conozco son:\n"
                lista_arboles = [f"{idx + 1}. {info['nombre']}" for idx, info in enumerate(arboles.values())]
                respuesta += "\n".join(lista_arboles)

                if seleccion_automatica:
                    return obtener_detalle_planta('arboles', seleccion_automatica, conocimientos), 'arboles'

                return respuesta, 'arboles'

        # Preguntas sobre verduras o huerta
        elif 'verdura' in pregunta.lower() or 'huerta' in pregunta.lower() or 'plantas' in pregunta.lower() or 'verduras' in pregunta.lower():
            huerta = conocimientos.get('planta', {}).get('huerta', {})
            if huerta:
                respuesta = "Las verduras que conozco son:\n"
                lista_huerta = [f"{idx + 1}. {info['nombre']}" for idx, info in enumerate(huerta.values())]
                respuesta += "\n".join(lista_huerta)

                if seleccion_automatica:
                    return obtener_detalle_planta('huerta', seleccion_automatica, conocimientos), 'huerta'

                return respuesta, 'huerta'

        return "Lo siento, no entendí tu pregunta. Prueba preguntando sobre suculentas, árboles o verduras.", None

    return "No detecté ninguna palabra clave relacionada con plantas. Por favor, pregunta sobre suculentas, árboles o verduras.", None



# TODO Autoanalisis
# Cargar datos de retroalimentación al inicio
retroalimentacion = cargar_datos_retroalimentacion()

# Asegúrate de que la función 'cargar_datos_retroalimentacion' esté definida correctamente:
def cargar_datos_retroalimentacion():
    try:
        with open('retroalimentación.json', 'r', encoding='utf-8') as archivo:
            return json.load(archivo)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}  # Retorna un diccionario vacío si el archivo no existe o está vacío

# Función para verificar si el usuario es un administrador
def verificar_administrador(nombre, contrasena):
    ADMIN_NOMBRE = "davidask"  # Nombre de usuario del administrador
    ADMIN_CONTRASENA = "611"  # Contraseña del administrador
    return nombre == ADMIN_NOMBRE and contrasena == ADMIN_CONTRASENA

# Función de auto-análisis con ejemplos específicos
def auto_analisis(nombre, contrasena, conocimientos, animales_data, retroalimentacion):
    if not verificar_administrador(nombre, contrasena):
        return "Acceso denegado. Solo un administrador puede iniciar el auto-análisis."

    print("IA: Iniciando auto-análisis...")

    # Lista de pruebas simples con descripciones y funciones de prueba
    pruebas_simples = [
        # Pruebas de saludos
        {"descripcion": "Prueba de saludo - 'buenas'", "funcion": lambda: buscar_saludo("buenas", conocimientos), "esperado": "buenas como estas??"},
        {"descripcion": "Prueba de saludo - 'ire a dormir'", "funcion": lambda: buscar_saludo("ire a dormir", conocimientos), "esperado": "que descanses, hasta mañana"},
        {"descripcion": "Prueba de saludo - 'bien'", "funcion": lambda: buscar_saludo("bien", conocimientos), "esperado": "que bueno que estes bien"},

        # Pruebas de chistes
        {"descripcion": "Prueba de chiste - 'sabes algun chiste'", "funcion": lambda: verificar_chiste("sabes algun chiste", conocimientos), "esperado": "Respuesta variable"},
        {"descripcion": "Prueba de chiste - 'otro chiste'", "funcion": lambda: verificar_chiste("otro chiste", conocimientos), "esperado": "Respuesta variable"},

        # Pruebas de presidente
        {"descripcion": "Prueba de presidente - 'quien fue presidente en el año 2024'", "funcion": lambda: presidente("quien fue presidente en el año 2024", conocimientos), "esperado": "Javier Gerardo Milei fue presidente entre 2023 - 2024."},
        {"descripcion": "Prueba de presidente - 'quien fue presidente en el año 90'", "funcion": lambda: presidente("quien fue presidente en el año 90", conocimientos), "esperado": "No tengo información sobre ese presidente o esa fecha. Por favor, intenta con un año de cuatro cifras, como 'quién fue presidente en el año 2022'."},

        # Pruebas de signos zodiacales
        {"descripcion": "Prueba de signo - 'aries'", "funcion": lambda: detectar_signo("aries"), "esperado": "El signo Aries cubre desde 21-03-2024 a 19-04-2024. Su elemento es fuego. Aries, el primer signo del zodiaco, es conocido por su energía y determinación. Los arianos son aventureros y les gusta ser líderes en cualquier situación. Son audaces y no temen asumir riesgos. Su personalidad ardiente les impulsa a actuar con rapidez y a buscar nuevas experiencias. Es compatible con: leo, sagitario, geminis."},

        # Pruebas de música y animales
        {"descripcion": "Prueba de música - 'cantante madonna'", "funcion": lambda: verificar_musica_animal("cantante madonna", conocimientos, animales_data), "esperado": "madonna: Madonna Louise Ciccone es un cantante de pop. Nació el 16-08-1958 en Estadounidense. Madonna es una de las figuras mas influyentes de la musica pop, conocida como la 'Reina del Pop'. Ha tenido una extensa carrera desde los anos 80, caracterizada por su habilidad para reinventarse y su influencia en la cultura musical."},
        {"descripcion": "Prueba de perro - 'que sabes del perro labrador'", "funcion": lambda: verificar_musica_animal("que sabes del perro labrador", conocimientos, animales_data), "esperado": "Labrador Retriever: Es una raza de perro grande, muy popular por su carácter amigable y su habilidad para el trabajo. Características: Peligro: Bajo, Docilidad: Alta, Amabilidad: Muy alta"},

        # Pruebas de matemáticas
        {"descripcion": "Prueba matemática - '20+20'", "funcion": lambda: matematica("20+20"), "esperado": "El resultado de 20+20 es 40."},
        {"descripcion": "Prueba matemática - 'pi*2+20'", "funcion": lambda: matematica("pi*2+20"), "esperado": "El resultado de 3.14*2+20 es 26.28."},
        {"descripcion": "Prueba matemática - 'raiz cuadrada de 25'", "funcion": lambda: matematica("raiz cuadrada de 25"), "esperado": "El resultado de raiz cuadrada de 25 es 5."},
        {"descripcion": "Prueba matemática - '20^3'", "funcion": lambda: matematica("20^3"), "esperado": "El resultado de 20**3 es 8000."},
        {"descripcion": "Prueba matemática - 'sin(90)'", "funcion": lambda: matematica("sin(90)"), "esperado": "El resultado de sin(90) es 1."}
    ]

    # Pruebas complejas (que requieren múltiples pasos)
    pruebas_complejas = [
        {"descripcion": "Prueba de opinión - 'te dejo una opinion'",
            "funcion": lambda: [
                manejar_recoleccion_opinion("josue", conocimientos, retroalimentacion),
                manejar_recoleccion_opinion("25", conocimientos, retroalimentacion),
                manejar_recoleccion_opinion("que tenga juegos de trivia", conocimientos, retroalimentacion)
            ],
            "esperado": "¡Gracias por tu opinión/sugerencia! La he guardado con tus datos."
        },
        # Pruebas de la función 'comida' en el autoanálisis
        {"descripcion": "Prueba de recetas - 'dame una receta de postre'",
         "funcion": lambda: comida("dame una receta de postre", conocimientos, eleccion_automatica=1),
         "esperado": "\nReceta de churros:\nIngredientes: 1 taza de harina, 1 taza de agua, 1 cucharadita de sal, Aceite para freír, Azúcar para espolvorear\nPaso a paso: Hierve el agua con la sal. -> Agrega la harina de golpe y mezcla bien hasta formar una masa. -> Deja enfriar un poco y coloca la masa en una manga pastelera. -> Calienta el aceite y fríe los churros hasta que estén dorados. -> Espolvorea con azúcar y sirve."}
    ]

    # Combinar todas las pruebas
    pruebas = pruebas_simples + pruebas_complejas

    # Resultado final de las pruebas
    resultados = []

    # Ejecutar cada prueba y almacenar el resultado
    for prueba in pruebas:
        try:
            resultado = prueba["funcion"]()
            if isinstance(resultado, list):
                # Si es una lista (prueba compleja), tomar el último resultado
                exitoso = resultado[-1] == prueba["esperado"]
                resultado_final = resultado[-1]
            else:
                # Prueba simple
                exitoso = resultado == prueba["esperado"] or prueba["esperado"] == "Respuesta variable"
                resultado_final = resultado

            resultados.append({
                "descripcion": prueba["descripcion"],
                "resultado": resultado_final,
                "esperado": prueba["esperado"],
                "exitoso": exitoso
            })
        except Exception as e:
            resultados.append({
                "descripcion": prueba["descripcion"],
                "resultado": f"ERROR: {str(e)}",
                "esperado": prueba["esperado"],
                "exitoso": False
            })

    # Guardar los resultados en el archivo 'diagnostico.json'
    guardar_datos(resultados, 'diagnostico.json', mostrar_mensaje=False)
    print("IA: Auto-análisis completado. Resultados guardados en 'diagnostico.json'.")
    # return explícito para evitar que retorne 'None'
    return "Análisis finalizado y resultados guardados correctamente."


# TODO: Función principal de preguntar (lógica de preguntas)
def preguntar(pregunta, conocimientos, animales_data, retroalimentacion, seleccion_automatica=None):
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
    if pregunta_limpia == "clark iniciar autoanalisis":
        nombre = input("Nombre de administrador: ")
        contrasena = input("Contraseña: ")
        resultado_analisis = auto_analisis(nombre, contrasena, conocimientos, animales_data, retroalimentacion)
        return resultado_analisis

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

    # Verificar si la pregunta es una consulta de recetas
    respuesta_receta = comida(pregunta, conocimientos)
    if respuesta_receta and "No entendí tu solicitud" not in respuesta_receta:
        conocimientos["contexto"]["ultimaPregunta"] = pregunta_limpia
        guardar_datos(conocimientos, 'conocimientos.json')
        return respuesta_receta

    # Manejar preguntas sobre plantas
    respuesta_planta, tipo_planta = manejar_planta(pregunta, conocimientos, seleccion_automatica)

    if respuesta_planta:  # Si hay una respuesta de plantas
        # Modo manual, ahora pedimos el número de la planta o temporada seleccionada
        if tipo_planta:  # Verifica que haya un tipo de planta válido
            print(respuesta_planta)  # Muestra la lista de opciones al usuario (solo en modo manual)

            # Si hay selección automática, usarla directamente
            if seleccion_automatica:
                detalle_planta = obtener_detalle_planta(tipo_planta, seleccion_automatica, conocimientos)
                return detalle_planta  # Retornamos la información detallada en modo automático

            # Lógica para cuando se consulta sobre la huerta
            if tipo_planta == 'huerta':
                seleccion = int(input("Introduce el número de la verdura que quieres conocer: ")) - 1
                if seleccion < 0:
                    raise ValueError("Número fuera de rango.")

                # Convertimos la selección numérica en el nombre de la planta
                planta_seleccionada = list(conocimientos.get('planta', {}).get('huerta', {}).values())[seleccion]['nombre']
                detalle_planta = obtener_detalle_planta(tipo_planta, planta_seleccionada, conocimientos)
                return detalle_planta

            # Lógica para suculentas o árboles (otros tipos)
            else:
                seleccion = int(input("Introduce el número de la planta que quieres conocer: ")) - 1
                if seleccion < 0:
                    raise ValueError("Número fuera de rango.")

                # Convertimos la selección numérica en el nombre de la planta
                if tipo_planta == 'suculentas':
                    planta_seleccionada = list(conocimientos.get('planta', {}).get('suculentas', {}).values())[seleccion]['nombre']
                elif tipo_planta == 'arboles':
                    planta_seleccionada = list(conocimientos.get('planta', {}).get('arboles', {}).values())[seleccion]['nombre']
                else:
                    return "Error al seleccionar la planta."

                # Obtener y devolver la información detallada de la planta seleccionada
                detalle_planta = obtener_detalle_planta(tipo_planta, planta_seleccionada, conocimientos)
                return detalle_planta

        else:
            return "No detecté ninguna palabra clave relacionada con plantas. Por favor, pregunta sobre suculentas, árboles o verduras."




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
