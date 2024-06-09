import React from "react";
import Image from "next/image";
import adminl from "@/app/assets/admin_line.png";
import adminf from "@/app/assets/admin_fill.png";
import profilel from "@/app/assets/profile_line.png";
import profilef from "@/app/assets/profile_fill.png";
import sumulal from "@/app/assets/sumula_line.png";
import sumulaf from "@/app/assets/sumula_fill.png";
import resultl from "@/app/assets/result_line.png";
import resultf from "@/app/assets/result_fill.png";
import { useRouter,usePathname } from 'next/navigation';


const EventNavBarComponent = () => {
    const router = useRouter();
    const currentPath = usePathname().split('/')[2];
    // this navbar is just a prototype, it will be changed in other branch :)
    return (
        <div className="bg-secondary w-full items-center justify-around  sm:px-30 lg:px-1/4 xl:px-1/5 h-20 fixed bottom-0 flex">
            <div className={`bg-primary w-[124px] h-[6px] rounded-full absolute top-0`}/>
            <Image onClick={() => {router.push('./profile')}}src={currentPath === 'profile' ? profilef : profilel} alt="profile" width={36} height={36}/>
            <Image onClick={() => {router.push('./results')}}src={currentPath === 'results' ? resultf : resultl} alt="results" width={36} height={36}/>
            <Image onClick={() => {router.push('./sumula')}}src={currentPath === 'sumula' ? sumulaf : sumulal} alt="sumula" width={36} height={36}/>
            <Image onClick={() => {router.push('./admin')}}src={currentPath === 'admin' ? adminf : adminl} alt="admin" width={36} height={36}/>
        </div>
    );
};

export default EventNavBarComponent;