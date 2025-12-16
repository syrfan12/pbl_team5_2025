// 1. Firebase SDKのインポート (CDN経由)
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-app.js";
import { getFirestore, collection, query, orderBy, limit, getDocs } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-firestore.js";

// 2. Firebaseの設定 (コンソールからコピーした内容を入れてください)
  const firebaseConfig = {
    apiKey: "",
    authDomain: "",
    projectId: "",
    storageBucket: "",
    messagingSenderId: "",
    appId: ""
  };

// 3. 初期化
const app = initializeApp(firebaseConfig);
const db = getFirestore(app);

// 4. アプリ起動処理
document.addEventListener('DOMContentLoaded', () => {
    // LIFF初期化（必要であればIDを入れてください）
    liff.init({ liffId: '' })
        .then(() => { startApp(); })
        .catch((err) => { 
            console.log('LIFF init failed', err);
            startApp(); 
        });
});

function startApp() {
    fetchAndDisplayData();
}

// main.js の fetchAndDisplayData 関数をこれに書き換え

async function fetchAndDisplayData() {
    // スクリーンショットの構造に合わせたパスを指定
    // plants > pbl-team5-app > readings
    const COLLECTION_REF = collection(db, "plants", "pbl-team5-app", "readings");

    try {
        // timestampは文字列ですが、ISO形式(YYYY-MM-DD...)なので文字順でソート可能です
        const q = query(
            COLLECTION_REF,
            orderBy('timestamp', 'desc'), 
            limit(10)
        );

        const querySnapshot = await getDocs(q);
        const dataList = [];

        querySnapshot.forEach((doc) => {
            const data = doc.data();
            
            // 1. 日付の変換（文字列 "2025-12-16T..." を読みやすい形に）
            let timeStr = '--/-- --:--';
            if (data.timestamp) {
                const d = new Date(data.timestamp);
                timeStr = `${d.getFullYear()}/${d.getMonth()+1}/${d.getDate()} ${d.getHours()}:${String(d.getMinutes()).padStart(2, '0')}`;
            }

            // 2. ステータス判定（土壌水分量から適当に判定するロジック）
            // ※430という値が「乾いている」のか「濡れている」のかはセンサーによりますが、
            //   一旦、値をそのまま表示するようにしています。
            let statusText = `水分: ${data.soil_moisture}`;
            let isHealthy = true;

            // 仮のロジック: 極端な値なら警告にする（必要に応じて調整してください）
            // if (data.soil_moisture < 200) { statusText = "乾燥"; isHealthy = false; }

            dataList.push({
                id: doc.id,
                date: timeStr,
                // image_url が null の場合はダミー画像を表示
                imgUrl: data.image_url ? data.image_url : 'https://placehold.jp/150x150.png?text=NoImage',
                result: statusText,
                isHealthy: isHealthy,
                // 気温や湿度も表示したければここに追加できます
                lastWatering: `気温 ${data.temperature}℃` 
            });
        });

        if (dataList.length > 0) {
            updateLatestDisplay(dataList[0]);
            updateHistoryDisplay(dataList);
        } else {
            console.log("データが見つかりませんでした");
            document.getElementById('latest-result-text').textContent = "データなし";
        }

    } catch (e) {
        console.error("データ取得エラー: ", e);
        // エラー内容を画面に出すとデバッグしやすいです
        alert(`読み込み失敗: ${e.message}`);
    }
}

// --- UI反映関数（ロジックは以前と同じ） ---

function updateLatestDisplay(latestData) {
    document.getElementById('latest-timestamp').textContent = latestData.date;
    document.getElementById('latest-img').src = latestData.imgUrl;
    
    const resultEl = document.getElementById('latest-result');
    resultEl.textContent = latestData.result;
    // クラスをリセットしてから追加
    resultEl.className = 'badge ' + (latestData.isHealthy ? 'healthy' : 'sick');

    document.getElementById('latest-result-text').textContent = latestData.result;
    // lastWateringフィールドがDBになければ「記録なし」などにする
    document.getElementById('latest-water').textContent = latestData.lastWatering;
}

function updateHistoryDisplay(historyData) {
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