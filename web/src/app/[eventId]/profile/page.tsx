'use client'
import { useContext, useEffect, useState } from "react";
import { UserContext } from "@/app/contexts/UserContext";
import { EventContext } from "@/app/contexts/EventContext";
import { useRouter, usePathname } from "next/navigation";
import HeaderComponent from "@/app/components/HeaderComponent";
import LoadingComponent from "@/app/components/LoadingComponent";
import EventNavBarComponent from "@/app/components/EventNavBarComponent";
import validatePath from "@/app/utils/validadePath";
import getBasePath from "@/app/utils/getBasePath";
import getPlayerInfo from "@/app/utils/api/getPlayerInfo";

export default function Profile() {
  const { user, loading } = useContext(UserContext);
  const [ playerInfo, setPlayerInfo ] = useState<any>(null);
  const [ canSee, setCanSee ] = useState<boolean>(false);
  const router = useRouter();
  const params = usePathname().split("/");
  const currentId = parseInt(params[1]);
  const currentPath = params[2];

  useEffect(() => {
    if (!user.access && !loading) {
      router.push("/");
    } else if (user.all_events) {
      const current = user.all_events.find(elem => elem.event?.id === currentId);
      if (current && current.role) {
        validatePath(current.role,currentPath) === true ?
        setCanSee(true) : router.push(`/${currentId}/${getBasePath(current.role)}`);
      } else {
        router.push("/contests");
      }
    }
  }, [user]);

  console.log(playerInfo);
  if(!canSee || loading){
    return <LoadingComponent/>;
  }

  return(
    <>
      <HeaderComponent/>
      <div className="grid justify-center items-center py-32 px-2 text-center">
        <p className="text-primary font-semibold text-xl">N SEI OQ COLOCAR</p>
        <p className="text-slate-700">Você não está inscrito em nenhuma chave no momento.</p>
      </div>
      <EventNavBarComponent/>
    </>
  );
}