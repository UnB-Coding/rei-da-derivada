'use client'
import { useContext, useEffect, useState } from "react";
import { UserContext } from "@/app/contexts/UserContext";
import { useRouter, usePathname } from "next/navigation";
import { Toast, toast } from "react-hot-toast";
import LoadingComponent from "@/app/components/LoadingComponent";
import HeaderComponent from "@/app/components/HeaderComponent";
import ActiveSumulaComponent from "@/app/components/ActiveSumulaComponent";
import EventNavBarComponent from "@/app/components/EventNavBarComponent";
import validatePath from "@/app/utils/validadePath";
import getBasePath from "@/app/utils/getBasePath";

export default function Sumula() {
  const { user, loading } = useContext(UserContext);
  const [ canSee, setCanSee ] = useState<boolean>(false);
  const router = useRouter();
  const params = usePathname().split("/");
  const currentId = parseInt(params[1]);
  const currentPath = params[2];
  const [ userType, setUserType ] = useState<UserType>('common');

  type UserType = 'player' | 'staff' | 'manager' | 'admin' | 'common';

  useEffect(() => {
    if (!user.access && !loading) {
      router.push("/");
    } else if (user.all_events) {
      const current = user.all_events.find(elem => elem.event?.id === currentId);
      if (current && current.role) {
        const isValidPath = validatePath(current.role, currentPath);
        if(isValidPath){
          setUserType(current.role as UserType);
          setCanSee(true);
        } else {
          router.push(`/${currentId}/${getBasePath(current.role)}`);
        }
      } else {
        router.push("/contests");
      }
    }
  }, [user]);

  if(!canSee || loading){
    return <LoadingComponent/>;
  }

  return( 
    <>
        <HeaderComponent/>
        <ActiveSumulaComponent/>
        <EventNavBarComponent userType={userType}/>
    </>
  );
}