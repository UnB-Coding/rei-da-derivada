import React from "react";
import JoinBoxComponent from "./JoinBoxComponent";
import { title } from "process";

interface ActiveSumulaComponentProps {
    title: string;
    active?: boolean;
};

const myObject = {  
    title: "chave-ab",
};

const ActiveSumulaComponent = () => {
    return (
        <div className="grid justify-center items-center py-32">
            <p className="text-primary font-semibold pb-4">SÚMULAS ATIVAS</p>
            <div className="grid gap-4">
                <JoinBoxComponent title={myObject.title} active={true} buttonPath={`./sumula/${myObject.title}`}/>
                <JoinBoxComponent title="chave-cd" active={true}/>
                <JoinBoxComponent title="chave-ef" active={true}/>
                <JoinBoxComponent title="imortais 10" active={true}/>
                <JoinBoxComponent title="imortais 11" active={true}/>
                <JoinBoxComponent title="imortais 12" active={true}/>
            </div>
        </div>    
    );
};

export default ActiveSumulaComponent;