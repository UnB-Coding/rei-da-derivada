'use client'
import { useContext, useEffect } from "react";
import { UserContext } from "@/app/contexts/UserContext";
import HeaderComponent from "@/app/components/HeaderComponent";
import NavBarComponent from "@/app/components/NavBarComponent";
import LoadingComponent from "@/app/components/LoadingComponent";
import Contests from "@/app/components/Contests";
import { useRouter } from "next/navigation";

export default function AllContests() {
  const router = useRouter();
  const { user, loading, setLoading } = useContext(UserContext);

  useEffect(() => {
    if (!user.access && !loading) {
      router.push("/");
    }
  }, [user]);
  
  return loading ? <LoadingComponent/> :
    <>
        <HeaderComponent/>
          <Contests/>
        <NavBarComponent/>
    </>
    
  
}