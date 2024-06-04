'use client'
import { useContext, useEffect } from "react";
import { useState } from "react";
import { UserContext } from "@/app/contexts/UserContext";
import profile from '@/app/assets/matui.jpg';
import logo from '@/app/assets/logo.png';
import HeaderComponent from "@/app/components/HeaderComponent";
import NavBarComponent from "@/app/components/NavBarComponent";
import LoadingComponent from "@/app/components/LoadingComponent";

export default function JoinEvents() {
  const { user, setUser, loading } = useContext(UserContext);  

  return loading ? <LoadingComponent/>:
    <>
      <HeaderComponent profile={profile} name={user.first_name} logo={logo}/>
      <NavBarComponent/>
    </>
    
  
}