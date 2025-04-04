import { useState } from 'react';
import { useEffect } from 'react';
import { useCallback } from 'react';

import Board from './Board';
import useTelegram from './Hooks/useTelegram';
// import 

export default function Game() {
  const {tg, WebAppMainButton} = useTelegram();
  const [squares, setSquares] = useState(Array(9).fill(null));
  const [xIsNext, setXIsNext] = useState(true);
  const [status, setStatus] = useState('');
  const [turn, setTurn] = useState(true);
  const [userPoints, setUserPoints] = useState(0);
  const [botPoints, setBotPoints] = useState(0);
  const [userScore, setUserScore] = useState(0);

  const winner = calculateWinner(squares)?.win;
  const winningLine = calculateWinner(squares)?.line || [];
  const isDraw = calculateWinner(squares);

  useEffect(() => {
    if (isDraw === 1) {
      setStatus("Нічия!");
    } else {
      setStatus(winner ? "Переможець: " + winner : "Зараз ходять: " + (xIsNext ? "X" : "O"));
    }
    if(winner === 'X'){
      setUserPoints(prev => prev+1);
      setUserScore(prev => prev+5);
    }
    else if(winner === 'O'){
      setBotPoints(prev => prev+1);
      if(userScore > 10){
        setUserScore(prev => prev-10);
      }
    }
  }, [squares, xIsNext]);

  function handleClick(i) {
    if (squares[i] || calculateWinner(squares) || !turn) return;
    const nextSquares = squares.slice();
    nextSquares[i] = 'X';
    setSquares(nextSquares);
    setXIsNext(!xIsNext);

    if(!calculateWinner(nextSquares) && isDraw !== 1){
      setTurn (false);
      const botSquares = nextSquares.slice();
      setTimeout(() => botMoves(botSquares), 1000);
      setTimeout(() => setTurn(true), 1000);
    }
  }
  
  function botMoves(botSquare){
    const turn = [0, 2, 6, 8];
    const filled = turn.every(index => botSquare[index] !== null);
    if(botSquare[4] === null){
      botSquare[4] = 'O';
      setSquares(botSquare);
      setXIsNext(true); 
    }
    else{
      if(filled){
        let rnd = Math.floor(Math.random() * 9);
        while(botSquare[rnd] !== null){
          rnd = Math.floor(Math.random() * 9);
        }
        botSquare[rnd] = 'O';
        setSquares(botSquare);
        setXIsNext(true);
      }
      else{
        let rnd = Math.floor(Math.random() * turn.length);
        while(botSquare[turn[rnd]] !== null){
          rnd = Math.floor(Math.random() * turn.length);
        }
        botSquare[turn[rnd]] = 'O';
        setSquares(botSquare);
        setXIsNext(true);
      }
    }
  }

  function calculateWinner(squares) {
    const lines = [
      [0, 1, 2], 
      [3, 4, 5], 
      [6, 7, 8],
      [0, 3, 6], 
      [1, 4, 7], 
      [2, 5, 8],
      [0, 4, 8], 
      [2, 4, 6]
    ];

    for (let i = 0; i < lines.length; i++) {
      const [a, b, c] = lines[i];
      if (squares[a] && squares[a] === squares[b] && squares[a] === squares[c]) {
        return { win: squares[a], line: [a, b, c],  };
      }
    }

    if (squares.every(square => square !== null)) {
      return 1;
    }

    return null;
  }

  function reset() {
    if(winner || isDraw === 1){
      setXIsNext(true);
      setSquares(Array(9).fill(null));
    }
  }

  useEffect(() => {
    WebAppMainButton.setText(`Your count: ${userScore}`);
    WebAppMainButton.show();
  }, [WebAppMainButton, userScore]);

  const onSendData = useCallback(() => {
      tg.sendData(JSON.stringify({playerCount : userScore}));
  }, [tg, userScore]);

  useEffect(() => {
      tg.onEvent('mainButtonClicked', onSendData);
      return () => {
          tg.offEvent('mainButtonClicked', onSendData);
      }
  }, [tg, onSendData])


  return (
    <Board
      squares={squares}
      status={status}
      winningLine={winningLine}
      onSquareClick={handleClick}
      onReset={reset}
      userPoints={userPoints}
      botPoints={botPoints}
      userScore={userScore}
    />
  );
}