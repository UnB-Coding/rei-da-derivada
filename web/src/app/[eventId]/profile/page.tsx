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

  return loading ? <LoadingComponent/> :
    <>
      <HeaderComponent/>
      <div className="grid justify-center items-center py-32 px-2 text-center">
        <p className="text-primary font-semibold text-xl">N SEI OQ COLOCAR</p>
        <p className="text-slate-700">Você não está inscrito em nenhuma chave no momento.</p>
      </div>
      <EventNavBarComponent/>
    </>
    
  
}