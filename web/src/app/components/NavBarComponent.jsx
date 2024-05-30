import React from 'react';
import homefill from '@/app/assets/home_fill.png';
import calendarline from '@/app/assets/calendar_line.png';
import Image from 'next/image';

const NavBarComponent = () => {
    return (
        <div className="bg-secondary w-full items-center justify-between px-20 sm:px-30 lg:px-1/4 xl:px-1/5 h-28 fixed bottom-0 flex">
            <div className="bg-primary w-[124px] h-[6px] rounded-full absolute top-0 left-10"/>
            <Image onClick={() => {console.log("deubom")}} src={homefill} alt="home icons" width={42} height={42} />
            <Image onClick={() => {console.log("deubom")}} src={calendarline} alt="calendar icons" width={42} height={42}/>
      </div>
    );
};

export default NavBarComponent;