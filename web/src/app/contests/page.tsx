'use client'
import { useContext, useEffect } from "react";
import { UserContext } from "@/app/contexts/UserContext";
import Image from 'next/image';
import profile from '@/app/assets/matui.jpg';
import logo from '@/app/assets/logo.png';
import HeaderComponent from "@/app/components/HeaderComponent";
import NavBarComponent from "@/app/components/NavBarComponent";
import ListObjectComponent from "../components/ListObjectComponent";

export default function AllContests() {
    const { user } = useContext(UserContext);
    useEffect(() => {
      if (!user.access) {
        console.log("Acesso negado");
      }
    });
  return (
    <div>
        <HeaderComponent profile={profile} name={user.first_name} logo={logo}/>
        <ListObjectComponent title="eventos ativos" active={true}/>
        <ListObjectComponent title="eventos passados"/>

        <NavBarComponent/>
    </div>
    
  );
}