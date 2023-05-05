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

question_context = "Genera 10 preguntas (en formato json {'tipo_pregunta':'multiple_respuesta|verdadero_o_falso|respuesta_unica', 'pregunta':'pregunta generada', 'opciones':'opciones posibles enumeradas de la forma a, b, c, d', 'respuesta_correcta':'la letra respuesta correcta'} basadas en el siguiente contexto: "

long_questions = "En este contexto, se te proporcionará un tema específico junto con una descripción detallada del mismo. A partir de esta información, se generarán preguntas de desarrollo que requerirán respuestas extensas y bien fundamentadas. El objetivo es evaluar y reforzar tu comprensión en profundidad del tema, así como fomentar habilidades analíticas y de pensamiento crítico en la materia. Que el formato de las preguntas sea: [{pregunta:respuesta},{pregunta:respuesta}]"
short_questions = "Este contexto se centra en presentarte un tema y su descripción, a partir de los cuales se generarán preguntas breves que demandarán respuestas concisas y directas. Estas preguntas están diseñadas para evaluar tu conocimiento básico y retener información clave del tema estudiado, permitiéndote practicar la síntesis y la precisión al responder. Que el formato de las preguntas sea: [{pregunta:respuesta},{pregunta:respuesta}]"
test_questions = "En este tercer contexto, recibirás un tema acompañado de su descripción, y se generarán preguntas tipo test con cuatro opciones de respuesta. Algunas preguntas permitirán múltiples respuestas correctas, mientras que otras admitirán solamente una. Estas preguntas de opción múltiple tienen como objetivo evaluar tu habilidad para identificar información correcta y relevante del tema, y poner a prueba tu comprensión general de la materia de manera más rápida y eficiente. Que el formato de las preguntas sea: [{pregunta:respuesta},{pregunta:respuesta}]"

asignaturas = {}

# Funciones para guardar y cargar asignaturas


def cargar_datos(archivo="data.json"):
    with open(archivo, "r", encoding="utf-8") as file:
        data = json.load(file)
    return data


def guardar_datos(data, archivo="data.json"):
    with open(archivo, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def generar_preguntas(contexto, tipo_pregunta):
    global short_questions, long_questions, test_questions, question_context

    prompt = question_context + contexto

    messages = [
        {"role": "system", "content": short_questions if tipo_pregunta ==
            "Preguntas cortas" else long_questions if tipo_pregunta == "Preguntas largas" else test_questions},
        {"role": "user", "content": prompt}
    ]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=1000,
        n=1,
        stop=None,
        temperature=0.8,
    )

    preguntas_json = response.choices[0].message["content"]
    print(preguntas_json)
    preguntas = json.loads(preguntas_json)
    return preguntas


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


def menu_tipo_pregunta():
    print("\n--- Selecciona el tipo de preguntas ---")
    tipos_pregunta = ["Preguntas largas",
                      "Preguntas cortas", "Preguntas tipo test"]
    mostrar_menu(tipos_pregunta, "Tipos de preguntas")
    tipo_seleccionado = seleccionar_opcion(tipos_pregunta)
    if tipo_seleccionado == 0:
        return None
    return tipos_pregunta[tipo_seleccionado - 1]


def obtener_descripcion_tema(asignatura, tema, datos):
    temas = datos[asignatura]
    for t in temas:
        if tema in t:
            return t[tema]
    return None


def realizar_preguntas_test(preguntas):
    respuestas_correctas = 0
    total_preguntas = len(preguntas)

    for i, pregunta in enumerate(preguntas):
        print(f"\nPregunta {i + 1} de {total_preguntas}:")
        print(pregunta["pregunta"])
        print(pregunta["opciones"])

        respuesta_usuario = input("\nIntroduce tu respuesta: ")

        if respuesta_usuario.lower() == pregunta["respuesta_correcta"].lower():
            respuestas_correctas += 1
            print("¡Respuesta correcta!")
        else:
            print(
                f"Respuesta incorrecta. La respuesta correcta es: {pregunta['respuesta_correcta']}")

    print(
        f"\nHas respondido correctamente {respuestas_correctas} de {total_preguntas} preguntas.")


def main():
    global datos
    datos = cargar_datos()

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

            # Menú tipo de preguntas: seleccionar tipo
            tipo_pregunta_seleccionado = menu_tipo_pregunta()
            if not tipo_pregunta_seleccionado:
                break

            contexto = "La asignatura es " + asignatura_seleccionada + ". El tema es " + tema_seleccionado + \
                ". Que trata de: " + \
                obtener_descripcion_tema(
                    asignatura_seleccionada, tema_seleccionado, datos)
            preguntas = generar_preguntas(contexto, tipo_pregunta_seleccionado)

            # Aquí, la variable "preguntas" contiene las preguntas y respuestas generadas en formato JSON
            print(
                f"\nHas seleccionado la asignatura '{asignatura_seleccionada}', el tema '{tema_seleccionado}' y el tipo de preguntas '{tipo_pregunta_seleccionado}'. ¡Buena suerte estudiando!")
            print(preguntas)

            realizar_preguntas_test(preguntas)


if __name__ == "__main__":
    main()
