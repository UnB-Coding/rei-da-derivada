'use client'
import { createContext, useState} from 'react';

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
}

export const UserContext = createContext({} as UserContextType);

export default function UserContextProvider({ children }:{children: React.ReactNode}) {
  const [user, setUser] = useState<User>({});

  return (
    <UserContext.Provider value={{ user, setUser }}>
      {children}
    </UserContext.Provider>
  );
}
