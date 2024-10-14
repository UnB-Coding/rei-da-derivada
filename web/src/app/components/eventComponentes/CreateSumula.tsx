import React, { useState, useContext, useEffect } from "react";
import Image from "next/image";
import { usePathname } from "next/navigation";
import { Switch, Listbox, ListboxItem } from "@nextui-org/react";
import CloseIcon from "@/app/assets/close_icon.png";
import Remove from "@/app/assets/remove.png";
import Add from "@/app/assets/add.png";
import { UserContext } from "@/app/contexts/UserContext";
import getAllPlayers from "@/app/utils/api/getAllPlayers";
import getStaffList from "@/app/utils/api/getStaffList";
import createQualifierSum from "@/app/utils/api/createQualifierSum";
import createImortalSum from "@/app/utils/api/createImortalSum";
import { Plus, Minus } from "lucide-react";
import capitalize from "@/app/utils/capitalize";
interface player {
    id: number;
    full_name: string;
}

interface CreateSumulaProps {
    buttonName: string;
    isImortal: boolean;
}

export const ListboxWrapper = ({ children }: { children: React.ReactNode }) => (
    <div className="w-full max-w-[260px] border-small px-1 py-2 rounded-small border-default-200 dark:border-default-100">
        {children}
    </div>
);

export default function CreateSumula(props: CreateSumulaProps) {
    const currentId = usePathname().split("/")[1];
    const { user } = useContext(UserContext);
    const [playerName, setplayerName] = useState<string>("");
    const [staffName, setStaffName] = useState<string>("");
    const [sumName, setSumName] = useState<string>("");
    const [isOpen, setIsOpen] = useState<boolean>(false);
    const [isImortal, setIsImortal] = useState<boolean>(false);
    const [staffs, setStaffs] = useState<any[]>([]);
    const [players, setPlayers] = useState<player[]>([]);
    const [classfiedPlayers, setClassfiedPlayers] = useState<player[]>([]);

    const [currentStaffs, setCurrentStaffs] = useState<any[]>([]);
    const [currentPlayers, setCurrentPlayers] = useState<player[]>([]);

    const MAX_LEN = 30;

    const cleatData = () => {
        setSumName("");
        setplayerName("");
        setStaffName("");
        setCurrentPlayers([]);
        setCurrentStaffs([]);
    }

    useEffect(() => {
        const fetchPlayers = async () => {
            if (isOpen) {
                try {
                    const playersList = await getAllPlayers(currentId, user.access);
                    const classfiedPlayers = playersList.filter((player: any) => player.is_imortal === false);
                    setPlayers(playersList);
                    setClassfiedPlayers(classfiedPlayers);
                } catch (error) {
                    console.log("Erro ao processar a requisição:", error);
                }
            }
        }
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
        fetchPlayers();
        fetchStaffList();
    }, [isOpen]);

    const handleClickRemovePlayer = (playerToRemove: player) => {
        setCurrentPlayers((prevPlayers) =>
            prevPlayers.filter((player) => player.id !== playerToRemove.id)
        );
    };

    const handleClickAddPlayer = (playerToAdd: player) => {
        setCurrentPlayers((prevPlayers) => [...prevPlayers.filter((player) => player.id !== playerToAdd.id), playerToAdd]);
    }

    const handleClickAddStaff = (staffToAdd: any) => {
        setCurrentStaffs((prevStaffs) =>
            [...prevStaffs.filter((staff) => staff.id !== staffToAdd.id), staffToAdd]
        );
    }

    const handleClickRemoveStaff = (staffToRemove: any) => {
        setCurrentStaffs((prevStaffs) =>
            prevStaffs.filter((staff) => staff.id !== staffToRemove.id)
        );
    };

    const filteredPlayers = (isImortal || props.isImortal ? players : classfiedPlayers)
        .filter(item => item?.full_name?.toLowerCase().includes(playerName?.toLowerCase()))
        .slice(0, 4);

    return (
        <div className="mt-4 flex justify-center">
            <button className=" w-[300px] h-[50px] bg-primary text-white font-semibold rounded-lg" onClick={() => setIsOpen(!isOpen)}>{props.buttonName}</button>
            {isOpen && (
                <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-40 z-20">
                    <div className="overflow-y-auto relative bg-white px-12 py-12 h-[80%] md:w-[600px] rounded-lg shadow-lg grid items-center justify-center">
                        <button className="abso</div>lute top-2 right-2 pt-0" onClick={() => { setIsOpen(!isOpen); setCurrentPlayers([]); setCurrentStaffs([]); setplayerName(""); setStaffName(""); setIsImortal(false); }}>
                            <Image src={CloseIcon} alt="close icon" width={30} height={30} />
                        </button>
                        <p className="text-primary font-semibold pb-4">CRIAR NOVA SÚMULA {props.isImortal ? "DE IMORTAIS" : "CLASSIFICATÓRIA"}</p>
                        <div className="grid gap-2 pb-8 ">
                            {!props.isImortal && <Switch defaultSelected={false} onValueChange={() => setIsImortal(!isImortal)}>
                                Utilizar suplentes
                            </Switch>}
                            {!props.isImortal && (
                                <>
                                    <label htmlFor="sumName">Nome da súmula</label>
                                    <input onChange={e => setSumName(e.target.value)} className="w-[300px] h-[40px] border-[1.5px] border-primary bg-neutral-100 rounded-lg pl-4" type="text" placeholder="Nome" />
                                </>
                            )}
                            <label htmlFor="staffName" className="text-primary font-medium">ADICIONAR STAFF'S</label>
                            <input onChange={e => setStaffName(e.target.value)} className="w-[300px] h-[40px] border-[1.5px] border-primary bg-neutral-100 rounded-lg pl-4" type="text" placeholder="Pesquisar" />
                            <Listbox classNames={{ base: "max-w-xs", list: "max-h-[300px] overflow-auto" }} items={staffs.filter(item => item?.full_name?.toLowerCase().includes(staffName?.toLocaleLowerCase())).slice(0, 4)} variant="flat" emptyContent="Nenhum staff encontrado">
                                {(item) => (
                                    <ListboxItem key={item.id} variant="flat" className="bg-slate-100 py-2">
                                        <div className="flex gap-2 justify-between items-center">
                                            <span className="text-base">{capitalize(item.full_name.slice(0, MAX_LEN))}</span>
                                            <button onClick={() => { handleClickAddStaff(item) }} className="bg-primary text-white font-semibold rounded-lg p-2" aria-label="Adicionar staff">
                                                <Plus size={24} />
                                            </button>
                                        </div>
                                    </ListboxItem>
                                )}
                            </Listbox>
                            <p>Staff's selecionados</p>
                            <Listbox classNames={{ base: "max-w-xs", list: "max-h-[300px] overflow-auto" }} items={currentStaffs} variant="flat" emptyContent="Nenhum staff escolhido">
                                {(item) => (
                                    <ListboxItem key={item.id} variant="flat" className="bg-slate-100 py-2">
                                        <div className="flex gap-2 justify-between items-center">
                                            <span className="text-base">{capitalize(item.full_name.slice(0, MAX_LEN))}</span>
                                            <button onClick={() => { handleClickRemoveStaff(item) }} className="bg-primary text-white font-semibold rounded-lg p-2" aria-label="Remover staff">
                                                <Minus size={24} />
                                            </button>
                                        </div>
                                    </ListboxItem>
                                )}
                            </Listbox>
                            <label htmlFor="playerName" className="text-primary font-medium">ADICIONAR JOGADORES</label>
                            <input onChange={e => setplayerName(e.target.value)} className="w-[300px] h-[40px] border-[1.5px] border-primary bg-neutral-100 rounded-lg pl-4" type="text" placeholder="Pesquisar" />
                            <Listbox classNames={{ base: "max-w-xs", list: "max-h-[300px] overflow-auto" }} items={filteredPlayers} variant="flat" emptyContent="Nenhum jogador encontrado">
                                {(item) => (
                                    <ListboxItem key={item.id} variant="flat" className="bg-slate-100 py-2">
                                        <div className="flex gap-2 justify-between items-center">
                                            <span className="text-base">{capitalize(item.full_name.slice(0, MAX_LEN))}</span>
                                            <button onClick={() => { handleClickAddPlayer(item) }} className="bg-primary text-white font-semibold rounded-lg p-2" aria-label="Adicionar jogador">
                                                <Plus size={24} />
                                            </button>
                                        </div>
                                    </ListboxItem>
                                )}
                            </Listbox>
                            <p>Jogadores selecionados</p>
                            <Listbox classNames={{ base: "max-w-xs", list: "max-h-[300px] overflow-auto" }} items={currentPlayers} variant="flat" emptyContent="Nenhum jogador escolhido">
                                {(item) => (
                                    <ListboxItem key={item.id} variant="flat" className="bg-slate-100 py-2">
                                        <div className="flex gap-2 justify-between items-center">
                                            <span className="text-base">{capitalize(item.full_name.slice(0, MAX_LEN))}</span>
                                            <button onClick={() => { handleClickRemovePlayer(item) }} className="bg-primary text-white font-semibold rounded-lg p-2" aria-label="Remover jogador">
                                                <Minus size={24} />
                                            </button>
                                        </div>
                                    </ListboxItem>
                                )}
                            </Listbox>
                        </div>
                        <button onClick={() => {
                            (props.isImortal ?
                                createImortalSum(sumName, currentId, currentPlayers, currentStaffs, user.access) :
                                createQualifierSum(sumName, currentId, currentPlayers, currentStaffs, user.access)); cleatData()
                        }} className="w-[300px] h-[50px] bg-primary text-white font-semibold rounded-lg ">Adicionar</button>
                    </div>
                </div>
            )}
        </div>
    );
}