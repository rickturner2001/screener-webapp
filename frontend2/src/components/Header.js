import {Link} from "react-router-dom";
import {useContext} from "react";
import AuthContext from "../context/AuthContext";

export const Header = () =>{

    const {user, logoutUser} = useContext(AuthContext)

    return(
        <div>
            <Link to='/'>Home</Link>
            <span> | </span>
            {user ? (
                <p onClick={logoutUser}>Logout</p>
            ): (
                <Link to='/login'>Login</Link>
            )}
            {user && <p>Hello {user.username}</p>}

        </div>
    )
}