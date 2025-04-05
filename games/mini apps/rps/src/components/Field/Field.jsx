import React, {useEffect, useCallback} from 'react';

import useGame from '../../hooks/useGame';
import useTelegram from '../../hooks/useTelegram';

import Button from '../UI/Button/Button';


import classes from './Field.module.css';

export default function Field() {
    const { botCount,
            playerCount,
            bot,
            player,
            onMove } = useGame();
    const {tg, WebAppMainButton} = useTelegram();
    
    useEffect(() => {
        WebAppMainButton.setText(`Your count: ${playerCount}`);
        WebAppMainButton.show();
    }, [WebAppMainButton, playerCount]);
 
    const onSendData = useCallback(() => {
        tg.sendData(JSON.stringify({playerCount}));
    }, [tg, playerCount]);

    useEffect(() => {
        tg.onEvent('mainButtonClicked', onSendData);
        return () => {
            tg.offEvent('mainButtonClicked', onSendData);
        }
    }, [tg, onSendData]);

    return (
        <div className={classes.wrap}>
            <h1 className={classes.title}>Paper Scissors Stone</h1>
            <div className={classes.playfield}>
                <div className={classes.player}>
                    <p className={classes.counter}>{botCount}</p>
                    <img className={classes.img} src={require(`../../images/${bot}.webp`)} alt="" />
                </div>
                <div className={classes.player}>
                    <p className={classes.counter}>{playerCount}</p>
                    <img className={classes.img} src={require(`../../images/${player}.webp`)} alt="" />
                </div>
            </div>
            <div className={classes.interaction}>
                <Button onMove={onMove} playerMove="Paper">
                    <img className={classes.buttonImg} src={require("../../images/Paper.webp")} alt="" />
                </Button>
                <Button onMove={onMove} playerMove="Stone">
                    <img className={classes.buttonImg} src={require("../../images/Stone.webp")} alt="" />
                </Button>
                <Button onMove={onMove} playerMove="Shears">
                    <img className={classes.buttonImg} src={require("../../images/Shears.webp")} alt="" />
                </Button>
            </div>
        </div>
    )
}
