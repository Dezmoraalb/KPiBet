import useTelegram from "./Hooks/useTelegram";
import { useEffect } from 'react';

export default function Board({
    squares,
    status,
    winningLine,
    onSquareClick,
    onReset,
    userPoints,
    botPoints,
    userScore
  }) {
    
    const {tg} = useTelegram();
    useEffect(() => {
      tg.ready();
    });
  
    return (
      <div className='game'>
        <div className={`status ${status.includes('Переможець') ? 'status--win' : ''}`}>
          {status}
        </div>

        <div className='pointsStatus'>
          Набрано очків:
          <div>{userScore}</div>
        </div>
  
        <div className='board-row'>
          <Square value={squares[0]} onSquareClick={() => onSquareClick(0)} isWining={winningLine.includes(0)} x = {squares[0] ==='X'}/>
          <Square value={squares[1]} onSquareClick={() => onSquareClick(1)} isWining={winningLine.includes(1)} x = {squares[1] ==='X'}/>
          <Square value={squares[2]} onSquareClick={() => onSquareClick(2)} isWining={winningLine.includes(2)} x = {squares[2] ==='X'}/>
        </div>
  
        <div className='board-row'>
          <Square value={squares[3]} onSquareClick={() => onSquareClick(3)} isWining={winningLine.includes(3)} x = {squares[3] ==='X'}/>
          <Square value={squares[4]} onSquareClick={() => onSquareClick(4)} isWining={winningLine.includes(4)} x = {squares[4] ==='X'}/>
          <Square value={squares[5]} onSquareClick={() => onSquareClick(5)} isWining={winningLine.includes(5)} x = {squares[5] ==='X'}/>
        </div>
  
        <div className='board-row'>
          <Square value={squares[6]} onSquareClick={() => onSquareClick(6)} isWining={winningLine.includes(6)} x = {squares[6] ==='X'}/>
          <Square value={squares[7]} onSquareClick={() => onSquareClick(7)} isWining={winningLine.includes(7)} x = {squares[7] ==='X'}/>
          <Square value={squares[8]} onSquareClick={() => onSquareClick(8)} isWining={winningLine.includes(8)} x = {squares[8] ==='X'}/>
        </div>

        <div className='pointsStatus'>
          <div className='pointsStatus--title'>
            <div>Виграші</div>
          </div>

          <div className='pointsStatus--row'>
              <div>Комп'ютер</div>
              <div>Користувач</div>
          </div>

          <div className='pointsStatus--row cent'>
              <div>{botPoints}</div>
              <div>{userPoints}</div>
          </div>
        </div>
  
        <button className='reset' onClick={onReset}>
          Очистити поле
        </button>
      </div>
    );
  }

  function Square({ value, onSquareClick, isWining, x}) {
    return <button className={
        `square ${isWining ? x ? 'square--winX' : 'square--winO' : x ? 'square--x' : 'square--o'}`
    } onClick={onSquareClick}>{value && <span>{value}</span>}</button>
  }