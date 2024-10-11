import React, { ReactNode } from 'react';
import Image from 'next/image';
import Arrow from '../assets/arrow.png';
import { useRouter } from 'next/navigation';  
import { HTMLProps } from 'react';  

interface ArrowButtonProps extends HTMLProps<HTMLButtonElement> {
    children?: React.ReactNode
};

const ArrowButton = ({ children, ...props }: ArrowButtonProps) =>{
    return (
        <button {...props} type='submit' className="bg-primary w-10 h-10 rounded-lg flex justify-center items-center">
            <Image src={Arrow} alt="home icons" width={40} height={40} />
        </button>
    );
}

export default ArrowButton;