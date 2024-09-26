'use client'
import { useContext, useEffect, useState } from "react";
import { UserContext } from "@/app/contexts/UserContext";
import HeaderComponent from "@/app/components/HeaderComponent";
import NavBarComponent from "@/app/components/NavBarComponent";
import LoadingComponent from "@/app/components/LoadingComponent";
import EventNavBarComponent from "@/app/components/EventNavBarComponent"
import Contests from "@/app/components/Contests";
import { useRouter } from "next/navigation";

export default function AllContests() {
  const router = useRouter();
  const { user, loading } = useContext(UserContext);

  useEffect(() => {
    if(!user.access && !loading){
      router.push("/");
    }
  },[user])

  if(!user.access || loading || !user.all_events){
    return <LoadingComponent/>;
  }

  return(
    <>
        <HeaderComponent/>
          <Contests/>
        <EventNavBarComponent userType="common"/>
    </>
  );
    
  
}