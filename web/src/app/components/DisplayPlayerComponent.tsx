import React from "react";

interface DisplayPlayerComponentProps{
    playerName: string;
    points: number;
};

export default function DisplayComponent(props: DisplayPlayerComponentProps) {
    const trimName = (name: string) => {
        if(name.length > 35){
            return name.slice(0, 32) + "...";
        }
        return name;
    }
    const name = trimName(props.playerName);
    return (
        <div className="bg-neutral-100 border-2 w-[360px] h-[55px] md:w-[450px] md:h-[60px] rounded-md flex justify-between items-center z-0 px-4">
            <p className={`text-primary font-semibold md:text-xl text-lg`}>{name}</p>
            <p className="text-primary font-semibold text-xl">{props.points}</p>    
        </div>
    );
};