import React from 'react'
import api from './services/api.js'
import './App.css';

function App() {
  return (
    <h1>
      {api.get("/")}
    </h1>
  );
}

export default App;
