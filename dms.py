import requests
from datetime import date
import urllib.request
import json

BASE_URL = 'http://dsm2015.cafe24.com:3000/'
AUTH_STUDENT = f'{BASE_URL}auth/student'
LOGIN_STUDENT = 'http://dsm2015.cafe24.com/account/login/student'
STUDY_MORE_11 = 'http://dsm2015.cafe24.com/apply/extension/11'
MEAL_URL = f'{BASE_URL}meal/'

CLASSIDS = {
    '가': 1,
    '가온': 1,
    '가온실': 1,
    '나': 2,
    '나온': 2,
    '나온실': 2,
    '다': 3,
    '다온': 3,
    '다온실': 3,
    '라': 4,
    '라온': 4,
    '라온실': 4,
    '3': 5,
    '삼': 5,
    '3층': 5,
    '삼층': 5,
    '4': 6,
    '사': 6,
    '4층': 6,
    '사층': 6,
    '5': 7,
    '오': 7,
    '5층': 7,
    '오층': 7
}

def classid_from_name(name: str):
    if name in CLASSIDS.keys():
        return name
    else:
        raise Exception('어디인지 모르겠네요')

def login(_id: str, pw: str) -> str:
    s = requests.Session()
    req = s.post(LOGIN_STUDENT, {'id': _id, 'password': pw})
    if req.status_code == 201:
        return s
    if req.status_code == 204:
        raise Exception('로그인 실패')
    raise Exception('서버가 죽었거나 내가 노답이거나 둘 중 하나겠지')

def study_more(s: requests.Session, room: int, seat: int):
    req = s.put(STUDY_MORE_11, {'class': room, 'seat': seat})
    if req.status_code == 204:
        raise Exception('응 연장시간 아니야~')
    if req.status_code == 200:
        return req
    raise Exception('오류남.. 아마도 걔네가 잘못한거임')

def cancle_more(s: requests.Session):
    pass

def meal(date: date) -> dict:
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
                "pretext": f"{date} 급식:rice:",
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
    return msg

def test_login():
    return login('dudcksdldjfrnf', 'dudcksdldjfrnf')
