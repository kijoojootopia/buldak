import requests
from bs4 import BeautifulSoup
import json

url = "https://buldak.com/kr/product/"
headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1"
}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

images = soup.find_all('img')
found_products = []

for img in images:
    src = img.get('src') or img.get('data-src')
    alt = img.get('alt', '').strip()
    
    # 불닭 제품 이미지 필터링
    if src and ('product' in src or 'upload' in src or alt):
        if not src.startswith('http'):
            src = "https://buldak.com" + src
        found_products.append({"name": alt, "img_url": src})

print(f"추출된 이미지 개수: {len(found_products)}")
for p in found_products[:10]:
    print(p)