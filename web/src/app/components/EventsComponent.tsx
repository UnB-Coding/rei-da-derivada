import React from "react";
import ArrowButton from "./ArrowButton";

interface EventsComponentProps {
    title: string;
    description: string;
    placeholder: string;
    useEmail: boolean;
    type: string;
}

const EventsComponent = (props: EventsComponentProps) => {
    return (
        <>
            <div className="bg-neutral-100 rounded-2xl mt-5 px-5 py-4 grid w-96 h-auto gap-4 shadow-sm">
                <p className="font-bold text-primary">{props.title.toUpperCase()}</p>
                <p className="font-light">{props.description}</p>
                {props.useEmail && <input className="border-[1.5px] border-blue-500 w-64 h-[40px] rounded-lg pl-5" type="email" placeholder={"Ex : exemplo@email.com"}/>}
                <div className="flex gap-4">
                    <input className="border-[1.5px] border-blue-500 w-64 rounded-lg pl-5" type="text" placeholder={props.placeholder}/>
                    <ArrowButton path="home"/>
                </div>
        
            </div>
        </>
        
    );
};

export default EventsComponent;