import React from 'react'

import classes from './Button.module.css';

export default function Button({children, onSendData, data, ...props}) {
    const sendData = () => {
        onSendData(data)
    }
    return (
        <button className={[classes.reser, classes.button].join(" ")} onClick={sendData} {...props}>{children}</button>
    )
}