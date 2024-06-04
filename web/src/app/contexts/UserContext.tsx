'use client'
import { createContext, use, useState} from 'react';
import { useEffect } from 'react';

interface User {
  access?: string;
  email?: string;
  first_name?: string;
  last_name?: string;
  picture_url?: string;
}

interface UserContextType {
  user: User;
  setUser: (user: User) => void;
  loading: boolean;
  setLoading: (loading: boolean) => void;
}

export const UserContext = createContext({} as UserContextType);

export default function UserContextProvider({ children }:{children: React.ReactNode}) {
  const [user, setUser] = useState<User>({});
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    fetch("http://localhost:8000/users/login/", {
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
      setLoading(false);
    }).catch((err) => {
      console.error(err);
      
      setLoading(false);
    });
  }, [setUser]);

  return (
    <UserContext.Provider value={{ user, setUser, loading, setLoading }}>
      {children}
    </UserContext.Provider>
  );
}
