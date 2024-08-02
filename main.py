import openai
from openai import OpenAI
from flask import Flask, request, jsonify
from decouple import config
from flask_cors import CORS, cross_origin

def create_App():
    app = Flask(__name__)
    CORS(app)
        
    openai = OpenAI(api_key = config('OPENAI_API_KEY'))

    @cross_origin
    @app.route('/generador', methods=['POST'])
    def generar_causas():
        data = request.get_json()

        if not data or 'problem' not in data:
            return jsonify({'rror': 'No se proporcionó ningún texto para clasificar.'}), 400

        problem = data['problem']
        items = {}

        prompt = (f'Vas a generar 20 pasos a realizar según un plan de continuidad del negocio (BCP), 10 de estos van a ser correctos y los otros 10 van a ser incorrectos, haz de realizar esto basado en el problema: {problem}, solamente dame los títulos de cada actividad a realizar y sin enumerar')
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Eres un experto en ciberseguridad y realizas un análisis Bussiness Continuity Plan basado en el método KJ."},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            max_tokens=2000,
            top_p=1,
            frequency_penalty=0.5,
            presence_penalty=0
        )

        items_aux = response.choices[0].message.content.split("\n\n")
        items_aux[0] = items_aux[0].split("\n- ")
        items_aux[1] = items_aux[1].split("\n- ")
        
        items_aux[0].pop(0)
        items_aux[1].pop(0)

        items['correct'] = items_aux[0]
        items['incorrect'] = items_aux[1]

        return items
    
    @cross_origin
    @app.route('/calificador', methods=['POST'])
    def calificar():
        data = request.get_json()

        items_correct = data['correct']
        responses = data['responses']
        result = {}

        prompt = (f'Las acciones del usuario son: {responses}\nLas respuestas correctas son: {items_correct}')
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": " Eres un evaluador, vas a calificar sobre un punto las acciones correctas tomadas por el usuario, comparándolas con las respuestas correctas, se te debe enviar diez acciones correctas para una calificación de 10, caso contrario la calificación baja en 1 punto por cada respuesta faltante(ejemplo: Acciones del usuario=['Realizar backups', 'Comunicar a los clientes']; calificación máxima=2) y además si la acción del usuario no coincide con ninguna respuesta correcta o carece de sentido, no sumaría ningún punto adicional (ejemplo: Acciones del usuario=['Realizar backups', 'Ver como va']; calificación = 1)"},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            max_tokens=500,
        )
        result = response.choices[0].message.content

        return result
    
    return app


if __name__ == '__main__':
    app = create_App()
    app.run()
