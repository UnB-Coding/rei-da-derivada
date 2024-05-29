import React from 'react';
import Image from 'next/image';

const HeaderComponent = (props) => {
    return (
      <div className=" pt-10 flex justify-between items-center px-9">
        <Image className="w-20 h-20 rounded-[10px]" src={props.profile} alt="Foto de perfil do usuário" width="250" height="250" />
          <div className="justify-between">
            <h2 className="text-lg font-normal text-slate-600">Seja bem-vindo(a)</h2>
            <h2 className="text-2xl font-semibold "> {props.name}</h2>
        </div>
        <Image className="w-14 h-14" src={props.logo} alt="Logo do evento" width="45" height="45" />
      </div>
    );
};

export default HeaderComponent;