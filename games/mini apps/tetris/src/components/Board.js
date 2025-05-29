import React from 'react';
import './Board.css';

function Board({ board, currentPiece, gameOver }) {
  const renderBoard = () => {
    const displayBoard = board.map(row => [...row]);

    // Add current piece to the display board
    if (currentPiece) {
      for (let y = 0; y < currentPiece.shape.length; y++) {
        for (let x = 0; x < currentPiece.shape[y].length; x++) {
          if (currentPiece.shape[y][x]) {
            const boardY = currentPiece.position.y + y;
            const boardX = currentPiece.position.x + x;
            if (boardY >= 0 && boardY < board.length && boardX >= 0 && boardX < board[0].length) {
              displayBoard[boardY][boardX] = currentPiece.color;
            }
          }
        }
      }
    }

    return displayBoard;
  };

  return (
    <div className={`board ${gameOver ? 'game-over' : ''}`}>
      {renderBoard().map((row, y) => (
        <div key={y} className="row">
          {row.map((cell, x) => (
            <div
              key={`${y}-${x}`}
              className="cell"
              style={{ backgroundColor: cell || '#1a1a1a' }}
            />
          ))}
        </div>
      ))}
    </div>
  );
}

export default Board; 