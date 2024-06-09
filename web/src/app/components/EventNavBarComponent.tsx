import React from "react";
import { useRouter} from 'next/navigation';

const EventNavBarComponent = () => {
    const router = useRouter();
    // this navbar is just a prototype, it will be changed in other branch :)
    return (
        <div className="bg-secondary w-full items-center justify-around  sm:px-30 lg:px-1/4 xl:px-1/5 h-20 fixed bottom-0 flex">
            <div className={`bg-primary w-[124px] h-[6px] rounded-full absolute top-0`}/>
            <p onClick={() => {router.push('./admin')}}>ADM</p>
            <p onClick={() => {router.push('./profile')}}>PFL</p>
            <p onClick={() => {router.push('./sumula')}}>SML</p>
            <p onClick={() => {router.push('./results')}}>RST</p>
        </div>
    );
};

export default EventNavBarComponent;