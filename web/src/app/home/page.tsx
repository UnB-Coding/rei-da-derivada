'use client'
import { useContext, useEffect } from "react";
import { UserContext } from "@/app/contexts/UserContext";
import Image from 'next/image';


export default function JoinEvents() {
    const { user } = useContext(UserContext);
    useEffect(() => {
        if (!user.access) {
            window.location.href = "/";
        }
    });
  return (
    <div>
      <h1>Página home do app</h1>
      <h2>Seja bem-vindo(a), {user.first_name}</h2>
      <Image src={`${user.picture_url}`} alt="Foto de perfil do usuário" width="250" height="250"/>
    </div>
  );
}