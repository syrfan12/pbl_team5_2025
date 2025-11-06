document.addEventListener('DOMContentLoaded', () => {
  liff.init({
    liffId: '2008382062-jBBleG0y' // ★★★ここに取得したLIFF IDを入力★★★
    // liffId: 'DUMMY_ID' // ★★★ここに取得したLIFF IDを入力★★★
  })
  .then(() => {
    console.log('LIFF init succeeded.');
    initializeApp();
  })
  .catch((err) => console.error('LIFF init failed:', err));
});

function initializeApp() {
  if (!liff.isLoggedIn()) {
    liff.login();
  } else {
    // ★ダミーデータを表示
    displayDummyData();
  }
}

function displayDummyData() {
  document.getElementById('temp').textContent = '25.5';
  document.getElementById('humidity').textContent = '60';
}
