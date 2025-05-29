import React, { useState, useEffect, useCallback } from 'react';
import Board from './Board';
import './Game.css';
import useTelegram from '../hooks/useTelegram';

// Constants
const BOARD_WIDTH = 10;
const BOARD_HEIGHT = 20;
const INITIAL_SPEED = 1000; // milliseconds
const SPEED_INCREASE_INTERVAL = 30000; // 30 seconds
const SPEED_INCREASE_AMOUNT = 100; // milliseconds

// Scoring system
const SCORE_POINTS = {
  SINGLE: 100,
  DOUBLE: 300,
  TRIPLE: 500,
  TETRIS: 800,
  SOFT_DROP: 1,
  HARD_DROP: 2
};

// Tetromino shapes
const TETROMINOES = {
  I: {
    shape: [
      [0, 0, 0, 0],
      [1, 1, 1, 1],
      [0, 0, 0, 0],
      [0, 0, 0, 0]
    ],
    color: '#00f0f0'
  },
  O: {
    shape: [
      [1, 1],
      [1, 1]
    ],
    color: '#f0f000'
  },
  T: {
    shape: [
      [0, 1, 0],
      [1, 1, 1],
      [0, 0, 0]
    ],
    color: '#a000f0'
  },
  S: {
    shape: [
      [0, 1, 1],
      [1, 1, 0],
      [0, 0, 0]
    ],
    color: '#00f000'
  },
  Z: {
    shape: [
      [1, 1, 0],
      [0, 1, 1],
      [0, 0, 0]
    ],
    color: '#f00000'
  },
  J: {
    shape: [
      [1, 0, 0],
      [1, 1, 1],
      [0, 0, 0]
    ],
    color: '#0000f0'
  },
  L: {
    shape: [
      [0, 0, 1],
      [1, 1, 1],
      [0, 0, 0]
    ],
    color: '#f0a000'
  }
};

