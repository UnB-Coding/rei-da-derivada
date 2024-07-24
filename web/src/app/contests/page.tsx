'use client'
import { useContext, useEffect, useState } from "react";
import { UserContext } from "@/app/contexts/UserContext";
import HeaderComponent from "@/app/components/HeaderComponent";
import NavBarComponent from "@/app/components/NavBarComponent";
import LoadingComponent from "@/app/components/LoadingComponent";
import Contests from "@/app/components/Contests";
import { useRouter } from "next/navigation";

export default function AllContests() {
  const router = useRouter();
  const { user, loading } = useContext(UserContext);

  useEffect(() => {
    const checkAccess = async () => {
      if(!user.access && !loading){
        router.push("/");
      }
    }
    checkAccess();
  },[user, loading, router])

  if(!user.access || loading){
    return <LoadingComponent/>;
  }

  return(
    <>
        <HeaderComponent/>
          <Contests/>
        <NavBarComponent/>
    </>
  );
    
  
}