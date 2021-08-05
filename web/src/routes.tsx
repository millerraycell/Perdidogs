import React from 'react'
import {BrowserRouter, Switch, Route} from 'react-router-dom';
import AnimalsMap from './pages/AnimalsMap';
import Landing from './pages/Landing';

function Routes(){
    return(
        <BrowserRouter>
            <Switch>
                <Route path="/" exact component={Landing}/>
                <Route path="/map" component={AnimalsMap}/>
            </Switch>
        </BrowserRouter>
    );
}

export default Routes 
