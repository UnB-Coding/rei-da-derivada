import React from 'react';
import Image from 'next/image';
import Arrow from '../assets/arrow.png';
import { useRouter } from 'next/navigation';

const ArrowButton = (props) =>{
    const router = useRouter();
    return (
        <div onClick={() => {router.push(`${props.path}`)}} className="bg-primary w-10 h-10 rounded-lg flex justify-center items-center">
            <Image src={Arrow} alt="home icons" width={40} height={40} />
        </div>
    );
}

export default ArrowButton;