import React from 'react';
import Image from 'next/image';

const HeaderComponent = (props) => {
    return (
        <div className="flex justify-between items-center">
          <div className="flex pt-20 px-9">
            <Image className="w-20 h-20 rounded-[10px]" src={props.profile} alt="Foto de perfil do usuário" width="250" height="250" />
            <div className="px-[14px]">
              <h2 className="text-lg font-normal">Seja bem-vindo(a)</h2>
              <h2 className="text-xl font-semibold"> {props.name}</h2>
            </div>
            <Image className="w-14 h-14"src={props.logo} alt="Logo do evento" width="45" height="45" />
          </div>
        </div>
      );
};

export default HeaderComponent;