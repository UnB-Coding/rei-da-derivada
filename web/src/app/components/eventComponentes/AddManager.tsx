import React, { useState, useEffect, useContext } from "react";
import { usePathname } from "next/navigation";
import { UserContext } from "@/app/contexts/UserContext";
import Image from "next/image";
import CloseIcon from "@/app/assets/close_icon.png"
import getStaffList from "@/app/utils/api/getStaffList";
import setAsManager from "@/app/utils/api/setAsManager";
import { Autocomplete, AutocompleteItem } from "@nextui-org/react";

export default function AddManager() {
    const { user } = useContext(UserContext);
    const [isOpen, setIsOpen] = useState<boolean>(false);
    const [staffs, setStaffs] = useState<any[]>([]);
    const [currentStaff, setCurrentStaff] = useState<any>();
    const currentId = usePathname().split("/")[1];

    useEffect(() => {
        const fetchStaffList = async () => {
            if (isOpen) {
                try {
                    const staffList = await getStaffList(currentId, user.access);
                    setStaffs(staffList);
                } catch (error) {
                    console.error("Erro ao processar a requisição:", error);
                }
            }
        };
        fetchStaffList();
    }, [isOpen]);

    return (
        <div className="mt-4 flex justify-center">
            <button className=" w-[300px] h-[50px] bg-primary text-white font-semibold rounded-lg" onClick={() => setIsOpen(!isOpen)}>Adicionar gerente</button>
            {isOpen && (
                <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-40 z-20">
                    <div className="relative bg-white px-12 py-10 rounded-lg shadow-lg">
                        <button className="absolute top-2 right-2 pt-0" onClick={() => { setIsOpen(!isOpen) }}>
                            <Image src={CloseIcon} alt="close icon" width={30} height={30} />
                        </button>
                        <p className="text-primary font-semibold pb-4">ADICIONAR GERENTE</p>
                        <div className="grid gap-2 pb-8">
                            <Autocomplete
                                variant="bordered"
                                defaultItems={staffs.filter(elem => elem.is_manager === false)}
                                placeholder="Buscar por monitor"
                                className="max-w-xs mb-52"
                                onInputChange={(item) => {setCurrentStaff(staffs.find(elem => elem.full_name === item))}}
                            >
                                {(item) => <AutocompleteItem key={item.id}>{ item.full_name }</AutocompleteItem>}
                            </Autocomplete>
                        </div>
                        <button onClick={() => {setAsManager(currentStaff.registration_email, currentId, user.access)}} className="w-[300px] h-[50px] bg-primary text-white font-semibold rounded-lg mt-6">Adicionar</button>
                    </div>
                </div>
            )}
        </div>
    );
}