from flask import Flask, Response, jsonify, request
from datetime import date
import urllib.request
import json
import dms
app = Flask(__name__)

@app.route('/')
def homepage():
    return """
    <h1>Hello heroku</h1>
    <p>It is currently {time}.</p>
    """.format(time=date.today())

@app.route('/slack/command/meal', methods=['POST'])
def meal():
    print(request.form.get('text'))
    try:
        res = dms.meal(date.today())
    except Exception as e:
        print('err', e.args)
        msg = {'response_type': 'in_channel', 'text': f'에러:blush::gun:\n{e.args[0]}'}
        return Response(json.dumps(msg), mimetype='application/json')
    return Response(res, mimetype='application/json')

@app.route('/slack/command/login', methods=['POST'])
def login():
    msg = {
        "text": "DMS에 로그인할거냐?",
        "attachments": [
            {
                "text": "비밀번호를 평문으로 맡겨도 될 만큼 안전할 거 같냐?",
                "fallback": "안전할 거 같아?",
                "callback_id": "login_answer",
                "color": "#ff0000",
                "attachment_type": "default",
                "actions": [
                    {
                        "name": "answer",
                        "text": "네!!!",
                        "type": "button",
                        "style": "danger",
                        "value": "yes"
                    },
                    {
                        "name": "answer",
                        "text": "아뇨..",
                        "type": "button",
                        "value": "no"
                    }
                ]
            }
        ]
    }
    return Response(json.dumps(msg), mimetype='application/json')

@app.route('/slack/command/home', methods=['POST'])
def janryu():
    pass

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
