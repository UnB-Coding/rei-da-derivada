import React from 'react';
import homefill from '@/app/assets/home_fill.png';
import homeline from '@/app/assets/home_line.png';
import calendarfill from '@/app/assets/calendar_fill.png';
import calendarline from '@/app/assets/calendar_line.png';
import Image from 'next/image';
import { usePathname } from 'next/navigation';
import { useRouter } from 'next/navigation';

const NavBarComponent = () => {
    const router = useRouter();
    const routpath = usePathname();
    const barPosition = {
        "/home": "left-11",
        "/contests": "right-11",
    };

    return (
        <div className="bg-secondary w-full items-center justify-evenly  sm:px-30 lg:px-1/4 xl:px-1/5 h-20 fixed bottom-0 flex">
            <div className={`bg-primary w-[124px] h-[6px] rounded-full absolute top-0  ${barPosition[routpath]}`}/>
            <Image onClick={() => {router.push("/home")}} src={routpath == '/home' ? homefill : homeline} alt="home icons" width={36} height={36} />
            <Image onClick={() => {router.push("/contests")}} src={routpath == '/contests' ? calendarfill : calendarline} alt="calendar icons" width={36} height={36}/>
        </div>
    );
};

export default NavBarComponent;