function Game() {
  const [board, setBoard] = useState(createEmptyBoard());
  const [currentPiece, setCurrentPiece] = useState(null);
  const [gameOver, setGameOver] = useState(false);
  const [score, setScore] = useState(0);
  const [level, setLevel] = useState(1);
  const [linesCleared, setLinesCleared] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentSpeed, setCurrentSpeed] = useState(INITIAL_SPEED);
  const [isMobile, setIsMobile] = useState(window.innerWidth <= 768);
  const { WebAppMainButton, tg } = useTelegram();
  WebAppMainButton.setText(`Exit`);
  WebAppMainButton.show();

  const onSendData = useCallback(() => {
      tg.sendData(JSON.stringify({playerCount : score}));
  }, [tg, score]);

  useEffect(() => {
      tg.onEvent('mainButtonClicked', onSendData);
      return () => {
          tg.offEvent('mainButtonClicked', onSendData);
      }
  }, [tg, onSendData]);

  // Create empty board
  function createEmptyBoard() {
    return Array(BOARD_HEIGHT).fill().map(() => Array(BOARD_WIDTH).fill(0));
  }

  // Get random tetromino
  function getRandomTetromino() {
    const pieces = Object.keys(TETROMINOES);
    const randomPiece = pieces[Math.floor(Math.random() * pieces.length)];
    return {
      ...TETROMINOES[randomPiece],
      position: { x: Math.floor(BOARD_WIDTH / 2) - 1, y: 0 }
    };
  }

  // Check if move is valid
  const isValidMove = useCallback((shape, position) => {
    for (let y = 0; y < shape.length; y++) {
      for (let x = 0; x < shape[y].length; x++) {
        if (shape[y][x]) {
          const boardX = position.x + x;
          const boardY = position.y + y;

          if (
            boardX < 0 ||
            boardX >= BOARD_WIDTH ||
            boardY >= BOARD_HEIGHT ||
            (boardY >= 0 && board[boardY][boardX])
          ) {
            return false;
          }
        }
      }
    }
    return true;
  }, [board]);

  // Calculate score based on lines cleared
  const calculateScore = useCallback((lines) => {
    let points = 0;
    switch (lines) {
      case 1:
        points = SCORE_POINTS.SINGLE;
        break;
      case 2:
        points = SCORE_POINTS.DOUBLE;
        break;
      case 3:
        points = SCORE_POINTS.TRIPLE;
        break;
      case 4:
        points = SCORE_POINTS.TETRIS;
        break;
      default:
        points = 0;
    }
    return points * level;
  }, [level]);

  // Place piece on board
  const placePiece = useCallback(() => {
    if (!currentPiece) return;

    const newBoard = [...board];
    for (let y = 0; y < currentPiece.shape.length; y++) {
      for (let x = 0; x < currentPiece.shape[y].length; x++) {
        if (currentPiece.shape[y][x]) {
          const boardY = currentPiece.position.y + y;
          const boardX = currentPiece.position.x + x;
          if (boardY >= 0) {
            newBoard[boardY][boardX] = currentPiece.color;
          }
        }
      }
    }

    // Check for completed lines
    const completedLines = newBoard.reduce((count, row) => {
      if (row.every(cell => cell !== 0)) {
        return count + 1;
      }
      return count;
    }, 0);

    if (completedLines > 0) {
      // Remove completed lines
      for (let i = newBoard.length - 1; i >= 0; i--) {
        if (newBoard[i].every(cell => cell !== 0)) {
          newBoard.splice(i, 1);
          newBoard.unshift(Array(BOARD_WIDTH).fill(0));
        }
      }
      
      // Update score and lines cleared
      const newScore = score + calculateScore(completedLines);
      const newLinesCleared = linesCleared + completedLines;
      setScore(newScore);
      setLinesCleared(newLinesCleared);
      
      // Update level every 10 lines
      const newLevel = Math.floor(newLinesCleared / 10) + 1;
      if (newLevel !== level) {
        setLevel(newLevel);
      }
    }

    setBoard(newBoard);
    const nextPiece = getRandomTetromino();
    setCurrentPiece(nextPiece);

    // Check for game over - only if the new piece can't be placed at the starting position
    if (!isValidMove(nextPiece.shape, nextPiece.position)) {
      setGameOver(true);
      setIsPlaying(false);
    }
  }, [board, currentPiece, score, linesCleared, level, isValidMove, calculateScore]);

  // Move piece left/right
  const movePiece = useCallback((direction) => {
    if (!currentPiece) return;

    const newPosition = {
      ...currentPiece.position,
      x: currentPiece.position.x + direction
    };

    if (isValidMove(currentPiece.shape, newPosition)) {
      setCurrentPiece({ ...currentPiece, position: newPosition });
    }
  }, [currentPiece, isValidMove]);

  // Move piece down
  const movePieceDown = useCallback(() => {
    if (!currentPiece) return;

    const newPosition = {
      ...currentPiece.position,
      y: currentPiece.position.y + 1
    };

    if (isValidMove(currentPiece.shape, newPosition)) {
      setCurrentPiece({ ...currentPiece, position: newPosition });
      setScore(prevScore => prevScore + SCORE_POINTS.SOFT_DROP);
    } else {
      placePiece();
    }
  }, [currentPiece, isValidMove, placePiece]);

  // Rotate piece
  const rotatePiece = useCallback(() => {
    if (!currentPiece) return;

    const rotated = currentPiece.shape[0].map((_, i) =>
      currentPiece.shape.map(row => row[i]).reverse()
    );

    // Try to rotate at current position
    if (isValidMove(rotated, currentPiece.position)) {
      setCurrentPiece({ ...currentPiece, shape: rotated });
    } else {
      // Try to rotate with wall kick (move left or right if rotation is blocked)
      const kicks = [
        { x: 1, y: 0 },  // Try moving right
        { x: -1, y: 0 }, // Try moving left
        { x: 0, y: -1 }, // Try moving up
        { x: 2, y: 0 },  // Try moving right twice
        { x: -2, y: 0 }, // Try moving left twice
      ];

      for (const kick of kicks) {
        const newPosition = {
          x: currentPiece.position.x + kick.x,
          y: currentPiece.position.y + kick.y
        };

        if (isValidMove(rotated, newPosition)) {
          setCurrentPiece({
            ...currentPiece,
            shape: rotated,
            position: newPosition
          });
          break;
        }
      }
    }
  }, [currentPiece, isValidMove]);

  // Start new game
  const startGame = useCallback(() => {
    setBoard(createEmptyBoard());
    setCurrentPiece(getRandomTetromino());
    setGameOver(false);
    setScore(0);
    setLevel(1);
    setLinesCleared(0);
    setCurrentSpeed(INITIAL_SPEED);
    setIsPlaying(true);
  }, []);

  // Handle mobile controls
  const handleMobileControl = useCallback((action) => {
    if (!isPlaying || gameOver) return;

    switch (action) {
      case 'left':
        movePiece(-1);
        break;
      case 'right':
        movePiece(1);
        break;
      case 'down':
        movePieceDown();
        break;
      case 'rotate':
        rotatePiece();
        break;
      default:
        break;
    }
  }, [isPlaying, gameOver, movePiece, movePieceDown, rotatePiece]);

  // Check for mobile device
  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth <= 768);
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Speed increase over time
  useEffect(() => {
    if (!isPlaying || gameOver) return;

    const speedInterval = setInterval(() => {
      setCurrentSpeed(prevSpeed => Math.max(100, prevSpeed - SPEED_INCREASE_AMOUNT));
    }, SPEED_INCREASE_INTERVAL);

    return () => clearInterval(speedInterval);
  }, [isPlaying, gameOver]);

  // Game loop with dynamic speed
  useEffect(() => {
    if (!isPlaying || gameOver) return;

    const gameLoop = setInterval(() => {
      // Always try to move down
      const newPosition = {
        ...currentPiece.position,
        y: currentPiece.position.y + 1
      };

      if (isValidMove(currentPiece.shape, newPosition)) {
        setCurrentPiece({ ...currentPiece, position: newPosition });
      } else {
        placePiece();
      }
    }, Math.max(100, currentSpeed - (level - 1) * 100));

    return () => clearInterval(gameLoop);
  }, [isPlaying, gameOver, currentPiece, isValidMove, placePiece, level, currentSpeed]);

  // Handle keyboard controls
  useEffect(() => {
    if (!isPlaying) return;

    const handleKeyPress = (event) => {
      if (gameOver) return;

      switch (event.key) {
        case 'ArrowLeft':
          event.preventDefault();
          movePiece(-1);
          break;
        case 'ArrowRight':
          event.preventDefault();
          movePiece(1);
          break;
        case 'ArrowDown':
          event.preventDefault();
          movePieceDown();
          break;
        case 'ArrowUp':
          event.preventDefault();
          rotatePiece();
          break;
        case ' ':
          event.preventDefault();
          // Hard drop functionality removed
          break;
        default:
          break;
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [isPlaying, gameOver, movePiece, movePieceDown, rotatePiece]);

  return (
    <div className="game">
      <div className="game-info">
        <div className="score">Score: {score}</div>
        <div className="level">Level: {level}</div>
        <div className="lines">Lines: {linesCleared}</div>
        {!isPlaying && (
          <button onClick={startGame}>
            {gameOver ? 'Play Again' : 'Start Game'}
          </button>
        )}
      </div>
      <Board
        board={board}
        currentPiece={currentPiece}
        gameOver={gameOver}
      />
      {isMobile && isPlaying && (
        <div className="mobile-controls">
          <button className="mobile-btn left" onClick={() => handleMobileControl('left')}>←</button>
          <button className="mobile-btn right" onClick={() => handleMobileControl('right')}>→</button>
          <button className="mobile-btn down" onClick={() => handleMobileControl('down')}>↓</button>
          <button className="mobile-btn rotate" onClick={() => handleMobileControl('rotate')}>↻</button>
        </div>
      )}
    </div>
  );
}

export default Game; 