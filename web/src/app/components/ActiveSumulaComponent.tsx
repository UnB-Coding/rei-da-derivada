import React, { useState, useEffect} from "react";
import JoinBoxComponent from "./JoinBoxComponent";
import { usePathname } from "next/navigation";
import { title } from "process";

interface SumulaProps {
    id: number;
    active: boolean;
    name: string;
    description: string;
    referee: string;
}

const ActiveSumulaComponent = () => {
    const [ sumulas, setSumulas ] = useState<any[]>([]);
    useEffect(() => {

    },[]);

    return (
        <div className="grid justify-center items-center py-32">
            <p className="text-primary font-semibold pb-4">SÚMULAS ATIVAS</p>
            <div className="grid gap-4">
                {sumulas.map((sumula) => {
                    return <JoinBoxComponent key={sumula.id} name={sumula.name} active={sumula.activate} isEvent={false}/>
                })}
            </div>
        </div>    
    );
};

export default ActiveSumulaComponent;