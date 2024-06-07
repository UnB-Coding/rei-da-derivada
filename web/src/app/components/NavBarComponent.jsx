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
        "/home": "left-10",
        "/contests": "right-10",
    };

    return (
        <div className="bg-secondary w-full items-center justify-around px-20 sm:px-30 lg:px-1/4 xl:px-1/5 h-20 fixed bottom-0 flex">
            <div className={`bg-primary w-[124px] h-[6px] rounded-full absolute top-0 transition-all ${barPosition[routpath]}` }/>
            <Image onClick={() => {router.push("/home")}} src={homefill} alt="home icons" width={36} height={36} />
            <Image onClick={() => {router.push("/contests")}} src={calendarline} alt="calendar icons" width={36} height={36}/>
      </div>
    );
};

export default NavBarComponent;