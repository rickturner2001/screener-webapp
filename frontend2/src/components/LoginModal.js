import React, {useContext, useState} from "react";
import AuthContext from "../context/AuthContext";


export const LoginModal = () =>{

    const [email, setEmail] = useState("")
    const [password, setPassword] = useState("")

    const resetData = () =>{
        setPassword("");
        setEmail("");
        document.querySelector(".input-email").value = "";
        document.querySelector(".input-password").value = "";
    }

    const {loginUser} = useContext(AuthContext)

    return (
        <>
            <input type="checkbox" id="login-modal" className="modal-toggle"/>
            <div className="modal">
                <div className="modal-box">
                    <label className="btn btn-sm btn-circle absolute right-2 top-2 modal-close-login" htmlFor='login-modal' onClick={() =>{
                        setEmail("")
                        setPassword("")
                        resetData()
                    }}>x</label>
                    <div className="card-body">
                        <div className="form-control">
                            <label className="label">
                                <span className="label-text">Email</span>
                            </label>
                            <input type="text" placeholder="email" className="input input-bordered input-primary input-email" onChange={(e) =>{
                                setEmail(e.target.value)
                            }}/>
                        </div>
                        <div className="form-control">
                            <label className="label">
                                <span className="label-text">Password</span>
                            </label>
                            <input type="password" placeholder="password" className="input input-bordered input-primary input-password" onChange={(e) =>{
                                setPassword(e.target.value)
                            }}/>
                            <label className="label">
                                <a href="src/components/LoginModal#" className="label-text-alt link link-hover">Forgot password?</a>
                            </label>
                        </div>
                        <div className="form-control mt-6">
                            <button disabled={!password || !email} className="btn btn-primary" onClick={async (event) => {

                                loginUser(email, password)
                                document.querySelector("#login-modal").click()

                                }
                            }
                            >Login</button>
                        </div>
                    </div>
                </div>
            </div>
        </>
    )

}
