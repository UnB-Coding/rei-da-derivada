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
    let activeEvents: UserEvent[] = [];
    let endedEvents: UserEvent[] = [];

    if (events !== undefined && events.length > 0) {
        activeEvents = events.filter(event => event.event?.active)
        endedEvents = events.filter(event => !event.event?.active)
    }
    return(
        <div className="grid justify-center items-center gap-4 pb-4 pt-10">
            <p className="text-xl font-semibold text-primary ">{props.title.toUpperCase()}</p>
            {props.live ? 
            <>
                {activeEvents.length === 0 ? <p>Nenhum evento contrado</p>
                : activeEvents.map((event) => {
                    return (
                        <JoinBoxComponent key={event.event?.id} name={event.event?.name} active={event.event?.active} id={event.event?.id} isEvent={true}/>
                    )
                })}
            </>
            :
            <>
                {endedEvents.length === 0 ? <p>Nenhum evento contrado</p>
                : endedEvents.map((event) => {
                    return (
                        <JoinBoxComponent key={event.event?.id} name={event.event?.name} active={event.event?.active} id={event.event?.id} isEvent={true}/>
                    )
                })}
            </>}
        </div>
    );
}

export default ListObjectComponent;