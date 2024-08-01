import openai
from openai import OpenAI
from flask import Flask, request, jsonify
from decouple import config

def create_App():
    app = Flask(__name__)
    
    
    openai = OpenAI(api_key = config('OPENAI_API_KEY'))


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
                {"role": "system", "content": "Eres un experto en ciberseguridad y realizas un análisis BCA basado en el método KJ."},
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
    
    return app


if __name__ == '__main__':
    app = create_App()
    app.run()
