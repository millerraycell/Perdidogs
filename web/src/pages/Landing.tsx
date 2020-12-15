import React, { FormEvent, useEffect, useState } from 'react'
import { FiArrowRight } from 'react-icons/fi'
import { useHistory } from 'react-router-dom'

import '../styles/pages/landing.css'

function Landing(){
    const [currentPos, setCurrentPos] = useState<[number, number]>([0,0])

    const history = useHistory()

    useEffect(()=>{
        navigator.geolocation.getCurrentPosition(pos => {
            setCurrentPos([pos.coords.latitude,pos.coords.longitude])
        })
    },[])

    const handleSubmit = (e: FormEvent) => {
        e.preventDefault()

        history.push({
            pathname: "/map",
            state: {
                center : currentPos
            }
        })
    }

    return(
        <div id="landing-page">
            <div className="content-wrapper">
                
                <main>
                    <strong>Bem Vindo</strong>
                    <h1>Perdidogs é uma plataforma para compartilhar animais perdidos</h1>
                    <h1>Para mais informações acesse nosso Twitter: </h1>
                    <a href="https://twitter.com/perdidogss" >
                        <h1>Twitter</h1>
                    </a>
                    <h1>Ou mande uma mensagem no nosso Telegram:</h1>
                    <a href="https://t.me/geo_localization_bot" >
                        <h1>Telegram</h1>
                    </a>
                        
                </main>

                <button type="submit" onClick={handleSubmit} className="enter-app">
                    Veja os animais<FiArrowRight size={26} color = 'rgba(0,0,0,0.6)'/>
                </button>
            </div>
        </div>
    );
}

export default Landing