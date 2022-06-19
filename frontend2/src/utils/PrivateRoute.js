import {Redirect, Route} from "react-router-dom";
import React from "react";
import {useContext} from "react";
import AuthContext from "../context/AuthContext";


export const PrivateRoute = ({children, ...rest}) =>{
    const {user} = useContext(AuthContext)
    return (
        !user ? <Redirect to='/'/>:
            <Route {...rest}>{children}</Route>
    )
}