'use client'
import { useContext, useEffect } from "react";
import { UserContext } from "@/app/contexts/UserContext";
import { useRouter } from "next/navigation";
import HeaderComponent from "@/app/components/HeaderComponent";
import NavBarComponent from "@/app/components/NavBarComponent";
import LoadingComponent from "@/app/components/LoadingComponent";
import HomeJoinComponent from "../components/HomeJoinComponent";

export default function JoinEvents() {
  const { user, loading } = useContext(UserContext);
  const router = useRouter();

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

  return (
    <>
      <HeaderComponent/>
      <HomeJoinComponent/>
      <NavBarComponent/>
    </>
  );
}