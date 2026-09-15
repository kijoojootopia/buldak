import os
import re
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, unquote

URL = "https://buldak.com/kr/product/"
APP_FILE = "app.py"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def fetch_buldak_products():
    print("buldak.com 크롤링을 시작합니다...")
    res = requests.get(URL, headers=HEADERS)
    res.encoding = 'utf-8'
    
    soup = BeautifulSoup(res.text, "html.parser")
    items = []
    seen_names = set()

    # Next.js 내부 이미지 및 상품 태그 순회
    imgs = soup.find_all("img")
    
    idx = 1
    for img in imgs:
        src = img.get("src") or img.get("data-src") or ""
        alt = img.get("alt", "").strip()

        # 불닭 제품명 필터링 (로고, 배너 제외)
        if not alt or "logo" in alt.lower() or "banner" in alt.lower():
            continue
            
        # Next.js의 /_next/image?url= 파라미터에서 원본 이미지 추출
        if "/_next/image" in src and "url=" in src:
            match = re.search(r"url=([^&]+)", src)
            if match:
                src = unquote(match.group(1))

        full_img_url = urljoin(URL, src)

        # 중복 제품명 제거
        clean_name = re.sub(r'[\r\n\t]+', ' ', alt).strip()
        if clean_name in seen_names or len(clean_name) < 2:
            continue
            
        seen_names.add(clean_name)

        # 맵기 및 스코빌 기본 추정치 할당
        scoville = 4404
        spicy_level = 4
        category = "classic"

        if "핵" in clean_name or "2X" in clean_name or "3X" in clean_name:
            scoville = 10000
            spicy_level = 5
            category = "challenge"
        elif "까르보" in clean_name or "크림" in clean_name or "치즈" in clean_name or "로제" in clean_name:
            scoville = 2400
            spicy_level = 2
            category = "creamy"
        elif "야키소바" in clean_name or "하바네로" in clean_name or "마라" in clean_name:
            scoville = 3200
            spicy_level = 3
            category = "special"
        elif "소스" in clean_name:
            scoville = 4404
            spicy_level = 4
            category = "source"

        items.append({
            "id": f"b{str(idx).zfill(2)}",
            "name": clean_name,
            "category": category,
            "spicy_level": spicy_level,
            "scoville": scoville,
            "scoville_text": f"{scoville:,} SHU",
            "price": 1800 if category != "source" else 4500,
            "desc": f"화끈한 삼양 불닭 공식 제품: {clean_name}",
            "badge": "HOT",
            "img": full_img_url
        })
        idx += 1

    # 웹 크롤링 실패 대비 기본값 방어
    if not items:
        print("정적 태그에서 항목을 찾지 못해 기본 세트로 대체 구성합니다.")
        return None

    print(f"총 {len(items)}개의 공식 불닭 제품 및 이미지 수집 완료!")
    return items

def update_app_py(products):
    if not products or not os.path.exists(APP_FILE):
        print("app.py 파일을 찾을 수 없거나 제품 데이터가 비어 있습니다.")
        return

    with open(APP_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # json 포맷으로 보기 좋게 딕셔너리 리스트 생성
    formatted_menu = "MENU_ITEMS = " + json.dumps(products, ensure_ascii=False, indent=4)

    # MENU_ITEMS = [ ... ] 정규식으로 치환
    pattern = r"MENU_ITEMS\s*=\s*\[.*?\](?=\n\n|\nHOTCHI_PROMPT)"
    
    if re.search(pattern, content, re.DOTALL):
        new_content = re.sub(pattern, formatted_menu, content, flags=re.DOTALL)
        with open(APP_FILE, "w", encoding="utf-8") as f:
            f.write(new_content)
        print("app.py의 MENU_ITEMS가 자동으로 성공적으로 업데이트되었습니다!")
    else:
        print("경고: app.py 내에서 MENU_ITEMS 패턴을 찾지 못했습니다. 수동 확인이 필요합니다.")

if __name__ == "__main__":
    products = fetch_buldak_products()
    if products:
        update_app_py(products)