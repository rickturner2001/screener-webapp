import React, {ChangeEvent, useState} from "react";


export const SignupModal = () => {
    const [step, setStep] = useState(0)
    const [hasError, setHasError] = useState(false)

    const [username, setUsername] = useState("")
    const [email, setEmail] = useState("")
    const [password, setPassword] = useState("")
    const [confirmPassword, setConfirmPassword] = useState("")


    const inputs = [
        ["Username", "randomuser001", "text", setUsername, username, {constraints: username.trim().length >= 6}],
        ["Email", "johndoe@gmail.com", "email", setEmail, email, {constraints: email.trim().includes("@")}],
        ["Password", "password123", "password",setPassword, password, {constraints: password.length >= 6}],
        ["Confirm Password", "password123", "password", setConfirmPassword, confirmPassword, {constraints: confirmPassword === password}]]

    const backOneStep = () =>{
        document.querySelector(".value-input")
        setStep(step - 1)
    }

    const resetInput = () =>{
        setStep(0)
        setEmail("")
        setUsername("")
        setPassword("")
        setConfirmPassword("")
    }
    const setData = (data) =>{
        if(data){
            console.log(data)
        }
        document.querySelector(".modal-close").click()
        resetInput()
    }

    const renderInput = (values) =>{
        const [label, placeholder, type, setFunc, _, constraints] = values
        return(
            <>
                <label className="label">
                    <span className="label-text">{label}</span>
                </label>
                <div className='flex w-full gap-4'>
                    <input type={type} placeholder={placeholder} onChange={(event) =>{setFunc(event.target.value.trim())}}
                           className={`input input-bordered input-primary w-full max-w-xs value-input`}/>
                    <button disabled={!constraints.constraints}  onClick={async (event) => {
                        event.preventDefault()

                        }
                    }
                            className={`w-[20%] btn ${step === 3 ? 'btn-accent' : "btn-primary"}` } defaultValue={step === 3 ? "Done": "Next"}>
                        {`${step === 3 ? "Done" : "Next"}`}
                    </button>
                    <button className={`btn btn-warning`} disabled={step === 0} onClick={(event) =>{
                        event.preventDefault()
                        backOneStep()
                    }}>Previous</button>
                </div>
            </>
        )
    }

    const badInput = (message) =>{
        return (
            <div className="alert alert-error shadow-lg w-[100%] mt-4 h-12">
                <div>
                    <svg xmlns="http://www.w3.org/2000/svg"
                         className="stroke-current flex-shrink-0 h-6 w-6" fill="none"
                         viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2"
                              d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                    </svg>
                    <span>Error! {message}</span>
                </div>
            </div>
        )
    }

    return(
        <>
            <input type="checkbox" id="SignupModal" className="modal-toggle"/>
            <div className="modal">
                <form className="modal-box">
                    <label className='btn btn-sm btn-circle absolute right-2 top-2 modal-close' htmlFor="SignupModal" >x</label>
                    <div className='flex flex-col w-full h-full gap-4 mb-4'>
                        <h3 className="font-bold text-lg text-center mb-2">Sign Up</h3>
                        <div className="form-control w-[100%]">
                            {step === 3 ? renderInput(inputs[3]) : step === 2 ? renderInput(inputs[2]) : step === 1 ? renderInput(inputs[1]) : renderInput(inputs[0]) }
                            {hasError && badInput(`${step === 0 ? "username is too short (6 characters)" :
                                step === 1 ? "Email is invalid" : step === 2 ? "Password is too short (8 characters)" : "Passwords don't match"}`)}
                        </div>
                    </div>
                    <ul className="steps steps-vertical lg:steps-horizontal">
                        <li className="step step-primary">Username</li>
                        <li className={`step ${step > 0 ? ' step-primary': ""}`}>Email</li>
                        <li className={`step ${step > 1 ? ' step-primary': ""}`}>Password</li>
                        <li className={`step ${step > 2 ? ' step-primary': ""}`}>Confirm Password</li>
                    </ul>
                </form>
            </div>
        </>
    )
}

