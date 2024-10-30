  // Import the functions you need from the SDKs you need
  import { initializeApp } from "https://www.gstatic.com/firebasejs/11.0.1/firebase-app.js";
  import { getAnalytics } from "https://www.gstatic.com/firebasejs/11.0.1/firebase-analytics.js";
  // TODO: Add SDKs for Firebase products that you want to use
  // https://firebase.google.com/docs/web/setup#available-libraries

  // Your web app's Firebase configuration
  // For Firebase JS SDK v7.20.0 and later, measurementId is optional
  const firebaseConfig = {
    apiKey: "AIzaSyCqmozU0o6QFsIHET33KVVazf2ah67BjaY",
    authDomain: "hideandseek-main.firebaseapp.com",
    projectId: "hideandseek-main",
    storageBucket: "hideandseek-main.appspot.com",
    messagingSenderId: "735377376955",
    appId: "1:735377376955:web:c5078194804827d3facb9e",
    measurementId: "G-2EFSXLX3BP"
  };

  // Initialize Firebase
  const app = initializeApp(firebaseConfig);
  const analytics = getAnalytics(app);