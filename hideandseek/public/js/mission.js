// Firebaseの初期化（インポートの代わりに直接SDKのスクリプトを使用）
const firebaseConfig = {
  apiKey: "AIzaSyCQHe6oqqp9dWPLTnbuSevPtH-OM61nmmg",
  authDomain: "hideend-8d9cc.firebaseapp.com",
  projectId: "hideend-8d9cc",
  storageBucket: "hideend-8d9cc.firebasestorage.app",
  messagingSenderId: "73697262710",
  appId: "1:73697262710:web:ba8aa964343f65e11cf357",
  measurementId: "G-4YW1T5E2B6"
};

// Firebase初期化
firebase.initializeApp(firebaseConfig);
const db = firebase.firestore();

let currentMission = ""; // 初期化
let currentMissionBarId = ""; // 初期化

// ポップアップを表示する関数
function showPopup(missionName, missionBarId) {
  currentMission = missionName;
  currentMissionBarId = missionBarId;
  document.getElementById('name-popup').style.display = 'block';
}

// 名前をFirebaseに保存する関数
async function saveName() {
  const nameInput = document.getElementById('name-input');
  const name = nameInput.value;

  if (name) {
    try {
      // Firestoreに名前を保存
      await db.collection("missions").doc(currentMission).set({ name: name });

      // 保存後、ポップアップを非表示にして表示を更新
      document.getElementById('name-popup').style.display = 'none';
      nameInput.value = ''; // 入力フィールドをクリア

      // 対応するミッションバーに名前を表示
      document.getElementById(currentMissionBarId).innerText = name;

    } catch (error) {
      console.error('Error saving name: ', error);
    }
  }
}

// Firebaseから名前を取得して表示する関数
async function loadName(missionName, missionBarId) {
  try {
    const docRef = db.collection("missions").doc(missionName);
    const docSnap = await docRef.get();

    if (docSnap.exists) {
      const name = docSnap.data().name;
      document.getElementById(missionBarId).innerText = name;
    }
  } catch (error) {
    console.error('Error loading name: ', error);
  }
}

// ページ読み込み時に各ミッションの名前をロード
window.onload = function() {
  loadName('ボタンを1回押せ', 'mission-bar-1');
  loadName('色を当てろ', 'mission-bar-2');
  loadName('振れ！', 'mission-bar-3');
};

// グローバルスコープに公開
window.showPopup = showPopup;
window.saveName = saveName;
