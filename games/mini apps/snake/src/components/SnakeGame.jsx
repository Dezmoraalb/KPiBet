import React, { useEffect, useCallback } from 'react';
import useSnakeGame from '../hooks/useSnakeGame';
import useTelegram from '../hooks/useTelegram';
import './SnakeGame.css';

const SnakeGame = () => {
    const {
        grid,
        score,
        gameOver,
        gameStarted,
        resetGame,
        GRID_SIZE,
        CELL_SIZE,
        handleDirectionChange
    } = useSnakeGame();

    const { tg, WebAppMainButton } = useTelegram();
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
    
    return (
        <div className="game-container">
            <div className="score">Score: {score}</div>
            <div 
                className="grid"
                style={{
                    width: GRID_SIZE * CELL_SIZE,
                    height: GRID_SIZE * CELL_SIZE,
                }}
            >
                {grid.map(({ x, y, isSnake, isFood }) => (
                    <div
                        key={`${x}-${y}`}
                        className={`cell ${isSnake ? 'snake' : ''} ${isFood ? 'food' : ''}`}
                        style={{
                            width: CELL_SIZE,
                            height: CELL_SIZE,
                        }}
                    />
                ))}
            </div>
            {!gameStarted && (
                <div className="start-message">
                    Press any arrow key to start
                </div>
            )}
            {gameOver && (
                <div className="game-over">
                    <div>Game Over!</div>
                    <button onClick={resetGame}>Play Again</button>
                </div>
            )}
            <div className="controls">
                <div className="controls-row">
                    <button 
                        className="control-button up"
                        onClick={() => handleDirectionChange('ArrowUp')}
                        aria-label="Move Up"
                    >
                        ▲
                    </button>
                </div>
                <div className="controls-row">
                    <button 
                        className="control-button left"
                        onClick={() => handleDirectionChange('ArrowLeft')}
                        aria-label="Move Left"
                    >
                        ◀
                    </button>
                    <button 
                        className="control-button right"
                        onClick={() => handleDirectionChange('ArrowRight')}
                        aria-label="Move Right"
                    >
                        ▶
                    </button>
                </div>
                <div className="controls-row">
                    <button 
                        className="control-button down"
                        onClick={() => handleDirectionChange('ArrowDown')}
                        aria-label="Move Down"
                    >
                        ▼
                    </button>
                </div>
            </div>
        </div>
    );
};

export default SnakeGame; 