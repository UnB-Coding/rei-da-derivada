import React, { useState, useContext } from "react";
import { usePathname } from "next/navigation";
import Image from "next/image";
import CloseIcon from "@/app/assets/close_icon.png"
import addNewPlayers from "@/app/utils/api/addNewPlayers";
import { UserContext } from "@/app/contexts/UserContext";
import { Checkbox } from "@nextui-org/checkbox";

export default function AddPlayerComponent() {
    const { user } = useContext(UserContext);
    const [visible, setVisible] = useState<boolean>(false);
    const [fullName, setFullName] = useState<string>("");
    const [isImortal, setIsImortal] = useState<boolean>(false);
    const [socialName, setSocialName] = useState<string>("");
    const [registrationEmail, setRegistrationEmail] = useState<string>("");
    const eventId = usePathname().split("/")[1];

    return (
        <div className="mt-4 flex justify-center">
            <button className=" w-[300px] h-[50px] bg-primary text-white font-semibold rounded-lg" onClick={() => setVisible(!visible)}>Adicionar jogador</button>
            {visible && (
                <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-40 z-20">
                    <div className="relative bg-white px-12 py-16 rounded-lg shadow-lg">
                        <button className="absolute top-2 right-2 pt-0" onClick={() => { setVisible(!visible) }}>
                            <Image src={CloseIcon} alt="close icon" width={30} height={30} />
                        </button>
                        <p className="text-primary font-semibold pb-4">ADICIONAR NOVO JOGADOR</p>
                        <div className="grid gap-2 pb-8">
                            <p>Nome completo</p>
                            <input onChange={e => setFullName(e.target.value)} className="w-[300px] h-[40px] border-[1.5px] border-primary bg-neutral-100 rounded-lg pl-4" type="text" placeholder="Nome" />
                            <p>Nome social</p>
                            <input onChange={e => setSocialName(e.target.value)} className="w-[300px] h-[40px] border-[1.5px] border-primary bg-neutral-100 rounded-lg pl-4" type="text" placeholder="Nome social" />
                            <p>Email de inscrição</p>
                            <input onChange={e => setRegistrationEmail(e.target.value)} className="w-[300px] h-[40px] bg-neutral-100 border-[1.5px] border-primary rounded-lg pl-4" type="email" placeholder="Ex: exemplo@email.com" />
                            <Checkbox className="mt-2"  defaultSelected size="lg" radius="sm" isSelected={isImortal} onValueChange={setIsImortal}>
                                O novo jogador é imortal?
                            </Checkbox>
                        </div>
                        <button onClick={() => { addNewPlayers(fullName, socialName, registrationEmail, eventId, isImortal, user.access) }} className="w-[300px] h-[50px] bg-primary text-white font-semibold rounded-lg ">Adicionar</button>
                    </div>
                </div>
            )}
        </div>
    );
}