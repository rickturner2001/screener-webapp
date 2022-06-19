import React, {useState, useEffect} from "react";

import {Hero} from "../components/Hero";
import {Section} from "../components/Section";
import {Footer} from "../components/Footer";
import bgTest from "../assets/bg_tes.png";



export const HomePage = () =>{
    return(
        <>
            <Hero reverse={true} title='Portfolio Management' content='Provident cupiditate voluptatem et in. Quaerat fugiat ut assumenda excepturi
                            exercitationem quasi. In deleniti eaque aut repudiandae et a id nisi.' img={bgTest}
                            hasMenu={true}
            ></Hero>
            <Section></Section>
            <Footer></Footer>
        </>
    )

}