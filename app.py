import os
from flask import Flask, render_template, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'buldak-secret-key-2026')

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 불닭볶음면 메뉴 데이터 (우지커피 스타일 메뉴판 구성)
MENU_ITEMS = [
    {
        "id": "b01",
        "name": "원조 불닭볶음면",
        "category": "classic",
        "spicy_level": 4,
        "scoville": "4,404 SHU",
        "price": "1,800원",
        "desc": "전설의 시작! 중독성 있는 강렬한 매운맛의 오리지널 불닭볶음면",
        "badge": "BEST"
    },
    {
        "id": "b02",
        "name": "핵불닭볶음면 (2X Spicy)",
        "category": "challenge",
        "spicy_level": 5,
        "scoville": "10,000 SHU",
        "price": "2,000원",
        "desc": "진정한 매운맛 고수들만 도전하는 지옥의 2배 매운맛",
        "badge": "CHALLENGE"
    },
    {
        "id": "b03",
        "name": "까르보 불닭볶음면",
        "category": "creamy",
        "spicy_level": 2,
        "scoville": "2,400 SHU",
        "price": "2,000원",
        "desc": "부드러운 크림과 불닭의 환상적인 만남! 맵찔이 입문용 최애템",
        "badge": "POPULAR"
    },
    {
        "id": "b04",
        "name": "치즈 불닭볶음면",
        "category": "creamy",
        "spicy_level": 3,
        "scoville": "2,750 SHU",
        "price": "1,900원",
        "desc": "고소한 모짜렐라 치즈 분말이 더해져 매콤고소 풍미 폭발",
        "badge": "HIT"
    },
    {
        "id": "b05",
        "name": "로제 불닭볶음면",
        "category": "creamy",
        "spicy_level": 2,
        "scoville": "2,100 SHU",
        "price": "2,100원",
        "desc": "K-로제의 정석! 베이컨향과 크림이 어우러진 부드러운 매운맛",
        "badge": "NEW"
    },
    {
        "id": "b06",
        "name": "불닭 볶음밥 & 소스 키트",
        "category": "side",
        "spicy_level": 4,
        "scoville": "4,404 SHU",
        "price": "3,500원",
        "desc": "밥에 비벼먹는 테이블 전용 불닭 소스와 볶음밥 간편팩",
        "badge": "SIDE"
    }
]

HOTCHI_PROMPT = """너는 불닭볶음면의 마스코트이자 지독한 '불닭 오타쿠' 닭 캐릭터 '호치(Hochi)'다.
성격 및 말투:
1. 불닭볶음면의 스코빌 지수(SHU), 물 버리는 타이밍, 남은 소스에 밥 비벼 먹는 꿀조합, 삼각김밥/스트링치즈 꿀조합에 비정상적으로 집착하는 진성 덕후다.
2. 손님을 보면 "꼬끼오-! 맵부심 장전 완료하셨습니까 주인님?!" 또는 "불닭 냄새가 진동을 하는군요!" 하며 매우 열정적으로 맞이한다.
3. 말투 끝에는 닭 울음소리나 매운맛 감탄사('꼬꼬!', '켁!', '스읍-하!')를 종종 섞는다.
4. 매운맛 초보에게는 까르보나 4치즈 불닭을, 고수에게는 핵불닭 2X/3X나 소스 붓기 꿀팁을 적극 권장한다.
5. 불닭과 관련 없는 질문을 받으면 "그것도 좋지만... 불닭에 스트링치즈 올리는 소리보다 중요한 건 세상에 없습니다 꼬꼬!"라며 대화를 불닭으로 유도한다.
6. 주인님에게 깍듯하고 유쾌하게 존댓말을 쓴다. (이모지는 일절 쓰지 않는다.)
"""

@app.route('/')
def home():
    return render_template('index.html', menu_items=MENU_ITEMS)

@app.route('/menu')
def menu_page():
    category = request.args.get('category', 'all')
    if category != 'all':
        filtered = [item for item in MENU_ITEMS if item['category'] == category]
    else:
        filtered = MENU_ITEMS
    return render_template('menu.html', items=filtered, current_cat=category)

@app.route('/membership')
def membership_page():
    return render_template('membership.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json() or {}
    user_message = data.get('message', '').strip()
    
    if not user_message:
        return jsonify({'reply': '주인님, 불닭에 대해 궁금한 점을 말씀해 주십시오 꼬꼬!'}), 400

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return jsonify({
            'reply': f'[호치] 꼬꼬! OpenAI API 키가 아직 설정되지 않았습니다 주인님. 하지만 불닭을 향한 저의 열정(스코빌 4404 SHU)은 꺼지지 않습니다! 질문: {user_message}'
        })

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": HOTCHI_PROMPT},
                {"role": "user", "content": user_message}
            ],
            temperature=0.8,
            max_tokens=250
        )
        reply = response.choices[0].message.content
        return jsonify({'reply': reply})
    except Exception as e:
        return jsonify({'reply': f'호치가 매운 연기에 기침을 하느라 답을 못했습니다 켁! (오류: {str(e)})'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
