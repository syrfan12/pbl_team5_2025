document.addEventListener('DOMContentLoaded', () => {
    liff.init({
      // liffId: '2008382062-jBBleG0y' // ★★★ここに取得したLIFF IDを入力★★★
    })
    .then(() => {
      console.log('LIFF init succeeded.');
      initializeApp();
    })
    .catch((err) => console.error('LIFF init failed:', err));
  });
  
  function initializeApp() {
    // 開発中はログインチェックをスキップしたい場合はここをコメントアウト
    if (!liff.isLoggedIn()) {
       liff.login();
    } else {
      // ★各ダミーデータ表示関数を呼び出し
      displaySensorData(); // 温度・湿度
      displayDiagnosisData(); // 診断結果
      displayWateringHistory(); // 水やり記録
    }
  }
  
  // --- 1. センサーデータ表示 ---
  function displaySensorData() {
    // 将来はここでFirebaseから fetch する
    const dummySensor = { temp: 25.5, humidity: 60 };
  
    document.getElementById('temp').textContent = dummySensor.temp;
    document.getElementById('humidity').textContent = dummySensor.humidity;
  }
  
  // --- 2. 診断結果表示 ---
  function displayDiagnosisData() {
    // ダミーの診断データ
    const dummyDiagnosis = {
      // プレースホルダー画像サービスを使用（実際はFirebase StorageのURLなど）
      imageUrl: 'https://placehold.jp/300x200.png?text=Plant+Image', 
      result: 'うどんこ病の疑い', // または '正常'
      isHealthy: false, // 正常なら true, 病気なら false
      confidence: 89.5,
      date: '2025/11/18 14:30'
    };
  
    const imgEl = document.getElementById('plant-img');
    const resultEl = document.getElementById('diagnosis-result');
    
    imgEl.src = dummyDiagnosis.imageUrl;
    resultEl.textContent = dummyDiagnosis.result;
    
    // 病気かどうかで色を変えるクラスを付与
    resultEl.className = 'badge ' + (dummyDiagnosis.isHealthy ? 'healthy' : 'sick');
  
    document.getElementById('diagnosis-confidence').textContent = dummyDiagnosis.confidence;
    document.getElementById('diagnosis-date').textContent = dummyDiagnosis.date;
  }
  
  // --- 3. 水やり履歴表示 ---
  function displayWateringHistory() {
    // ダミーの履歴データ（配列）
    const dummyHistory = [
      { date: '2025/11/18 08:00', amount: 'たっぷり' },
      { date: '2025/11/15 07:30', amount: '普通' },
      { date: '2025/11/12 18:00', amount: '少なめ' },
      { date: '2025/11/10 08:15', amount: 'たっぷり' }
    ];
  
    const listEl = document.getElementById('watering-list');
    listEl.innerHTML = ''; // 一旦クリア
  
    // 配列をループしてリスト項目を作成
    dummyHistory.forEach(item => {
      const li = document.createElement('li');
      li.innerHTML = `
        <span>${item.date}</span>
        <span>${item.amount}</span>
      `;
      listEl.appendChild(li);
    });
  }