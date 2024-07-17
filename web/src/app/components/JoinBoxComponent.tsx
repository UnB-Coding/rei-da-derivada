import React from "react";
import ArrowButton from "../components/ArrowButton";

interface JoinBoxComponentProps {
    id?: number;
    name?: string;
    active?: boolean;
}

function handleClick(){
    console.log("clicked");
    /* 
       lidar depois com o click do usuário para o envio da rota
       relativa ao cargo do participante
    */
}

const JoinBoxComponent = (props: JoinBoxComponentProps) => {
    return (
        <div className="bg-neutral-100 border-2 w-[316px] h-[55px] rounded-md flex justify-between px-2 items-center z-0">
            <p className="text-primary font-semibold text-xl">{props.name?.toUpperCase()}</p>
            {props.active && (
                <span className="flex h-3 w-3 absolute ml-56">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full bg-green-500 h-3 w-3 bg--500"></span>
                </span>
            )}
            <ArrowButton onClick={handleClick}/>
        </div>
    );
}

export default JoinBoxComponent;