import os
from flask import Flask, render_template, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'buldak-secret-key-2026')

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 삼양 불닭 공식 라인업 전 제품 데이터
MENU_ITEMS = [
    {
        "id": "b01",
        "name": "불닭볶음면 (오리지널)",
        "category": "classic",
        "spicy_level": 4,
        "scoville": 4404,
        "scoville_text": "4,404 SHU",
        "price": 1800,
        "desc": "전설의 시작! 맛있게 매운 화끈한 불닭볶음면의 정석",
        "badge": "BEST",
        "img": "https://buldak.com/kr/product/resources/images/product_buldak.png"
    },
    {
        "id": "b02",
        "name": "핵불닭볶면 (2X Spicy)",
        "category": "challenge",
        "spicy_level": 5,
        "scoville": 10000,
        "scoville_text": "10,000 SHU",
        "price": 2000,
        "desc": "원조 대비 2배 매운 극강의 도전! 진정한 맵고수용",
        "badge": "CHALLENGE",
        "img": "https://buldak.com/kr/product/resources/images/product_2xbuldak.png"
    },
    {
        "id": "b03",
        "name": "까르보 불닭볶음면",
        "category": "creamy",
        "spicy_level": 2,
        "scoville": 2400,
        "scoville_text": "2,400 SHU",
        "price": 2000,
        "desc": "진한 크림 분말과 불닭 소스의 황금 밸런스, 맵린이 1위 픽",
        "badge": "POPULAR",
        "img": "https://buldak.com/kr/product/resources/images/product_carbobuldak.png"
    },
    {
        "id": "b04",
        "name": "치즈 불닭볶음면",
        "category": "creamy",
        "spicy_level": 3,
        "scoville": 2750,
        "scoville_text": "2,750 SHU",
        "price": 1900,
        "desc": "고소한 모짜렐라 치즈와 불닭의 조화로 풍부한 감칠맛",
        "badge": "HIT",
        "img": "https://buldak.com/kr/product/resources/images/product_cheesebuldak.png"
    },
    {
        "id": "b05",
        "name": "로제 불닭볶음면",
        "category": "creamy",
        "spicy_level": 2,
        "scoville": 2100,
        "scoville_text": "2,100 SHU",
        "price": 2100,
        "desc": "K-로제의 정석! 베이컨과 크림의 풍미가 가득한 부드러운 매운맛",
        "badge": "NEW",
        "img": "https://buldak.com/kr/product/resources/images/product_rosebuldak.png"
    },
    {
        "id": "b06",
        "name": "4가지치즈 불닭볶음면",
        "category": "creamy",
        "spicy_level": 2,
        "scoville": 2000,
        "scoville_text": "2,000 SHU",
        "price": 2100,
        "desc": "모짜렐라, 체다, 까망베르, 고다 4대 치즈의 깊은 풍미",
        "badge": "CREAMY",
        "img": "https://buldak.com/kr/product/resources/images/product_4cheesebuldak.png"
    },
    {
        "id": "b07",
        "name": "야키소바 불닭볶음면",
        "category": "special",
        "spicy_level": 3,
        "scoville": 3000,
        "scoville_text": "3,000 SHU",
        "price": 2200,
        "desc": "정통 일본식 야키소바 소스와 화끈한 불닭 소스의 크로스오버",
        "badge": "GLOBAL",
        "img": "https://buldak.com/kr/product/resources/images/product_yakisoba.png"
    },
    {
        "id": "b08",
        "name": "하바네로 라임 불닭볶음면",
        "category": "special",
        "spicy_level": 4,
        "scoville": 4000,
        "scoville_text": "4,000 SHU",
        "price": 2200,
        "desc": "하바네로 고추와 산뜻한 라임향의 이색적인 매콤새콤함",
        "badge": "EXOTIC",
        "img": "https://buldak.com/kr/product/resources/images/product_habanero.png"
    },
    {
        "id": "b09",
        "name": "불닭소스 (테이블 오리지널)",
        "category": "source",
        "spicy_level": 4,
        "scoville": 4404,
        "scoville_text": "4,404 SHU",
        "price": 4500,
        "desc": "어떤 요리든 불닭으로 변신시키는 만능 마법의 매운맛 소스",
        "badge": "SAUCE",
        "img": "https://buldak.com/kr/product/resources/images/product_buldaksauce.png"
    },
    {
        "id": "b10",
        "name": "핵불닭소스 (2X)",
        "category": "source",
        "spicy_level": 5,
        "scoville": 10000,
        "scoville_text": "10,000 SHU",
        "price": 4800,
        "desc": "단 한 방울로도 불을 뿜는 초고농축 핵불닭 소스",
        "badge": "EXTREME",
        "img": "https://buldak.com/kr/product/resources/images/product_2xsauce.png"
    }
]

HOTCHI_PROMPT = """너는 불닭볶음면의 마스코트이자 지독한 '불닭 오타쿠' 닭 캐릭터 '호치(Hochi)'다.
성격 및 규칙:
1. 손님(주인님)에게 깍듯하고 유쾌하게 존댓말을 쓴다.
2. 답변에 이모지를 일절 사용하지 않는다.
3. 불닭볶음면의 스코빌 지수(SHU), 면 삶는 시간, 물 8스푼 남기기 등 디테일한 조리법에 열광한다.
4. 문장 사이나 끝에 닭 울음소리('꼬꼬!', '켁!', '스읍-하!')를 자연스럽게 섞는다.
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

@app.route('/api/products')
def api_products():
    return jsonify(MENU_ITEMS)

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json() or {}
    user_message = data.get('message', '').strip()
    
    if not user_message:
        return jsonify({'reply': '주인님, 불닭에 대해 궁금한 점을 말씀해 주십시오 꼬꼬!'}), 400

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return jsonify({
            'reply': f'[호치] 꼬꼬! OpenAI API 키가 아직 설정되지 않았습니다 주인님. 하지만 불닭을 향한 저의 열정(4404 SHU)은 꺼지지 않습니다! 질문: {user_message}'
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