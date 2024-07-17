import React from "react";
import EventsComponent from "./EventsComponent";
import eventLogin from "../utils/api/eventLogin";
import staffLogin from "../utils/api/staffLogin";
import createEvent from "../utils/api/createEvent";

const HomeJoinComponent = () => {
  function seila(){
    console.log("oi")
  }
    return (
        <div className="grid justify-center items-center pb-28 pt-32">
        <EventsComponent
        type="create"
        description="Insira abaixo o nome do evento e o token fornecido pelo organizador do evento."
        optionalph="Ex: Nome do evento"
        placeholder="Ex: RRDD-TOKEN-1234"
        title="criar um evento"
        useEmail={true}
        function={createEvent}
        />
      <EventsComponent 
        type="join" 
        description="Insira abaixo o e-mail utilizado na inscrição do evento e o token." 
        optionalph="Ex: example@email.com"
        placeholder="Ex: RRDD-TOKEN-1234" 
        title="participar de um evento" 
        useEmail={true}
        function={eventLogin}
        />
        <EventsComponent 
        type="staff" 
        description="Insira abaixo o e-mail utilizado na inscrição do evento e o token." 
        placeholder="Ex: RRDD-TOKEN-1234" 
        title="Entrar como staff" 
        useEmail={false}
        function={staffLogin}
        />
        </div>
    );
};

export default HomeJoinComponent;