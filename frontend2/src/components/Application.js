import {useContext, useEffect, useState} from "react";
import AuthContext from "../context/AuthContext";
import useAxios from "../utils/useAxsios";
import {Hero} from "./Hero";

export const Application = () =>{

    let [marketData, setMarketData] = useState([null])
    let {authTokens, logoutUser} = useContext(AuthContext)

    let api = useAxios()



    useEffect(()=> {
        const getGeneralMarketData = async() =>{
            let response = await api.get('/api/market-data/general')

            if(response.status === 200){
                setMarketData(response.data)
            }

        }
        getGeneralMarketData()
    }, [])


    const stats = (marketData) =>{

        const tickers = Object.keys(marketData.entries)
        //
        const totalSignalsPerTicker = {}
        tickers.map((ticker, index) =>{
            totalSignalsPerTicker[ticker] = 0
            Object.keys(marketData.entries[ticker]).map((strategy, location) =>{
                if(marketData.entries[ticker][strategy].status){
                    totalSignalsPerTicker[ticker]++
                }
            })
        })
        return (
            <div className="stats shadow bg-base-300 ">

                <div className="stat place-items-center">
                    <div className="stat-title">Entries</div>
                    <div className="stat-value">{tickers.length}</div>
                    {/*<div className="stat-desc"></div>*/}
                </div>

                <div className="stat place-items-center">
                    <div className="stat-title">Multiple Indicators</div>
                    <div className="stat-value text-secondary">{Object.values(totalSignalsPerTicker).filter(val => val > 1).length}</div>
                    {/*<div className="stat-desc text-secondary"></div>*/}
                </div>

                <div className="stat place-items-center">
                    <div className="stat-title">Single Indicator</div>
                    <div className="stat-value">{Object.values(totalSignalsPerTicker).filter(val => val === 1).length}</div>
                    {/*<div className="stat-value"></div>*/}
                </div>

            </div>
        )
    }

    return(
        <div className="hero min-h-screen bg-base-200">
            <div className="hero-content flex-col lg:flex-row-reverse">
                <div>
                    <h1 className="text-5xl font-bold">Some Title</h1>
                    <p className="py-6">Provident cupiditate voluptatem et in. Quaerat fugiat ut assumenda excepturi
                        exercitationem quasi. In deleniti eaque aut repudiandae et a id nisi.</p>
                    {marketData ? stats(marketData): <></>}

                </div>
            </div>
        </div>
    )
}