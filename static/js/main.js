document.addEventListener('DOMContentLoaded', () => {
    // 1. 장바구니 상태 관리
    let cart = JSON.parse(localStorage.getItem('buldak_cart') || '[]');

    const cartHeaderBtn = document.getElementById('cart-header-btn');
    const navCartBtn = document.getElementById('nav-cart-btn');
    const cartModal = document.getElementById('cart-modal');
    const closeCartBtn = document.getElementById('close-cart-btn');
    const cartCountBadge = document.getElementById('cart-count-badge');
    const cartItemsWrap = document.getElementById('cart-items-wrap');
    const cartTotalPrice = document.getElementById('cart-total-price');
    const checkoutBtn = document.getElementById('cart-checkout-btn');

    function updateCartUI() {
        const totalCount = cart.reduce((sum, item) => sum + item.qty, 0);
        if (cartCountBadge) cartCountBadge.textContent = totalCount;

        if (!cartItemsWrap) return;
        if (cart.length === 0) {
            cartItemsWrap.innerHTML = '<p class="empty-cart-msg">장바구니가 비어 있습니다 주인님!</p>';
            if (cartTotalPrice) cartTotalPrice.textContent = '0원';
            return;
        }

        let total = 0;
        cartItemsWrap.innerHTML = '';
        cart.forEach((item, index) => {
            total += item.price * item.qty;
            const row = document.createElement('div');
            row.className = 'cart-row';
            row.innerHTML = `
                <div>
                    <div class="cart-item-title">${item.name}</div>
                    <div class="cart-item-price">${(item.price * item.qty).toLocaleString()}원</div>
                </div>
                <div class="qty-control">
                    <button class="qty-btn" onclick="changeQty(${index}, -1)">-</button>
                    <span>${item.qty}</span>
                    <button class="qty-btn" onclick="changeQty(${index}, 1)">+</button>
                </div>
            `;
            cartItemsWrap.appendChild(row);
        });

        if (cartTotalPrice) cartTotalPrice.textContent = total.toLocaleString() + '원';
        localStorage.setItem('buldak_cart', JSON.stringify(cart));
    }

    window.changeQty = function(index, delta) {
        cart[index].qty += delta;
        if (cart[index].qty <= 0) cart.splice(index, 1);
        updateCartUI();
    };

    function addToCart(item) {
        const found = cart.find(x => x.id === item.id);
        if (found) {
            found.qty += 1;
        } else {
            cart.push({ ...item, qty: 1 });
        }
        updateCartUI();
        alert(`${item.name}이(가) 장바구니에 담겼습니다 주인님!`);
    }

    // 담기 버튼 바인딩
    document.querySelectorAll('.direct-add-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const item = {
                id: btn.dataset.id,
                name: btn.dataset.name,
                price: parseInt(btn.dataset.price, 10)
            };
            addToCart(item);
        });
    });

    if (cartHeaderBtn) cartHeaderBtn.addEventListener('click', () => cartModal.classList.remove('hidden'));
    if (navCartBtn) navCartBtn.addEventListener('click', () => cartModal.classList.remove('hidden'));
    if (closeCartBtn) closeCartBtn.addEventListener('click', () => cartModal.classList.add('hidden'));

    if (checkoutBtn) {
        checkoutBtn.addEventListener('click', () => {
            if (cart.length === 0) {
                alert('장바구니가 비어 있습니다 주인님!');
                return;
            }
            alert('주문이 접수되었습니다! 호치가 매콤하게 조리를 시작합니다 꼬꼬!');
            cart = [];
            updateCartUI();
            cartModal.classList.add('hidden');
        });
    }

    updateCartUI();

    // 2. 맵부심 지수 실시간 슬라이더 로직
    const rangeInput = document.getElementById('scoville-range');
    const rangeVal = document.getElementById('current-range-val');
    const matchTitle = document.getElementById('match-title');
    const matchDesc = document.getElementById('match-desc');
    const matchPrice = document.getElementById('match-price');
    const matchAddBtn = document.getElementById('match-add-cart-btn');

    let currentRecommendProduct = {
        id: "b01",
        name: "불닭볶음면 (오리지널)",
        price: 1800
    };

    if (rangeInput) {
        rangeInput.addEventListener('input', (e) => {
            const val = parseInt(e.target.value, 10);
            rangeVal.textContent = `${val.toLocaleString()} SHU`;

            if (val <= 2300) {
                currentRecommendProduct = { id: "b05", name: "로제 불닭볶음면", price: 2100 };
                matchTitle.textContent = "로제 불닭볶음면 (2,100 SHU)";
                matchDesc.textContent = "크리미하고 부드러운 매운맛! 맵린이도 부담 없이 즐기는 로제 조합입니다.";
            } else if (val <= 2800) {
                currentRecommendProduct = { id: "b03", name: "까르보 불닭볶음면", price: 2000 };
                matchTitle.textContent = "까르보 불닭볶음면 (2,400 SHU)";
                matchDesc.textContent = "가장 사랑받는 베스트셀러! 고소한 크림치즈 분말이 일품입니다.";
            } else if (val <= 3800) {
                currentRecommendProduct = { id: "b07", name: "야키소바 불닭볶음면", price: 2200 };
                matchTitle.textContent = "야키소바 불닭볶음면 (3,000 SHU)";
                matchDesc.textContent = "단짠단짠 감칠맛과 불닭의 매콤함이 어우러진 특색 메뉴입니다.";
            } else if (val <= 6500) {
                currentRecommendProduct = { id: "b01", name: "불닭볶음면 (오리지널)", price: 1800 };
                matchTitle.textContent = "불닭볶음면 오리지널 (4,404 SHU)";
                matchDesc.textContent = "전설의 시작! 화끈한 오리지널 불닭볶음면의 정석입니다.";
            } else {
                currentRecommendProduct = { id: "b02", name: "핵불닭볶음면 (2X Spicy)", price: 2000 };
                matchTitle.textContent = "핵불닭볶음면 (10,000 SHU)";
                matchDesc.textContent = "원조 불닭의 2배! 눈물 쏙 빠지는 매운맛 최강자 챌린지 메뉴입니다.";
            }
            matchPrice.textContent = `${currentRecommendProduct.price.toLocaleString()}원`;
        });

        if (matchAddBtn) {
            matchAddBtn.addEventListener('click', () => {
                addToCart(currentRecommendProduct);
            });
        }
    }

    // 3. 호치 챗봇 열기/닫기/메시지 송수신
    const openChatBtn = document.getElementById('open-chat-btn');
    const closeChatBtn = document.getElementById('close-chat-btn');
    const chatModal = document.getElementById('chat-modal');
    const sendBtn = document.getElementById('chat-send-btn');
    const inputField = document.getElementById('chat-user-input');
    const chatMessages = document.getElementById('chat-messages');

    if (openChatBtn && chatModal) {
        openChatBtn.addEventListener('click', () => {
            chatModal.classList.remove('hidden');
            if (inputField) inputField.focus();
        });
    }

    if (closeChatBtn && chatModal) {
        closeChatBtn.addEventListener('click', () => {
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
        tempBotMsg.textContent = '호치가 매운 비법 노트 뒤지는 중... 꼬꼬!';
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
            tempBotMsg.textContent = '네트워크 연결이 지연되고 있습니다 주인님!';
        }
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    if (sendBtn) sendBtn.addEventListener('click', handleSend);
    if (inputField) {
        inputField.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') handleSend();
        });
    }
});