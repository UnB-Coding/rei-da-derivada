import React from 'react';
import homefill from '@/app/assets/home_fill.png';
import homeline from '@/app/assets/home_line.png';
import calendarfill from '@/app/assets/calendar_fill.png';
import calendarline from '@/app/assets/calendar_line.png';
import Image from 'next/image';
import { usePathname } from 'next/navigation';

const NavBarComponent = () => {
    const routpath = usePathname();
    const barPosition = {
        "/home": "left-10",
        "/event": "right-10",
    };

    return (
        console.log(usePathname()),
        <div className="bg-secondary w-full items-center justify-between px-20 sm:px-30 lg:px-1/4 xl:px-1/5 h-20 fixed bottom-0 flex">
            <div className={`bg-primary w-[124px] h-[6px] rounded-full absolute top-0 transition-all ${barPosition[routpath]}`}/>
            <Image onClick={() => {console.log("deubom")}} src={homefill} alt="home icons" width={36} height={36} />
            <Image onClick={() => {console.log("deubom")}} src={calendarline} alt="calendar icons" width={36} height={36}/>
      </div>
    );
};

export default NavBarComponent;