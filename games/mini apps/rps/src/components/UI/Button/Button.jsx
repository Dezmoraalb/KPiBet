import React from 'react'

import classes from './Button.module.css';

export default function Button({children, playerMove, onMove, ...props}) {
    const move = () => {
        onMove(playerMove)
    }
    return (
        <button className={[classes.reser, classes.button].join(" ")} onClick={move} {...props}>{children}</button>
    )
}
