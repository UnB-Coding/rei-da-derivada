import React from "react";
import JoinBoxComponent from "./JoinBoxComponent";
import { useContext } from "react";
import { UserContext } from "../contexts/UserContext";

interface UserEvent {
    role?: string;
    event?: {
      id: number;
      name: string;
      active: boolean;
    }
}
interface ListObjectComponentProps {
    title: string;
    live?: boolean;
}

const ListObjectComponent = (props: ListObjectComponentProps) => {
    const { user } = useContext(UserContext);
    const events = user.all_events;
    const activeEvents: UserEvent[] = [];
    const endedEvents: UserEvent[] = [];
    let hasEvents = false;

    if (events !== undefined && events.length > 0) {
        hasEvents = true;
        events.forEach((event) => {
            if(event.event?.active){
                activeEvents.push(event);
            } else {
                endedEvents.push(event);
            }
        })
    }
    return(
        <div className="grid justify-center items-center gap-4 pb-4 pt-10">
            <p className="text-xl font-semibold text-primary ">{props.title.toUpperCase()}</p>
            {props.live ? 
            <>
                {!hasEvents || activeEvents.length === 0 ? <p>Nenhum evento contrado</p>
                : activeEvents.map((event) => {
                    return (
                        <JoinBoxComponent name={event.event?.name} active={event.event?.active}/>
                    )
                })}
            </>
            :
            <>
                {!hasEvents || endedEvents.length === 0 ? <p>Nenhum evento contrado</p>
                : endedEvents.map((event) => {
                    return (
                        <JoinBoxComponent name={event.event?.name} active={event.event?.active}/>
                    )
                })}
            </>}
        </div>
    );
}

export default ListObjectComponent;