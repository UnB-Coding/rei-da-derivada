import React from "react";

interface DisplayPlayerComponentProps{
    playerName: string;
    points: number;
};

export default function DisplayComponent(props: DisplayPlayerComponentProps) {
    return (
        <div className="bg-neutral-100 border-2 w-[316px] h-[55px] rounded-md flex justify-between items-center z-0 px-4">
            <p className="text-primary font-semibold text-xl">{props.playerName}</p>
            <p className="text-primary font-semibold text-xl">{props.points}</p>    
        </div>
    );
};