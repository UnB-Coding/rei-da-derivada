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
import { Autocomplete, AutocompleteItem } from "@nextui-org/react";
import { isAxiosError } from "axios";


export default function PublishResults() {
    const { user } = useContext(UserContext);
    const [isOpen, setIsOpen] = useState<boolean>(false);
    const [top1, setTop1] = useState<any | null>(null);
    const [top2, setTop2] = useState<any | null>(null);
    const [top3, setTop3] = useState<any | null>(null);
    const [top4, setTop4] = useState<any | null>(null);
    const [ambassor, setAmbassor] = useState<any | null>(null);
    const [paladin, setPaladin] = useState<any | null>(null);
    const [postTop4, setPostTop4] = useState<boolean>(false);
    const [postImortais, setPostImortais] = useState<boolean>(false);
    const [postPaladin, setPostPaladin] = useState<boolean>(false);
    const [postAmbassor, setPostAmbassor] = useState<boolean>(false);
    const [confirm, setConfirm] = useState<boolean>(false);
    const [allPlayers, setAllPlayers] = useState<any[]>([]);
    const eventId = usePathname().split("/")[1];

    interface Player {
        full_name: string;
        id: number;
    }

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
        if (postAmbassor || postPaladin || postTop4) {
            const body: any = {}
            if (postTop4) {
                const top4List = [{ player_id: top1.id }, { player_id: top2.id }, { player_id: top3.id }, { player_id: top4.id }];
                body.top4 = top4List;
            }
            if (postPaladin) {
                body.paladin = { player_id: paladin.id }
            }
            if (postAmbassor) {
                body.ambassor = { player_id: ambassor.id }
            }
            try {
                const response = await request.put(`/api/results/?event_id=${eventId}`, body, settingsWithAuth(user.access));
                if (response.status === 200) {
                    toast.success("Resultados publicados com sucesso.")
                }
            } catch (error) {
                if (isAxiosError(error)) {
                    const errorMessage = error.response?.data.errors || "Erro desconhecido";
                    toast.error(errorMessage);
                }
            }
        }
        if (postImortais) {
            try {
                const response = await request.put(`/api/publish/results/imortals/?event_id=${eventId}`, {}, settingsWithAuth(user.access));
                if (response.status === 200) {
                    toast.success("Imortais publicados com sucesso.")
                }
            } catch (error) {
                if (isAxiosError(error)) {
                    const errorMessage = error.response?.data.errors || "Erro desconhecido";
                    toast.error(errorMessage);
                }
            }
        }
    }

    const getPlayers = async () => {
        const players = await getAllPlayers(eventId, user.access);
        setAllPlayers(players);
    }

    useEffect(() => {
        if (isOpen) {
            getPlayers();
        }
    }, [isOpen]);

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
                            <Autocomplete style={{ zIndex: 100, pointerEvents: 'auto' }} placeholder="Nome do Top 1"
                                onInputChange={(item) => {
                                    const selectedPlayer = allPlayers.find((player) => player.full_name === item);
                                    setTop1(selectedPlayer);
                                }}>
                                {allPlayers.map((player) => (
                                    <AutocompleteItem style={{ zIndex: 101, pointerEvents: 'auto' }} key={player.id}>{player.full_name}</AutocompleteItem>
                                ))}
                            </Autocomplete>
                            <Autocomplete style={{ zIndex: 100, pointerEvents: 'auto' }} placeholder="Nome do Top 2"
                                onInputChange={(item) => {
                                    const selectedPlayer = allPlayers.find((player) => player.full_name === item); setTop2(selectedPlayer)
                                }}>
                                {allPlayers.map((player) => (
                                    <AutocompleteItem style={{ zIndex: 101, pointerEvents: 'auto' }} key={player.id}>{player.full_name}</AutocompleteItem>
                                ))}
                            </Autocomplete>
                            <Autocomplete style={{ zIndex: 100, pointerEvents: 'auto' }} placeholder="Nome do Top 3" onInputChange={(item) => {
                                const selectedPlayer = allPlayers.find((player: Player) => player.full_name === item); setTop3(selectedPlayer)
                            }}>
                                {allPlayers.map((player) => (
                                    <AutocompleteItem style={{ zIndex: 101, pointerEvents: 'auto' }} key={player.id}>{player.full_name}</AutocompleteItem>
                                ))}
                            </Autocomplete>
                            <Autocomplete style={{ zIndex: 100, pointerEvents: 'auto' }} placeholder="Nome do Top 4" onInputChange={(item) => {
                                const selectedPlayer = allPlayers.find((player: Player) => player.full_name === item); setTop4(selectedPlayer)
                            }}>
                                {allPlayers.map((player) => (
                                    <AutocompleteItem style={{ zIndex: 101, pointerEvents: 'auto' }} key={player.id}>{player.full_name}</AutocompleteItem>
                                ))}
                            </Autocomplete>
                        </div>
                    )}
                    <Switch defaultSelected={false} onValueChange={() => setPostPaladin(!postPaladin)}>
                        <p>Publicar Paladino</p>
                    </Switch>
                    {postPaladin && (
                        <Autocomplete style={{ zIndex: 100, pointerEvents: 'auto' }} placeholder="Nome do Paladino" onInputChange={(item) => {
                            const selectedPlayer = allPlayers.find((player: Player) => player.full_name === item); setPaladin(selectedPlayer)
                        }}>
                            {allPlayers.map((player) => (
                                <AutocompleteItem style={{ zIndex: 101, pointerEvents: 'auto' }} key={player.id}>{player.full_name}</AutocompleteItem>
                            ))}
                        </Autocomplete>
                    )}
                    <Switch defaultSelected={false} onValueChange={() => setPostAmbassor(!postAmbassor)}>
                        <p>Publicar Embaixador</p>
                    </Switch>
                    {postAmbassor && (
                        <Autocomplete style={{ zIndex: 100, pointerEvents: 'auto' }} placeholder="Nome do Embaixador" onInputChange={(item) => {
                            const selectedPlayer = allPlayers.find((player: Player) => player.full_name === item); setAmbassor(selectedPlayer)
                        }}>
                            {allPlayers.map((player) => (
                                <AutocompleteItem style={{ zIndex: 101, pointerEvents: 'auto' }} key={player.id}>{player.full_name}</AutocompleteItem>
                            ))}
                        </Autocomplete>
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