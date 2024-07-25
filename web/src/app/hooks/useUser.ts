'use client'

import { useContext } from "react"
import { UserContext } from "../contexts/UserContext"

export default function useUser(){
    const user = useContext(UserContext);

    return user;
}