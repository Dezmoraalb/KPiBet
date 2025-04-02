import { useEffect, useState } from 'react';

export default function useGame() {
        function getRandomNumber(x, y) {
            return Math.floor(Math.random() * (y - x + 1)) + x;
        }
        const settings = {
            1: "Paper",
            2: "Stone",
            3: "Shears"
        }
        const [bot, setBot] = useState("WindСharged");
        const [player, setPlayer] = useState("WindСharged");
        const [count, setCount] = useState({botCount: 0, playerCount: 0});
        const onMove = (playerMove) => {
            let botNumberMove = getRandomNumber(1, 3);
            while (settings[botNumberMove] === bot) {
                botNumberMove = getRandomNumber(1, 3);
            }
            let botMove = settings[botNumberMove];
            setBot(botMove);
            setPlayer(playerMove);
            console.log("Bot:", bot);
            console.log("Player:", player);
        }
    
        useEffect(() => {
            if ((bot === "Paper" && player === "Stone") ||
                (bot === "Stone" && player === "Shears") ||
                (bot === "Shears" && player === "Paper")) {
                setCount(prevCount => ({ 
                    ...prevCount, 
                    botCount: prevCount.botCount + 3, 
                    playerCount: prevCount.playerCount - 2 
                }));
            }
        
            if ((player === "Paper" && bot === "Stone") ||
                (player === "Stone" && bot === "Shears") ||
                (player === "Shears" && bot === "Paper")) {
                setCount(prevCount => ({ 
                    ...prevCount, 
                    botCount: prevCount.botCount - 2, 
                    playerCount: prevCount.playerCount + 3 
                }));
            }
    
        }, [bot, player]);

        return {
            botCount: count.botCount,
            playerCount: count.playerCount,
            bot,
            player,
            onMove,
        }
}