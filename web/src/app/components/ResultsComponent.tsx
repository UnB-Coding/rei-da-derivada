import React, { use, useContext } from "react";
import { useState } from "react";
import DisplayComponent from "./DisplayPlayerComponent";
import NoResults from "./NoResults";
import { UserContext } from "../contexts/UserContext";
import getResults from "../utils/api/getResults";

export default function ResultsComponent() {
    const { user } = useContext(UserContext);
    const [ isPlayer, setIsPlayer ] = useState<boolean>(false);
    const [ result, setResult ] = useState<boolean>(false);

    return result ? <NoResults/> :
        <>
            <div className="grid justify-center items-center gap-5 py-32">
            {isPlayer && 
                <div>
                    <p className="font-semibold text-slate-700">SEU DESEMPENHO</p>
                    <DisplayComponent playerName="Player 1" points={10}/>
                </div>}
            <div className="grid gap-3">
                <p className="font-semibold text-slate-700">TOP 4</p>
                <DisplayComponent playerName="Player 2" points={52}/>
                <DisplayComponent playerName="Player 2" points={48}/>
                <DisplayComponent playerName="Player 2" points={46}/>
                <DisplayComponent playerName="Player 2" points={47}/>
            </div>
            <div className="grid gap-3">
                <p className="font-semibold text-slate-700">IMORTAIS</p>
                <DisplayComponent playerName="Player 2" points={90}/>
                <DisplayComponent playerName="Player 2" points={89}/>
                <DisplayComponent playerName="Player 2" points={88}/>
            </div>
            <div className="grid gap-3">
                <p className="font-semibold text-slate-700">PALADINO</p>
                <DisplayComponent playerName="Player 2" points={50}/>
            </div>
            

        </div>
        </>
        
    
};