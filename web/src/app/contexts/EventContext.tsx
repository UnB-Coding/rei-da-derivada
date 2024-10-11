'use client'

import { createContext, useState, useEffect } from 'react'

export interface CurrentEvent {
    role?: string;
    event?: {
        id: number;
        name: string;
        active: boolean;
    }
    paths?: string[];
};

interface EventContextType{
    currentEvent: CurrentEvent;
    setCurrentEvent: (currentEvent: CurrentEvent) => void;
};

export const EventContext = createContext({} as EventContextType);

export default function EventContextProvider({ children }:{children: React.ReactNode}) {
    const [currentEvent, setCurrentEvent] = useState<CurrentEvent>({});
    return (
    <EventContext.Provider value={{currentEvent, setCurrentEvent}}>
      {children}
    </EventContext.Provider>
  )
}