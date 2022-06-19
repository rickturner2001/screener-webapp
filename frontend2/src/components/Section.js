import {DuplicateIcon} from "@heroicons/react/outline";
import {useState} from "react";


export const Section = () =>{

    const [isCopy, setIsCopy] = useState(false)

    const copyToClipboard = () => {
        setIsCopy(true)
        const url = "https://github.com/rickturner2001/market_screener.git"
        const temp = document.createElement("input")
        temp.value = url
        document.body.appendChild(temp)
        temp.select()
        document.execCommand("copy")
        temp.remove()
        setTimeout(() =>{
            setIsCopy(false)
        }, 1000)
    }


    return (
        <section className="w-full h-[100%]  bg-base-200">
            <div className='hero py-32 bg-base-200'>
                <div className="hero-content flex-col lg:flex-row">
                    <div className="mockup-code w-[50%] mr-10">
                        <pre data-prefix="$"><code>pip install -r requirements.txt</code></pre>
                        <pre data-prefix=">" className="text-warning"><code>installing...</code></pre>
                        <pre data-prefix=">" className="text-success"><code>Done!</code></pre>
                        <pre data-prefix="$"><code>uvicorn app:app --reload</code></pre>
                        <pre data-prefix="$"><code className='text-success'>INFO</code><code>:     Application startup complete.</code></pre>

                    </div>
                    <div>
                        <h1 className="text-5xl font-bold">Try The API</h1>
                        <p className="py-6">Provident cupiditate voluptatem et in. Quaerat fugiat ut assumenda excepturi
                            exercitationem quasi. In deleniti eaque aut repudiandae et a id nisi.</p>
                        <div className='flex items-center'>
                            <button  className="btn btn-primary" onClick={copyToClipboard}><DuplicateIcon className='w-5 h-5 mr-2'/> Clone IT</button>
                            <p className='ml-2 px-2 py-2 rounded-xl w-max text-center text-white text-3xlxl h-10 bg-base-100 transition-all duration-300'
                               style={isCopy ? {opacity: 1, visibility:"visible"} : {opacity: 0, visibility: "hidden"}}>Copied to Clipboard</p>
                        </div>

                    </div>
                </div>
            </div>
        </section>
    )
}