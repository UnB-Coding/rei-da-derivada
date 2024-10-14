import React from 'react';
import Image from 'next/image';
import { useContext } from 'react';
import { UserContext } from "@/app/contexts/UserContext";
import logo from '@/app/assets/logo.png';

const HeaderComponent = () => {
    const { user } = useContext(UserContext);
    return (
      <div className=" pt-10 flex justify-between items-center px-9 pb-4  backdrop-blur-2xl w-full h-32 fixed top-0 z-10">
        <Image draggable="false" className="w-20 h-20 rounded-[10px]" src={user.picture_url} alt="Foto de perfil do usuário" width="250" height="250" />
          <div className="justify-between absolute left-32">
            <h2 className="text-lg font-normal text-slate-600">Seja bem-vindo(a)</h2>
            <h2 className="text-2xl font-semibold text-slate-800"> {user.first_name}</h2>
        </div>
        <Image draggable="false" className="w-14 h-14" src={logo} alt="Logo do evento" width="45" height="45" />
      </div>
    );
};

export default HeaderComponent;