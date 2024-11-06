// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyCQHe6oqqp9dWPLTnbuSevPtH-OM61nmmg",
  authDomain: "hideend-8d9cc.firebaseapp.com",
  projectId: "hideend-8d9cc",
  storageBucket: "hideend-8d9cc.firebasestorage.app",
  messagingSenderId: "73697262710",
  appId: "1:73697262710:web:ba8aa964343f65e11cf357",
  measurementId: "G-4YW1T5E2B6"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);