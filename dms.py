import requests
from datetime import date
import urllib.request
import json

BASE_URL = 'http://dsm2015.cafe24.com:3000/'
AUTH_STUDENT = f'{BASE_URL}auth/student'
LOGIN_STUDENT = 'http://dsm2015.cafe24.com/account/login/student'
STUDY_MORE_11 = 'http://dsm2015.cafe24.com/apply/extension/11'
MEAL_URL = f'{BASE_URL}meal/'

def login(id: str, pw: str) -> str:
    s = requests.Session()
    req = s.post(LOGIN_STUDENT, {'id': id, 'password': pw})
    if req.status_code == 201:
        return s
    if req.status_code == 204:
        raise Exception('로그인 실패')
    raise Exception('서버가 죽었거나 내가 노답이거나 둘 중 하나겠지')

def study_more(s: requests.Session, room: int, seat: int):
    req = s.put(STUDY_MORE_11, {'class': room, 'seat': seat})
    if req.status_code == 204:
        raise Exception('응 늦었어~')
    if req.status_code == 200:
        return req
    raise Exception('오류남.. 아마도 걔네가 잘못한거임')

def meal(date: date) -> str:
    url = f'{MEAL_URL}{str(date)}'
    print(url)
    try:
        bs = urllib.request.urlopen(url).read()
        res = json.loads(bs)
    except:
        raise Exception('한심한 DMS 급식 또 터졌음 :thinking_face:\n왜냐하면 내가 잘못됐을리는 없거든')

    msg = {
        'response_type': 'in_channel',
        "attachments": [
            {
                "fallback": "",
                "pretext": "오늘자 급식:rice:",
                "fields": [
                    {
                        "title": "아침",
                        "value": '\n'.join(res['breakfast']),
                        "short": True
                    },
                    {
                        "title": "점심",
                        "value": '\n'.join(res['lunch']),
                        "short": True
                    },
                    {
                        "title": "저녁",
                        "value": '\n'.join(res['dinner']),
                        "short": True
                    }
                    ],
                "color": "#7CD197"
            }
        ]
    }
    return json.dumps(msg)

def test_login():
    return login('dudcksdldjfrnf', 'dudcksdldjfrnf')
