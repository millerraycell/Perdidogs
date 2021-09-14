import React, { useEffect, useState } from 'react'
import {RouteComponentProps} from 'react-router'
import {Link} from 'react-router-dom'
import {FiArrowLeft} from 'react-icons/fi'
import {TileLayer, Marker, Map, Popup} from 'react-leaflet'
import Leaflet from 'leaflet';

import '../styles/pages/animalsmap.css'
import 'leaflet/dist/leaflet.css'

import mapMarker from '../images/forma-da-pata-preta.svg'
import map_pin from '../images/map-pin.svg'
import perdidogs from '../images/perdidogs.jpeg'
import api from '../services/api';

const mapIcon = Leaflet.icon({
    iconUrl: mapMarker,
    iconAnchor: [29, 68],
    iconSize:[58, 68],

    popupAnchor: [170, 2]
})

const user_location = Leaflet.icon({
    iconUrl: map_pin,
    iconAnchor: [29, 68],
    iconSize:[58, 68],

    popupAnchor: [170, 2]
})

interface Animal{
    _id: string,
    images : [string],
    latitude: number,
    longitude: number,
    date: Date
};

interface propriedades{
    center: [number,number]
}

function AnimalsMap( props : RouteComponentProps<{}, any, propriedades | any> ){
    const pos = props.location.state;

    let options = {maximumAge:10000, timeout:5000, enableHighAccuracy: true}

    const [animal_api, setAnimal] = useState<Animal[]>([])

    navigator.geolocation.getCurrentPosition((position) => {
        pos["center"] = [position.coords.latitude, position.coords.longitude]
        console.log(position)
    },undefined, options)    

    useEffect(()=>{
        api.get(`/?latitude=${pos["center"][0]}&longitude=${pos["center"][1]}`)
            .then(response => {
                setAnimal(response.data)
            })
    },[])

    return(
        <div id="page-map">
            <aside>
                <Link to="/" className="enter-app">
                    <FiArrowLeft size={26} color = 'rgba(0,0,0,0.6)'/>
                </Link>
                <img src={perdidogs} alt="Perdidogs"/>
                <header>
                    <h2>Animais próximos</h2>
                </header>

                <footer>
                    <strong>Boa Vista</strong>
                    <span>Roraima</span>
                </footer>
            </aside>
            <Map
                center={pos["center"]}
                zoom = {15}
                style = { {width:'100%', height:'100%'}}
                >

                <TileLayer 
                    url= {`https://api.mapbox.com/styles/v1/mapbox/light-v10/tiles/256/{z}/{x}/{y}@2x?access_token=${process.env.REACT_APP_MAPBOX_TOKEN}`} />

                {/* <TileLayer url="https://a.tile.openstreetmap.org/{z}/{x}/{y}.png" /> */}

                <Marker
                    position={pos["center"]}
                    icon = {user_location}
                >
                </Marker>

                {animal_api.map(animal =>{
                        return(
                            <Marker
                            key = {animal._id}
                            position={[animal.latitude,animal.longitude]}
                            icon = {mapIcon}
                            >
                                <Popup closeButton= {false} minWidth={240} maxWidth={240} className="map-popup">
                                    <p>Animal encontrado em: {animal.date}</p>
                                </Popup>
                            </Marker>
                        )

                    }
                )}       
            </Map>
        </div>

    );
};

export default AnimalsMap 
