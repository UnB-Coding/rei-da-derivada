import { useContext } from "react";
import { EventContext } from "../contexts/EventContext";

export default function useCurrentEvent() {
    const { currentEvent } = useContext(EventContext);
    
    return currentEvent;
}