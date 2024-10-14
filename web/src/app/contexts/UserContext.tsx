'use client'
import { createContext, use, useState} from 'react';
import { useEffect } from 'react';
import request from '../utils/request';
import getEvents from '../utils/api/getEvents';
import { settingsWithAuth } from '../utils/settingsWithAuth';

export interface User {
  access?: string;
  email?: string;
  first_name?: string;
  last_name?: string;
  picture_url?: string;
  all_events?: UserEvent[];
} 
export interface UserEvent {
  role?: string;
  event?: {
    id: number;
    name: string;
    active: boolean;
  }
}

interface UserContextType {
  user: User;
  setUser: (user: User) => void;
  loading: boolean;
  setLoading: (loading: boolean) => void;
}

export async function eventLogin(args: any){
  const {access, email, token} = args
  const body = {
    "email": email,
    "join_token": token
  }
  const response = await request.post("/api/players/", body, settingsWithAuth(access));
  if(response.status === 200){
    const data = response.data;
  }
}


export const UserContext = createContext({} as UserContextType);

export default function UserContextProvider({ children }:{children: React.ReactNode}) {
  const [user, setUser] = useState<User>({});
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    fetch(`${process.env.NEXT_PUBLIC_API_URL}/users/login/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Accept": "application/json",
      },
      credentials: "include",
    }).then((res) => {
      return res.json();
    }).then((data) => {
      setUser(data);
    }).catch((err) => {
      console.error(err);
    });
    setLoading(false);
  }, [setUser]);

  useEffect(() => {
    if (user.access) {
      getEvents(user.access).then((events) => {
        setUser((prev) => ({ ...prev, all_events: events }));
      });
    }
  },[user.access]);

  return (
    <UserContext.Provider value={{ user, setUser, loading, setLoading }}>
      {children}
    </UserContext.Provider>
  );
}
