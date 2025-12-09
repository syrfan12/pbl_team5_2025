document.addEventListener('DOMContentLoaded', () => {
    // 開発用ダミー起動
    liff.init({ liffId: '' })
    .then(() => { initializeApp(); })
    .catch((err) => { initializeApp(); });
});

function initializeApp() {
    displayLatestInfo();
    displayHistory();
}

// --- 1. 最新情報を表示 ---
function displayLatestInfo() {
    // ダミーデータ：最新の状態
    const latestData = {
        timestamp: '2025/11/27 10:30',
        imgUrl: 'https://images.unsplash.com/photo-1520412099551-62b6bafeb5bb?q=80&w=600&auto=format&fit=crop',
        result: '正常',
        isHealthy: true,
        lastWatering: '本日 08:00 (たっぷり)'
    };

    // DOM要素へ反映
    document.getElementById('latest-timestamp').textContent = latestData.timestamp;
    document.getElementById('latest-img').src = latestData.imgUrl;
    
    const resultEl = document.getElementById('latest-result');
    resultEl.textContent = latestData.result;
    resultEl.className = 'badge ' + (latestData.isHealthy ? 'healthy' : 'sick');

    document.getElementById('latest-result-text').textContent = latestData.result;
    document.getElementById('latest-water').textContent = latestData.lastWatering;
}

// --- 2. 過去の記録を表示 ---
function displayHistory() {
    // ダミーデータ：過去の履歴配列（写真と結果を含む）
    const historyData = [
        { 
            date: '2025/11/26 14:00', 
            imgUrl: 'https://images.unsplash.com/photo-1599598425947-32103f6f1946?q=80&w=200&auto=format&fit=crop', 
            result: '正常' 
        },
        { 
            date: '2025/11/25 10:00', 
            imgUrl: 'https://images.unsplash.com/photo-1459156212016-c812468e2115?q=80&w=200&auto=format&fit=crop', 
            result: '乾燥気味' 
        },
        { 
            date: '2025/11/24 09:30', 
            imgUrl: 'https://images.unsplash.com/photo-1520412099551-62b6bafeb5bb?q=80&w=200&auto=format&fit=crop', 
            result: '正常' 
        },
        { 
            date: '2025/11/23 16:45', 
            imgUrl: 'https://images.unsplash.com/photo-1599598425947-32103f6f1946?q=80&w=200&auto=format&fit=crop', 
            result: '正常' 
        }
    ];

    const listEl = document.getElementById('history-list');
    listEl.innerHTML = '';

    historyData.forEach(item => {
        const li = document.createElement('li');
        li.innerHTML = `
            <div class="history-item-container">
                <span class="history-date">${item.date}</span>
                <div class="history-content">
                    <img src="${item.imgUrl}" alt="記録画像" class="history-thumb">
                    <span class="history-result">${item.result}</span>
                </div>
            </div>
        `;
        listEl.appendChild(li);
    });
}