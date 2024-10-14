import React, { useState, useContext, useEffect } from "react";
import { UserContext } from "@/app/contexts/UserContext";
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from "@/app/components/ui/dialog";
import { Button } from "@/app/components/ui/button";
import { Switch } from "@nextui-org/react";
import { Checkbox } from "@nextui-org/checkbox";
import toast from "react-hot-toast";
import request from "@/app/utils/request";
import { settingsWithAuth } from "@/app/utils/settingsWithAuth";
import getAllPlayers from "@/app/utils/api/getAllPlayers";
import { usePathname } from "next/navigation";


export default function PublishResults() {
    const { user } = useContext(UserContext);
    const [ isOpen, setIsOpen ] = useState<boolean>(false);
    const [ top1, setTop1 ] = useState<string>("");
    const [ top2, setTop2 ] = useState<string>("");
    const [ top3, setTop3 ] = useState<string>("");
    const [ top4, setTop4 ] = useState<string>("");
    const [ ambassor, setAmbassor ] = useState<string>("");
    const [ paladin, setPaladin ] = useState<string>("");
    const [ postTop4, setPostTop4 ] = useState<boolean>(false);
    const [ postImortais, setPostImortais ] = useState<boolean>(false);
    const [ postPaladin, setPostPaladin ] = useState<boolean>(false);
    const [ postAmbassor, setPostAmbassor ] = useState<boolean>(false);
    const [ confirm, setConfirm ] = useState<boolean>(false);
    const [ allPlayers, setAllPlayers ] = useState<any[]>([]);
    const eventId = usePathname().split("/")[1];

    const handleClose = () => {
        setPostTop4(false);
        setPostImortais(false);
        setPostPaladin(false);
        setPostAmbassor(false);
        setPaladin("");
        setAmbassor("");
        setTop1("");
        setTop2("");
        setTop3("");
        setTop4("");
        setConfirm(false);
    }

    const handlePublish = async () => {
        const body = {};

    }

    const getPlayers = async () => {
        const players = await getAllPlayers(eventId, user.access);
        setAllPlayers(players);
    }

    useEffect(() => {
        if(isOpen) {
            getPlayers();
        }
    },[isOpen])

    return (
        <div className="mt-4 flex justify-center">
            <Dialog open={isOpen} onOpenChange={setIsOpen}>
                <DialogTrigger>
                    <div className="w-[300px] h-[50px] bg-primary text-white font-semibold rounded-lg flex items-center justify-center cursor-pointer" onClick={() => setIsOpen(true)}>
                        Publicar resultados
                    </div>
                </DialogTrigger>
                <DialogContent onCloseAutoFocus={() => handleClose()} className="max-h-[80vh] overflow-y-auto items-center justify-center">
                    <DialogHeader>
                        <DialogTitle className="text-primary font-semibold pb-4 text-2xl">PUBLICAR RESULTADOS</DialogTitle>
                    </DialogHeader>
                    <DialogDescription className="text-base">
                        Selecione os resultados que deseja publicar
                    </DialogDescription>
                    <Switch defaultSelected={false} onValueChange={() => setPostTop4(!postTop4)}>
                        <p>Publicar TOP 4</p>
                    </Switch>
                    {postTop4 && (
                        <div className="grid gap-2">
                            <input onChange={(e) => setTop1(e.target.value)} className="border-[1.5px] border-blue-500 w-64 h-10 rounded-lg pl-5" type="text" placeholder="Nome do Top 1" />
                            <input onChange={(e) => setTop2(e.target.value)} className="border-[1.5px] border-blue-500 w-64 h-10 rounded-lg pl-5" type="text" placeholder="Nome do Top 2" />
                            <input onChange={(e) => setTop3(e.target.value)} className="border-[1.5px] border-blue-500 w-64 h-10 rounded-lg pl-5" type="text" placeholder="Nome do Top 3" />
                            <input onChange={(e) => setTop4(e.target.value)} className="border-[1.5px] border-blue-500 w-64 h-10 rounded-lg pl-5" type="text" placeholder="Nome do Top 4" />
                        </div>
                    )}
                    <Switch defaultSelected={false} onValueChange={() => setPostPaladin(!postPaladin)}>
                        <p>Publicar Paladino</p>
                    </Switch>
                    {postPaladin && (
                        <input onChange={(e) => setPaladin(e.target.value)} className="border-[1.5px] border-blue-500 w-64 h-10 rounded-lg pl-5" type="text" placeholder="Nome do paladino" />
                    )}
                    <Switch defaultSelected={false} onValueChange={() => setPostAmbassor(!postAmbassor)}>
                        <p>Publicar Embaixador</p>
                    </Switch>
                    {postAmbassor && (
                        <input onChange={(e) => setAmbassor(e.target.value)} className="border-[1.5px] border-blue-500 w-64 h-10 rounded-lg pl-5" type="text" placeholder="Nome do embaixador" />
                    )}
                    <Switch defaultSelected={false} onValueChange={() => setPostImortais(!postImortais)}>
                        <p>Publicar Imortais</p>
                    </Switch>
                    {postImortais && (
                        <p className="text-base">Serão selecionados os 3 jogadores com as maiores pontuações</p>
                    )}
                    <Checkbox className="mt-2" size="md" radius="sm" isSelected={confirm} onValueChange={setConfirm}>
                        Confirmo que os dados estão corretos
                    </Checkbox>
                    <DialogFooter className="gap-2">
                        <Button variant="outline" className="bg-slate-200" onClick={() => setIsOpen(false)}>Cancelar</Button>
                        <Button disabled={!confirm} onClick={handlePublish}>Publicar</Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>
        </div>
    );
}