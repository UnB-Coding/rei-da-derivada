import React, { useState, useContext } from "react";
import ArrowButton from "./ArrowButton";
import { UserContext } from "../contexts/UserContext";

interface EventsComponentProps {
    title: string;
    description: string;
    optionalph?: string;
    placeholder: string;
    useEmail: boolean;
    type: string;
    function: (args: any) => any;
}

const EventsComponent = (props: EventsComponentProps) => {
    const { user } = useContext(UserContext);
    const [field, setField] = useState<string>("");
    const [token, setToken] = useState<string>("");

    let params: any;
    switch (props.type) {
        case "create":
            params = {
                access: user.access,
                name: field,
                token: token
            }
            break;
        case "join":
            params = {
                access: user.access,
                email: field,
                token: token
            }
            break;
        
        case "staff":
            params = {
                access: user.access,
                token: token
            }
            break;
        default:
            break;
    }

    return (
        <>
            <div className="bg-neutral-100 rounded-2xl mt-5 px-5 py-4 grid w-96 h-auto gap-4 shadow-sm">
                <p className="font-bold text-primary">{props.title.toUpperCase()}</p>
                <p className="font-light">{props.description}</p>
                {props.useEmail && <input onChange={event => setField(event.target.value)} className="border-[1.5px] border-blue-500 w-64 h-[40px] rounded-lg pl-5" type="email" placeholder={props.optionalph}/>}
                <div className="flex gap-4">
                    <input onChange={event => setToken(event.target.value)}className="border-[1.5px] border-blue-500 w-64 rounded-lg pl-5" type="text" placeholder={props.placeholder}/>
                    <ArrowButton onClick={() => props.function(params)}/>
                </div>
        
            </div>
        </>
        
    );
};

export default EventsComponent;