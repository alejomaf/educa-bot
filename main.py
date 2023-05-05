import os
import openai
import json
from unidecode import unidecode
from dotenv import load_dotenv

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Importar la clave de la API de OpenAI desde el archivo .env
api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = api_key

long_questions = "En este contexto, se te proporcionará un tema específico junto con una descripción detallada del mismo. A partir de esta información, se generarán preguntas de desarrollo que requerirán respuestas extensas y bien fundamentadas. El objetivo es evaluar y reforzar tu comprensión en profundidad del tema, así como fomentar habilidades analíticas y de pensamiento crítico en la materia."
short_questions = "Este contexto se centra en presentarte un tema y su descripción, a partir de los cuales se generarán preguntas breves que demandarán respuestas concisas y directas. Estas preguntas están diseñadas para evaluar tu conocimiento básico y retener información clave del tema estudiado, permitiéndote practicar la síntesis y la precisión al responder."
test_questions = "En este tercer contexto, recibirás un tema acompañado de su descripción, y se generarán preguntas tipo test con cuatro opciones de respuesta. Algunas preguntas permitirán múltiples respuestas correctas, mientras que otras admitirán solamente una. Estas preguntas de opción múltiple tienen como objetivo evaluar tu habilidad para identificar información correcta y relevante del tema, y poner a prueba tu comprensión general de la materia de manera más rápida y eficiente."

asignaturas = {}

# Funciones para guardar y cargar asignaturas


def cargar_datos(archivo="data.json"):
    with open(archivo, "r", encoding="utf-8") as file:
        data = json.load(file)
    return data


def guardar_datos(data, archivo="data.json"):
    with open(archivo, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def generate_text(chapter, prompt, add_context=True, model="gpt-3.5-turbo", max_tokens=1000):
    global project_context
    messages = [{"role": "system", "content": project_context},
                {"role": "user", "content": prompt}]

    content_generated = False

    while not content_generated:
        try:
            response = openai.ChatCompletion.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                n=1,
                stop=None,
                temperature=0.4,  # this is the degree of randomness of the model's output
            )
            content_generated = True
        except:
            print("Error en la generación del capítulo, volviendo a intentar...")

    chapter_generated = response.choices[0].message["content"]
    if add_context:
        project_context += "\n" + summarize_chapter(chapter, prompt)
    # project_context += "\n" + chapter_generated
    print(project_context)
    return chapter_generated


def summarize_chapter(chapter, prompt, model="gpt-3.5-turbo", max_tokens=700):
    global project_context
    messages = [
        {"role": "system", "content": project_context},
        {"role": "user", "content": "Haz un resumen de este capítulo de menos de 60 palabras: " + prompt}]

    content_generated = False

    while not content_generated:
        try:
            response = openai.ChatCompletion.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                n=1,
                stop=None,
                temperature=0,  # this is the degree of randomness of the model's output
            )
            content_generated = True
        except:
            print("Error en la generación del resumen, volviendo a intentar...")

    return "Resumen de "+chapter+" "+response.choices[0].message["content"]


def initialize_gpt_context(title, model="gpt-3.5-turbo", max_tokens=700):
    global project_context
    global indice
    messages = [
        {"role": "user", "content": "Elabora un guión y un resumen de 100 palabras para desarrollar un proyecto que trate de: " + title}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        max_tokens=max_tokens,
        n=1,
        stop=None,
        temperature=0.2,  # this is the degree of randomness of the model's output
    )
    project_context += "\n El proyecto trata de " + \
        response.choices[0].message["content"]

    messages = [
        {"role": "user", "content": "Elabora un índice para desarrollar un un proyecto que trate de: '" + title + "' proyecta ese índice en formato json de la siguiente forma [\{nombre_del_capitulo_1: [subapartado_1, subapartado2...]\},\{nombre_del_capitulo_2: [subapartado_1, subapartado2...]\}...]"}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        max_tokens=max_tokens,
        n=1,
        stop=None,
        temperature=0,  # this is the degree of randomness of the model's output
    )
    indice = json.loads(response.choices[0].message["content"])

    print(project_context)
    print(indice)


def mostrar_menu(opciones, titulo):
    print(f"\n--- {titulo} ---")
    for idx, opcion in enumerate(opciones, start=1):
        print(f"{idx}. {opcion}")
    print("0. Agregar asignaturas y temas")


def seleccionar_opcion(opciones):
    while True:
        try:
            seleccion = int(input("Selecciona una opción: "))
            if 0 <= seleccion <= len(opciones):
                return seleccion
            else:
                print("Por favor, selecciona una opción válida.")
        except ValueError:
            print("Por favor, ingresa un número.")


def menu_principal(data):
    asignaturas = list(data.keys())
    mostrar_menu(asignaturas, "Menú principal")
    seleccion = seleccionar_opcion(asignaturas)
    if seleccion == 0:
        return None
    return asignaturas[seleccion - 1]


def menu_temas(data, asignatura):
    temas = [list(tema.keys())[0] for tema in data[asignatura]]
    mostrar_menu(temas, f"Temas de {asignatura}")
    seleccion = seleccionar_opcion(temas)
    if seleccion == 0:
        return None
    return temas[seleccion - 1]


def agregar_asignatura(data):
    nombre_asignatura = input(
        "Introduce el nombre de la nueva asignatura: ").strip()
    if nombre_asignatura in data:
        print("Esta asignatura ya existe. Por favor, elige otro nombre.")
        return
    data[nombre_asignatura] = []
    print(f"Asignatura '{nombre_asignatura}' agregada exitosamente.")


def agregar_tema(data, asignatura):
    nombre_tema = input("Introduce el nombre del nuevo tema: ").strip()
    for tema in data[asignatura]:
        if nombre_tema in tema:
            print("Este tema ya existe en la asignatura. Por favor, elige otro nombre.")
            return
    descripcion_tema = input(
        "Introduce una descripción detallada del tema: ").strip()
    data[asignatura].append({nombre_tema: descripcion_tema})
    print(
        f"Tema '{nombre_tema}' agregado exitosamente a la asignatura '{asignatura}'.")


def menu_agregar(data):
    print("\n--- Menú para agregar ---")
    print("1. Agregar asignatura")
    print("2. Agregar tema a una asignatura")
    print("0. Volver al menú principal")
    seleccion = seleccionar_opcion([1, 2])
    if seleccion == 1:
        agregar_asignatura(data)
    elif seleccion == 2:
        asignatura_seleccionada = menu_principal(data)
        if asignatura_seleccionada:
            agregar_tema(data, asignatura_seleccionada)


def main():
    global datos
    datos = cargar_datos()
    print(datos)

    while True:
        # Menú principal: seleccionar asignatura o agregar contenido
        asignatura_seleccionada = menu_principal(datos)

        if not asignatura_seleccionada:
            menu_agregar(datos)
            guardar_datos(datos)  # Guardar datos actualizados en el archivo
            continue

        while True:
            # Menú temas: seleccionar tema
            tema_seleccionado = menu_temas(datos, asignatura_seleccionada)
            if not tema_seleccionado:
                break

            print(
                f"\nHas seleccionado la asignatura '{asignatura_seleccionada}' y el tema '{tema_seleccionado}'. ¡Buena suerte estudiando!")


if __name__ == "__main__":
    main()
