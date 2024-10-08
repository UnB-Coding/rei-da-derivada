import React, { useEffect, useContext, useState } from "react";
import ArrowButton from "../components/ArrowButton";
import { UserContext } from "../contexts/UserContext";
import { EventContext } from "../contexts/EventContext";
import { useRouter } from "next/navigation";
import { CurrentEvent } from "../contexts/EventContext";

interface JoinBoxComponentProps {
    id?: number;
    name?: string;
    active?: boolean;
    isEvent?: boolean;
    onClick?: () => Promise<void>;
}

const JoinBoxComponent = (props: JoinBoxComponentProps) => {
    const { user, setLoading } = useContext(UserContext);
    const { currentEvent, setCurrentEvent } = useContext(EventContext);
    const [shouldNavigate, setShouldNavigate] = useState(false);
    const router = useRouter();

    const adminpaths = ["admin", "sumula", "results"];
    const staffpaths = ["sumula", "results"];
    const playerpaths = ["profile", "results"];

    async function handleClick() {
        setLoading(true);
        let current = user.all_events?.find((event) => event.event?.id === props.id);

        const atual: CurrentEvent = {
            role: current?.role,
            event: current?.event,
            paths: current?.role === "admin" || current?.role === "manager"
                ? adminpaths
                : current?.role === "staff"
                    ? staffpaths
                    : playerpaths
        }

        setCurrentEvent(atual);
        setShouldNavigate(true);
        setLoading(false);
    }
    useEffect(() => {
        if (shouldNavigate && currentEvent && currentEvent.paths) {
            router.push(`/${currentEvent.event?.id}/${currentEvent.paths[0]}`);
            setShouldNavigate(false);
        }
    }, [shouldNavigate, currentEvent]);

    return (
        <div className="bg-neutral-100 border-2 w-[316px] h-[55px] md:w-[400px] md:h-[60px] rounded-md flex justify-between px-2 items-center z-0">
            <p className="text-primary font-semibold text-lg md:text-xl">{props.name?.toUpperCase()}</p>
            <div className="flex items-center relative">
                {props.active && (
                    <span className="absolute flex h-3 w-3 right-14">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                        <span className="relative inline-flex rounded-full bg-green-500 h-3 w-3"></span>
                    </span>
                )}
                <ArrowButton onClick={() => { props.isEvent ? handleClick() : props.onClick?.() }} />
            </div>
        </div>
    );
}

export default JoinBoxComponent;