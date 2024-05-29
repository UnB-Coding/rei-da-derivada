'use client'
import { useContext, useEffect } from "react";
import { UserContext } from "@/app/contexts/UserContext";
import Image from 'next/image';
import profile from '@/app/assets/matui.jpg';
import logo from '@/app/assets/logo.png';
import  HeaderComponent  from "@/app/components/HeaderComponent";


export default function JoinEvents() {
  const { user } = useContext(UserContext);
  useEffect(() => {
    if (!user.access) {
      window.location.href = "/";
    }
  });
  return (
    <div>
      <HeaderComponent profile={profile} name={user.first_name} logo={logo}/>
      <div className="">

      </div>
    </div>
    
  );
}