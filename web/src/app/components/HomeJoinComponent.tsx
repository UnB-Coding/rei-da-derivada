import React from "react";
import EventsComponent from "./EventsComponent";

const HomeJoinComponent = () => {
    return (
        <div className="grid justify-center items-center pb-28 pt-32">
        <EventsComponent
        type="none"
        description="Insira abaixo o token fornecido pelo organizador do evento."
        placeholder="Ex: RRDD-TOKEN-1234"
        title="criar um evento"
        useEmail={false}
        />
      <EventsComponent 
        type="bla" 
        description="Insira abaixo o e-mail utilizado na inscrição do evento e o token." 
        placeholder="Ex: RRDD-TOKEN-1234" 
        title="participar de um evento" 
        useEmail={true}
        />
        <EventsComponent 
        type="bla" 
        description="Insira abaixo o e-mail utilizado na inscrição do evento e o token." 
        placeholder="Ex: RRDD-TOKEN-1234" 
        title="Entrar como monitor" 
        useEmail={true}
        />
        </div>
    );
};

export default HomeJoinComponent;