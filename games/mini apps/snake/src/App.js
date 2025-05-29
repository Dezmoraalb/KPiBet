import React, { useEffect } from 'react';
import SnakeGame from './components/SnakeGame';
import useTelegram from './hooks/useTelegram';
import './App.css';

function App() {
  const {tg} = useTelegram();
  useEffect(() => {
    tg.ready();
  });
  return (
    <div className="App">
      <SnakeGame />
    </div>
  );
}

export default App;
