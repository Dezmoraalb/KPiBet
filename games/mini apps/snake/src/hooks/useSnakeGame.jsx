import { useState, useEffect, useCallback } from 'react';

const GRID_SIZE = 20;
const CELL_SIZE = 20;
const INITIAL_SPEED = 150;
const SPEED_INCREMENT = 5;

const useSnakeGame = () => {
    const [snake, setSnake] = useState([{ x: 10, y: 10 }]);
    const [food, setFood] = useState({ x: 5, y: 5 });
    const [direction, setDirection] = useState('right');
    const [score, setScore] = useState(0);
    const [gameOver, setGameOver] = useState(false);
    const [gameStarted, setGameStarted] = useState(false);
    const [speed, setSpeed] = useState(INITIAL_SPEED);

    const generateFood = useCallback(() => {
        const newFood = {
            x: Math.floor(Math.random() * GRID_SIZE),
            y: Math.floor(Math.random() * GRID_SIZE)
        };
        return newFood;
    }, []);

    const resetGame = useCallback(() => {
        setSnake([{ x: 10, y: 10 }]);
        setFood(generateFood());
        setDirection('right');
        setScore(0);
        setGameOver(false);
        setGameStarted(false);
        setSpeed(INITIAL_SPEED);
    }, [generateFood]);

    const handleDirectionChange = useCallback((newDirection) => {
        if (!gameStarted) {
            setGameStarted(true);
        }

        const opposites = {
            ArrowUp: 'ArrowDown',
            ArrowDown: 'ArrowUp',
            ArrowLeft: 'ArrowRight',
            ArrowRight: 'ArrowLeft'
        };

        if (opposites[newDirection] !== direction) {
            setDirection(newDirection);
        }
    }, [direction, gameStarted]);

    useEffect(() => {
        const handleKeyPress = (event) => {
            if (['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(event.key)) {
                handleDirectionChange(event.key);
            }
        };

        window.addEventListener('keydown', handleKeyPress);
        return () => window.removeEventListener('keydown', handleKeyPress);
    }, [handleDirectionChange]);

    useEffect(() => {
        if (!gameStarted || gameOver) return;

        const moveSnake = () => {
            setSnake(prevSnake => {
                const head = { ...prevSnake[0] };

                switch (direction) {
                    case 'ArrowUp':
                        head.y -= 1;
                        break;
                    case 'ArrowDown':
                        head.y += 1;
                        break;
                    case 'ArrowLeft':
                        head.x -= 1;
                        break;
                    case 'ArrowRight':
                        head.x += 1;
                        break;
                    default:
                        break;
                }

                // Check for collisions
                if (
                    head.x < 0 || head.x >= GRID_SIZE ||
                    head.y < 0 || head.y >= GRID_SIZE ||
                    prevSnake.some(segment => segment.x === head.x && segment.y === head.y)
                ) {
                    setGameOver(true);
                    return prevSnake;
                }

                const newSnake = [head];

                // Check if food is eaten
                if (head.x === food.x && head.y === food.y) {
                    setScore(prev => prev + 1);
                    setFood(generateFood());
                    setSpeed(prev => Math.max(50, prev - SPEED_INCREMENT));
                    newSnake.push(...prevSnake);
                } else {
                    newSnake.push(...prevSnake.slice(0, -1));
                }

                return newSnake;
            });
        };

        const gameInterval = setInterval(moveSnake, speed);
        return () => clearInterval(gameInterval);
    }, [direction, food, gameOver, gameStarted, generateFood, speed]);

    const grid = Array.from({ length: GRID_SIZE * GRID_SIZE }, (_, index) => {
        const x = index % GRID_SIZE;
        const y = Math.floor(index / GRID_SIZE);
        const isSnake = snake.some(segment => segment.x === x && segment.y === y);
        const isFood = food.x === x && food.y === y;
        return { x, y, isSnake, isFood };
    });

    return {
        grid,
        score,
        gameOver,
        gameStarted,
        resetGame,
        GRID_SIZE,
        CELL_SIZE,
        handleDirectionChange
    };
};

export default useSnakeGame; 