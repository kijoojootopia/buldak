import os

files = {
    "requirements.txt": """flask>=3.0.0
gunicorn>=21.2.0
openai>=1.12.0
python-dotenv>=1.0.0
""",

    "render.yaml": """services:
  - type: web
    name: buldak-oozy-app
    runtime: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn app:app
    envVars:
      - key: OPENAI_API_KEY
        sync: false
      - key: SECRET_KEY
        generateValue: true
""",

    ".env.example": """OPENAI_API_KEY=your_openai_api_key_here
SECRET_KEY=your_secret_key_here
""",

    "app.py": '''import os
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
''',

    "templates/base.html": '''<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>{% block title %}불닭 x 우지오더 모바일{% endblock %}</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <div class="mobile-container">
        <!-- 상단 헤더 -->
        <header class="app-header">
            <div class="logo">
                <span class="brand-sub">BULDAK ORDER</span>
                <span class="brand-title">불닭 오더</span>
            </div>
            <div class="header-status">
                <span class="flame-tag">HOT 4404 SHU</span>
            </div>
        </header>

        <!-- 메인 콘텐츠 영역 -->
        <main class="content-area">
            {% block content %}{% endblock %}
        </main>

        <!-- 하단 네비게이션 바 (우지커피 앱 스타일) -->
        <nav class="bottom-nav">
            <a href="{{ url_for('home') }}" class="nav-item {% if request.endpoint == 'home' %}active{% endif %}">
                <div class="nav-icon">HOME</div>
                <div class="nav-label">홈</div>
            </a>
            <a href="{{ url_for('menu_page') }}" class="nav-item {% if request.endpoint == 'menu_page' %}active{% endif %}">
                <div class="nav-icon">MENU</div>
                <div class="nav-label">메뉴주문</div>
            </a>
            <a href="{{ url_for('membership_page') }}" class="nav-item {% if request.endpoint == 'membership_page' %}active{% endif %}">
                <div class="nav-icon">STAMP</div>
                <div class="nav-label">스탬프</div>
            </a>
            <button id="open-chat-btn" class="nav-item chat-trigger">
                <div class="nav-icon">HOTCHI</div>
                <div class="nav-label">호치톡</div>
            </button>
        </nav>

        <!-- 닭 얼굴 호치 챗봇 모달 레이어 -->
        <div id="chat-modal" class="chat-modal hidden">
            <div class="chat-header">
                <div class="rooster-profile">
                    <!-- SVG 닭 캐릭터 얼굴 -->
                    <svg class="rooster-svg" viewBox="0 0 100 100" width="44" height="44">
                        <circle cx="50" cy="50" r="45" fill="#E62129"/>
                        <!-- 닭 벼슬 -->
                        <path d="M40,15 Q50,0 60,15 Q70,5 75,22 Q65,25 50,22 Z" fill="#8B0000"/>
                        <!-- 눈 -->
                        <circle cx="35" cy="45" r="7" fill="#FFFFFF"/>
                        <circle cx="37" cy="45" r="3.5" fill="#111111"/>
                        <circle cx="65" cy="45" r="7" fill="#FFFFFF"/>
                        <circle cx="63" cy="45" r="3.5" fill="#111111"/>
                        <!-- 부리 -->
                        <polygon points="50,48 40,62 60,62" fill="#FFC800"/>
                        <!-- 볼터치 (불닭 매운맛 표현) -->
                        <circle cx="26" cy="56" r="6" fill="#FFA500" opacity="0.8"/>
                        <circle cx="74" cy="56" r="6" fill="#FFA500" opacity="0.8"/>
                        <!-- 턱수염 벼슬 -->
                        <path d="M46,62 Q50,75 54,62 Z" fill="#8B0000"/>
                    </svg>
                    <div class="rooster-meta">
                        <div class="rooster-name">호치 (불닭 오타쿠)</div>
                        <div class="rooster-desc">불닭 레시피 덕질 12년차</div>
                    </div>
                </div>
                <button id="close-chat-btn" class="close-btn">&times;</button>
            </div>
            <div id="chat-messages" class="chat-body">
                <div class="chat-bubble bot">
                    꼬꼬! 주인님 오셨습니까! 오늘도 화끈하게 스코빌 뿜어낼 불닭 라인업 완비했습니다. 조합 문의든 맵기 상담이든 무엇이든 물어보십시오!
                </div>
            </div>
            <div class="chat-input-row">
                <input type="text" id="chat-user-input" placeholder="호치에게 불닭 꿀조합을 물어보세요..." />
                <button id="chat-send-btn">전송</button>
            </div>
        </div>
    </div>

    <script src="{{ url_for('static', filename='js/main.js') }}"></script>
</body>
</html>
''',

    "templates/index.html": '''{% extends "base.html" %}
{% block content %}
<div class="home-screen">
    <!-- 메인 프로모션 배너 -->
    <section class="hero-banner">
        <span class="hero-sub">우지오더 스타일 x 매운맛의 끝판왕</span>
        <h2 class="hero-title">불닭 챌린지 시즌<br>극강의 매운맛 오더</h2>
        <p class="hero-desc">지금 모바일로 미리 주문하고 갓 조리된 화끈함을 픽업하세요.</p>
        <a href="{{ url_for('menu_page') }}" class="btn-primary">바로 주문하기</a>
    </section>

    <!-- 스코빌 미터기 위젯 -->
    <section class="scoville-widget">
        <div class="widget-title">오늘의 추천 맵부심 지수</div>
        <div class="meter-bar">
            <div class="meter-fill" style="width: 88%;"></div>
        </div>
        <div class="meter-label">
            <span>순한맛 (까르보)</span>
            <strong>핵불닭 10,000 SHU</strong>
        </div>
    </section>

    <!-- 퀵 바로가기 그리드 (우지커피 앱 기능 차용) -->
    <div class="quick-grid">
        <a href="{{ url_for('menu_page', category='classic') }}" class="quick-card">
            <span class="quick-tag">ORIGINAL</span>
            <span class="quick-name">원조 불닭</span>
        </a>
        <a href="{{ url_for('menu_page', category='creamy') }}" class="quick-card">
            <span class="quick-tag">CREAM</span>
            <span class="quick-name">까르보/로제</span>
        </a>
        <a href="{{ url_for('menu_page', category='challenge') }}" class="quick-card flame-bg">
            <span class="quick-tag">HELL</span>
            <span class="quick-name">핵불닭 2X</span>
        </a>
        <a href="{{ url_for('membership_page') }}" class="quick-card">
            <span class="quick-tag">REWARD</span>
            <span class="quick-name">불스탬프 10장</span>
        </a>
    </div>

    <!-- 인기 메뉴 프리뷰 슬라이더형 목록 -->
    <section class="recommend-section">
        <div class="sec-header">
            <h3>실시간 인기 불닭</h3>
            <a href="{{ url_for('menu_page') }}">전체보기 &gt;</a>
        </div>
        <div class="item-scroll-list">
            {% for item in menu_items[:3] %}
            <div class="item-card">
                <span class="item-badge">{{ item.badge }}</span>
                <h4 class="item-name">{{ item.name }}</h4>
                <div class="item-scoville">맵기 지수: {{ item.scoville }}</div>
                <div class="item-bottom">
                    <span class="item-price">{{ item.price }}</span>
                    <button class="cart-btn" onclick="alert('{{ item.name }}이(가) 장바구니에 담겼습니다 주인님!')">담기</button>
                </div>
            </div>
            {% endfor %}
        </div>
    </section>
</div>
{% endblock %}
''',

    "templates/menu.html": '''{% extends "base.html" %}
{% block title %}메뉴 주문 - 불닭 오더{% endblock %}
{% block content %}
<div class="menu-screen">
    <!-- 카테고리 탭 (우지커피 서브페이지 구조) -->
    <div class="category-tabs">
        <a href="{{ url_for('menu_page', category='all') }}" class="tab {% if current_cat == 'all' %}active{% endif %}">전체</a>
        <a href="{{ url_for('menu_page', category='classic') }}" class="tab {% if current_cat == 'classic' %}active{% endif %}">오리지널</a>
        <a href="{{ url_for('menu_page', category='creamy') }}" class="tab {% if current_cat == 'creamy' %}active{% endif %}">크리미 라인</a>
        <a href="{{ url_for('menu_page', category='challenge') }}" class="tab {% if current_cat == 'challenge' %}active{% endif %}">핵불닭 챌린지</a>
        <a href="{{ url_for('menu_page', category='side') }}" class="tab {% if current_cat == 'side' %}active{% endif %}">사이드/소스</a>
    </div>

    <!-- 메뉴 리스트 -->
    <div class="menu-list">
        {% for item in items %}
        <div class="menu-item-row">
            <div class="menu-meta">
                <span class="menu-badge">{{ item.badge }}</span>
                <h4 class="menu-title">{{ item.name }}</h4>
                <p class="menu-desc">{{ item.desc }}</p>
                <div class="menu-stat">
                    <span class="stat-shu">{{ item.scoville }}</span>
                    <span class="stat-level">맵기 레벨 {{ item.spicy_level }}/5</span>
                </div>
                <div class="menu-price">{{ item.price }}</div>
            </div>
            <button class="order-action-btn" onclick="alert('{{ item.name }} 주문 픽업 접수 완료! 호치가 빠르게 조리합니다.')">
                주문하기
            </button>
        </div>
        {% endfor %}
    </div>
</div>
{% endblock %}
''',

    "templates/membership.html": '''{% extends "base.html" %}
{% block title %}불닭 스탬프 멤버십 - 불닭 오더{% endblock %}
{% block content %}
<div class="membership-screen">
    <div class="stamp-card-wrap">
        <div class="card-header">
            <h3>불닭 매니아 멤버십</h3>
            <span class="card-no">NO. 8839-4404</span>
        </div>
        <p class="card-sub">불닭볶음면 1그릇당 화끈한 스탬프 1개 적립</p>

        <!-- 10개 스탬프 보드 -->
        <div class="stamp-grid">
            {% for i in range(1, 11) %}
            <div class="stamp-slot {% if i <= 7 %}stamped{% endif %}">
                {% if i <= 7 %}
                <span class="stamp-mark">불</span>
                {% else %}
                <span class="stamp-number">{{ i }}</span>
                {% endif %}
            </div>
            {% endfor %}
        </div>
        <div class="stamp-status">
            현재 적립 스탬프: <strong>7 / 10개</strong> (3개 더 모으면 치즈불닭 무료 쿠폰)
        </div>
    </div>

    <div class="coupon-box">
        <h4>보유 쿠폰</h4>
        <div class="coupon-item">
            <div class="cp-info">
                <strong>[맵린이 구원팩] 쿨피스 무료 증정 쿠폰</strong>
                <span>유효기간: 2026.12.31까지</span>
            </div>
            <button class="cp-use-btn" onclick="alert('쿨피스 쿠폰이 적용되었습니다 주인님!')">사용</button>
        </div>
    </div>
</div>
{% endblock %}
''',

    "static/css/style.css": '''* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
    font-family: -apple-system, BlinkMacSystemFont, "Apple SD Gothic Neo", "Pretendard", Roboto, sans-serif;
}

body {
    background-color: #121212;
    display: flex;
    justify-content: center;
    min-height: 100vh;
}

/* 모바일 앱 뷰포트 규격 (최대 480px) */
.mobile-container {
    width: 100%;
    max-width: 480px;
    background-color: #1a1a1a;
    color: #f1f1f1;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    position: relative;
    box-shadow: 0 0 25px rgba(0,0,0,0.8);
}

.app-header {
    background-color: #111111;
    padding: 16px 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 2px solid #E62129;
    position: sticky;
    top: 0;
    z-index: 10;
}

.brand-sub {
    font-size: 10px;
    color: #FFA500;
    letter-spacing: 1px;
    display: block;
}

.brand-title {
    font-size: 18px;
    font-weight: 900;
    color: #FFFFFF;
}

.flame-tag {
    background: #E62129;
    font-size: 11px;
    font-weight: bold;
    padding: 4px 8px;
    border-radius: 4px;
    color: #FFFFFF;
}

.content-area {
    flex: 1;
    padding-bottom: 80px; /* 하단 네비게이션 여백 */
    overflow-y: auto;
}

/* 홈 배너 */
.hero-banner {
    background: linear-gradient(135deg, #8B0000 0%, #E62129 100%);
    padding: 28px 20px;
    color: #FFFFFF;
}

.hero-sub {
    font-size: 12px;
    text-transform: uppercase;
    opacity: 0.9;
}

.hero-title {
    font-size: 24px;
    font-weight: 800;
    margin: 8px 0;
    line-height: 1.3;
}

.hero-desc {
    font-size: 13px;
    margin-bottom: 16px;
    opacity: 0.9;
}

.btn-primary {
    display: inline-block;
    background-color: #FFC800;
    color: #111;
    padding: 10px 18px;
    font-weight: 700;
    border-radius: 20px;
    text-decoration: none;
    font-size: 13px;
}

/* 스코빌 미터기 */
.scoville-widget {
    background: #242424;
    margin: 16px 20px;
    padding: 16px;
    border-radius: 12px;
}

.widget-title {
    font-size: 13px;
    color: #bbb;
    margin-bottom: 8px;
}

.meter-bar {
    height: 10px;
    background: #333;
    border-radius: 5px;
    overflow: hidden;
}

.meter-fill {
    height: 100%;
    background: linear-gradient(90deg, #FFA500, #E62129);
}

.meter-label {
    display: flex;
    justify-content: space-between;
    font-size: 12px;
    margin-top: 6px;
    color: #E62129;
}

/* 퀵 그리드 */
.quick-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    margin: 0 20px 20px;
}

.quick-card {
    background: #262626;
    padding: 16px;
    border-radius: 10px;
    text-decoration: none;
    display: flex;
    flex-direction: column;
    border: 1px solid #333;
}

.quick-card.flame-bg {
    border-color: #E62129;
    background: #2a1616;
}

.quick-tag {
    font-size: 10px;
    color: #FFC800;
    font-weight: 700;
}

.quick-name {
    font-size: 14px;
    color: #fff;
    margin-top: 4px;
    font-weight: bold;
}

/* 추천 리스트 */
.recommend-section {
    padding: 0 20px;
}

.sec-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
}

.sec-header h3 {
    font-size: 16px;
    font-weight: 700;
}

.sec-header a {
    font-size: 12px;
    color: #888;
    text-decoration: none;
}

.item-card {
    background: #242424;
    border-radius: 10px;
    padding: 14px;
    margin-bottom: 12px;
    border-left: 4px solid #E62129;
}

.item-badge {
    background: #E62129;
    font-size: 9px;
    padding: 2px 6px;
    border-radius: 3px;
    font-weight: bold;
}

.item-name {
    font-size: 15px;
    margin: 6px 0;
}

.item-scoville {
    font-size: 11px;
    color: #FFA500;
    margin-bottom: 8px;
}

.item-bottom {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.item-price {
    font-weight: 700;
    color: #fff;
}

.cart-btn {
    background: #333;
    border: 1px solid #555;
    color: #fff;
    padding: 6px 12px;
    border-radius: 6px;
    font-size: 12px;
    cursor: pointer;
}

/* 메뉴 서브페이지 */
.category-tabs {
    display: flex;
    gap: 8px;
    padding: 14px 20px;
    background: #191919;
    overflow-x: auto;
    white-space: nowrap;
    border-bottom: 1px solid #333;
}

.category-tabs::-webkit-scrollbar {
    display: none;
}

.tab {
    color: #999;
    text-decoration: none;
    font-size: 13px;
    padding: 6px 14px;
    border-radius: 16px;
    background: #252525;
}

.tab.active {
    background: #E62129;
    color: #fff;
    font-weight: bold;
}

.menu-list {
    padding: 16px 20px;
}

.menu-item-row {
    background: #242424;
    padding: 14px;
    border-radius: 10px;
    margin-bottom: 14px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.menu-badge {
    background: #FFC800;
    color: #111;
    font-size: 9px;
    font-weight: bold;
    padding: 2px 6px;
    border-radius: 3px;
}

.menu-title {
    font-size: 15px;
    margin: 4px 0 2px;
}

.menu-desc {
    font-size: 11px;
    color: #aaa;
    max-width: 250px;
    margin-bottom: 6px;
}

.menu-stat {
    font-size: 11px;
    color: #FF8C00;
    margin-bottom: 4px;
}

.menu-price {
    font-weight: bold;
    font-size: 14px;
}

.order-action-btn {
    background: #E62129;
    color: #fff;
    border: none;
    padding: 10px 14px;
    border-radius: 8px;
    font-weight: bold;
    cursor: pointer;
    font-size: 12px;
}

/* 멤버십 서브페이지 */
.membership-screen {
    padding: 20px;
}

.stamp-card-wrap {
    background: #262626;
    border: 2px solid #E62129;
    border-radius: 14px;
    padding: 18px;
}

.card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.card-no {
    font-size: 11px;
    color: #888;
}

.card-sub {
    font-size: 11px;
    color: #aaa;
    margin: 6px 0 16px;
}

.stamp-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 10px;
    margin-bottom: 14px;
}

.stamp-slot {
    aspect-ratio: 1;
    background: #1b1b1b;
    border: 1px dashed #555;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    color: #666;
}

.stamp-slot.stamped {
    background: #E62129;
    border: none;
    color: #FFC800;
    font-weight: bold;
    font-size: 15px;
    box-shadow: 0 0 8px rgba(230, 33, 41, 0.6);
}

.stamp-status {
    font-size: 12px;
    color: #ccc;
    text-align: center;
}

.coupon-box {
    margin-top: 24px;
}

.coupon-box h4 {
    font-size: 14px;
    margin-bottom: 10px;
}

.coupon-item {
    background: #262626;
    padding: 14px;
    border-radius: 8px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-left: 4px solid #FFC800;
}

.cp-info strong {
    display: block;
    font-size: 13px;
    margin-bottom: 4px;
}

.cp-info span {
    font-size: 11px;
    color: #888;
}

.cp-use-btn {
    background: #FFC800;
    color: #111;
    border: none;
    padding: 8px 12px;
    border-radius: 6px;
    font-weight: bold;
    font-size: 12px;
    cursor: pointer;
}

/* 하단 네비게이션 바 */
.bottom-nav {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 64px;
    background: #111;
    border-top: 1px solid #2a2a2a;
    display: flex;
    justify-content: space-around;
    align-items: center;
    z-index: 10;
}

.nav-item {
    text-decoration: none;
    color: #777;
    display: flex;
    flex-direction: column;
    align-items: center;
    background: none;
    border: none;
    cursor: pointer;
}

.nav-icon {
    font-size: 11px;
    font-weight: 800;
    margin-bottom: 2px;
}

.nav-label {
    font-size: 11px;
}

.nav-item.active {
    color: #E62129;
}

.chat-trigger {
    color: #FFA500;
}

/* 호치 챗봇 모달창 */
.chat-modal {
    position: absolute;
    bottom: 64px;
    left: 0;
    right: 0;
    height: 72%;
    background: #1c1c1c;
    border-top-left-radius: 16px;
    border-top-right-radius: 16px;
    border-top: 2px solid #E62129;
    display: flex;
    flex-direction: column;
    z-index: 20;
    box-shadow: 0 -5px 20px rgba(0,0,0,0.7);
    transition: transform 0.25s ease-in-out;
}

.chat-modal.hidden {
    display: none;
}

.chat-header {
    padding: 12px 16px;
    background: #242424;
    border-top-left-radius: 16px;
    border-top-right-radius: 16px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid #333;
}

.rooster-profile {
    display: flex;
    align-items: center;
    gap: 10px;
}

.rooster-name {
    font-size: 13px;
    font-weight: bold;
    color: #FFF;
}

.rooster-desc {
    font-size: 10px;
    color: #FFA500;
}

.close-btn {
    background: none;
    border: none;
    color: #888;
    font-size: 22px;
    cursor: pointer;
}

.chat-body {
    flex: 1;
    padding: 16px;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 10px;
}

.chat-bubble {
    max-width: 80%;
    padding: 10px 14px;
    border-radius: 12px;
    font-size: 13px;
    line-height: 1.4;
    word-break: break-word;
}

.chat-bubble.bot {
    background: #2d1818;
    border: 1px solid #8B0000;
    color: #fff;
    align-self: flex-start;
    border-bottom-left-radius: 2px;
}

.chat-bubble.user {
    background: #E62129;
    color: #fff;
    align-self: flex-end;
    border-bottom-right-radius: 2px;
}

.chat-input-row {
    padding: 10px 14px;
    display: flex;
    gap: 8px;
    background: #181818;
    border-top: 1px solid #2a2a2a;
}

.chat-input-row input {
    flex: 1;
    background: #2b2b2b;
    border: 1px solid #444;
    color: #fff;
    padding: 10px 12px;
    border-radius: 8px;
    font-size: 13px;
    outline: none;
}

.chat-input-row button {
    background: #E62129;
    color: #fff;
    border: none;
    padding: 0 16px;
    border-radius: 8px;
    font-weight: bold;
    cursor: pointer;
}
''',

    "static/js/main.js": '''document.addEventListener('DOMContentLoaded', () => {
    const openBtn = document.getElementById('open-chat-btn');
    const closeBtn = document.getElementById('close-chat-btn');
    const chatModal = document.getElementById('chat-modal');
    const sendBtn = document.getElementById('chat-send-btn');
    const inputField = document.getElementById('chat-user-input');
    const chatMessages = document.getElementById('chat-messages');

    if (openBtn && chatModal) {
        openBtn.addEventListener('click', () => {
            chatModal.classList.remove('hidden');
            inputField.focus();
        });
    }

    if (closeBtn && chatModal) {
        closeBtn.addEventListener('click', () => {
            chatModal.classList.add('hidden');
        });
    }

    function appendMessage(text, role) {
        const bubble = document.createElement('div');
        bubble.className = `chat-bubble ${role}`;
        bubble.textContent = text;
        chatMessages.appendChild(bubble);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    async function handleSend() {
        const text = inputField.value.trim();
        if (!text) return;

        appendMessage(text, 'user');
        inputField.value = '';

        const tempBotMsg = document.createElement('div');
        tempBotMsg.className = 'chat-bubble bot';
        tempBotMsg.textContent = '호치가 불닭 레시피 사전 뒤지는 중... 꼬꼬!';
        chatMessages.appendChild(tempBotMsg);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: text })
            });
            const data = await response.json();
            tempBotMsg.textContent = data.reply || '오류가 발생했습니다.';
        } catch (err) {
            tempBotMsg.textContent = '네트워크 연결 상태가 화끈하지 못합니다 주인님!';
        }
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    if (sendBtn) {
        sendBtn.addEventListener('click', handleSend);
    }
    if (inputField) {
        inputField.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') handleSend();
        });
    }
});
'''
}

def create_structure():
    # 필요한 디렉토리 생성
    directories = ["templates", "static/css", "static/js"]
    for d in directories:
        os.makedirs(d, exist_ok=True)
        print(f"디렉토리 생성 완료: {d}")

    # 파일 생성
    for path, content in files.items():
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"파일 생성 완료: {path}")

    print("\n[알림] 모든 프로젝트 파일 생성이 완료되었습니다!")

if __name__ == "__main__":
    create_structure()