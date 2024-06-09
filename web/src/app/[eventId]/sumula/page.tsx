'use client'
import { useContext, useEffect } from "react";
import { UserContext } from "@/app/contexts/UserContext";
import { useRouter } from "next/navigation";
import LoadingComponent from "@/app/components/LoadingComponent";
import HeaderComponent from "@/app/components/HeaderComponent";
import ActiveSumulaComponent from "@/app/components/ActiveSumulaComponent";
import EventNavBarComponent from "@/app/components/EventNavBarComponent";

export default function Sumula() {
  const { user, loading } = useContext(UserContext);
  const router = useRouter();
  useEffect(() => {
    if (!user.access && !loading) {
        //Adicionar um verificador para saber se o evento existe
        //Adicionar um verificador para saber se o usuário é monitor
        router.push("/");
    }
  }, [user]);

  return loading ? <LoadingComponent/>:
    <>
        <HeaderComponent/>
        <ActiveSumulaComponent/>
        <EventNavBarComponent/>
    </>
}