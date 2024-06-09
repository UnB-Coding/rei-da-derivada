'use client'
import { useContext, useEffect } from "react";
import { UserContext } from "@/app/contexts/UserContext";
import { useRouter } from "next/navigation";
import HeaderComponent from "@/app/components/HeaderComponent";
import LoadingComponent from "@/app/components/LoadingComponent";
import EventNavBarComponent from "@/app/components/EventNavBarComponent";

export default function Profile() {
  const { user, loading } = useContext(UserContext);
  const router = useRouter();
  useEffect(() => {
    if (!user.access && !loading) {
        //Adicionar um verificador para saber se o evento existe
        router.push("/");
    }
  }, [user]);

  return loading ? <LoadingComponent/>:
    <>
      <HeaderComponent/>
      <EventNavBarComponent/>
    </>
    
  
}