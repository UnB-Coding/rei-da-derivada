import React from "react";
import ArrowButton from "../components/ArrowButton";

interface JoinBoxComponentProps {
    title?: string;
    buttonPath?: string;
    active?: boolean;
}

const JoinBoxComponent = (props: JoinBoxComponentProps) => {
    return (
        <div className="bg-neutral-100 border-2 w-[316px] h-[55px] rounded-md flex justify-between px-2 items-center z-0">
            <p className="text-primary font-semibold text-xl">{props.title?.toUpperCase()}</p>
            {props.active && (
                <span className="flex h-3 w-3 absolute ml-56">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-sky-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-3 w-3 bg-sky-500"></span>
                </span>
            )}
            <ArrowButton path="contests"/>
        </div>
    );
}

export default JoinBoxComponent;