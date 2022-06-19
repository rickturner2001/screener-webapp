import {createContext, useEffect, useState} from "react";
import jwt_decode from 'jwt-decode'
import {useHistory} from "react-router-dom"

const AuthContext = createContext()

export default AuthContext;


export const AuthProvider = ({children}) =>{


    const [authTokens, setAuthTokens] = useState(()=> localStorage.getItem('authTokens') ? JSON.parse(localStorage.getItem('authTokens')) : null)
    const [user, setUser] = useState(()=> localStorage.getItem('authTokens') ? jwt_decode(localStorage.getItem('authTokens')) : null)
    const [loading, setLoading] = useState(true)

    const history = useHistory()

    const loginUser = async (username, password) =>{
        // e.preventDefault()
        console.log("Login User Called")

        const response = await fetch("http://127.0.0.1:8000/api/token/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({username: username, password: password})
        })

        const data = await response.json()
        if (response.status === 200){
            setAuthTokens(data)
            setUser(jwt_decode(data.access))
            localStorage.setItem("authTokens", JSON.stringify(data))
            history.push("/")
        }else{
            // Handle errors here
            alert("Something Went Wrong")
        }
    }

    const logoutUser = () =>{
        setAuthTokens(null)
        setUser(null)
        localStorage.removeItem("authTokens")
        history.push("/login")
    }

    // const updateToken = async () =>{
    //     console.log("Update token Called")
    //     const response = await fetch("http://127.0.0.1:8000/api/token/refresh/", {
    //         method: "POST",
    //         headers: {
    //             "Content-Type": "application/json"
    //         },
    //         body: JSON.stringify({refresh: authTokens?.refresh})
    //     })
    //
    //     const data = await response.json()
    //
    //     if (response.status === 200){
    //         setAuthTokens(data)
    //         setUser(jwt_decode(data.access))
    //         localStorage.setItem("authTokens", JSON.stringify(data))
    //     }else{
    //         logoutUser()
    //     }
    //
    //     if(loading){
    //         setLoading(false)
    //     }
    // }

    let contextData ={
        user:user,
        loginUser: loginUser,
        logoutUser: logoutUser,
        authTokens: authTokens
    }


    // Life-cycle (refreshing token every 4 minutes)
    useEffect(() =>{
        if(authTokens){
            jwt_decode(authTokens.access)
        }
        setLoading(false)
    }, [authTokens, loading])


    return(
        <AuthContext.Provider value={contextData}>
            {loading ? null : children}
        </AuthContext.Provider>
    )
}
