import React, { useState, useContext, useEffect } from "react";
import { UserContext } from "@/app/contexts/UserContext";
import { usePathname } from "next/navigation";
import { Trash2 } from "lucide-react";
import toast from "react-hot-toast";
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
import request from "@/app/utils/request";
import { settingsWithAuth } from "@/app/utils/settingsWithAuth";

export default function DeleteSumula() {
    const { user } = useContext(UserContext);
    const [isOpen, setIsOpen] = useState<boolean>(false);
    const [closedSumula, setClosedSumula] = useState<any[]>([]);
    const [selectedSumula, setSelectedSumula] = useState<any>(null);
    const [isConfirmOpen, setIsConfirmOpen] = useState<boolean>(false);

    const eventId = usePathname().split("/")[1];

    const getClosedSumula = async () => {
        if (isOpen) {
            const response = await request.get(`/api/sumula/?event_id=${eventId}`, settingsWithAuth(user.access));
            if (response.status === 200) {
                const closedSumulasClass = response.data.sumulas_classificatoria.filter((sumula: any) => sumula.active === false);
                const closedSumulasImortal = response.data.sumulas_imortal.filter((sumula: any) => sumula.active === false);
                const allClosedSumulas = closedSumulasClass.concat(closedSumulasImortal);
                setClosedSumula(allClosedSumulas);
            } else {
                console.error("Erro ao fazer a requisição:", response);
            }
        }
    }

    const handleDelete = async (id: number) => {
        const body = {
            "id": id
        }
        const response = await request.delete(`/api/sumula/?event_id=${eventId}`, {
            data: body,
            ...settingsWithAuth(user.access)
        });
        if (response.status === 200) {
            setClosedSumula(closedSumula.filter((sumula: any) => sumula.id !== id));
            toast.success("Súmula deletada com sucesso.");
        } else {
            toast.error("Erro ao deletar a súmula.");
            console.error("Erro ao fazer a requisição:", response);
        }
    }

    useEffect(() => {
        getClosedSumula();
    }, [isOpen]);


    return (
        <div className="mt-4 flex justify-center">
            <Dialog open={isOpen} onOpenChange={setIsOpen}>
                <DialogTrigger>
                    <div className="w-[300px] h-[50px] bg-primary text-white font-semibold rounded-lg flex items-center justify-center cursor-pointer" onClick={() => setIsOpen(true)}>
                        Súmulas fechadas
                    </div>
                </DialogTrigger>
                <DialogContent className="grid justify-center items-center">
                    <DialogHeader>
                        <DialogTitle className="text-primary font-semibold pb-4 text-2xl">SÚMULAS FECHADAS</DialogTitle>
                    </DialogHeader>
                    <DialogDescription className="text-lg font-medium">
                        Selecione a súmula que deseja deletar
                    </DialogDescription>
                    {closedSumula.length === 0 && (<p>Nenhuma súmula encontrada</p>)}
                    <div className="max-h-60 overflow-y-auto w-full">
                        {closedSumula.map((sumula: any) => (
                            <div key={sumula.id} className="bg-neutral-100 border-2 w-full h-14 md:w-[400px] md:h-[60px] rounded-md flex justify-between px-2 items-center z-0 mb-2">
                                <p className="text-primary font-semibold text-lg">{sumula.name?.toUpperCase()}</p>
                                <div className="flex items-center relative">
                                    <Button variant={"delete"} onClick={() => { setSelectedSumula(sumula); setIsConfirmOpen(true); }}>
                                        <Trash2 />
                                    </Button>
                                </div>
                            </div>
                        ))}
                    </div>
                    <DialogFooter className="gap-2">
                        <Button variant="outline" className="bg-slate-200" onClick={() => setIsOpen(false)}>Cancelar</Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>
            <Dialog open={isConfirmOpen} onOpenChange={setIsConfirmOpen}>
                <DialogContent className="grid justify-center items-center">
                    <DialogHeader>
                        <DialogTitle className="text-primary font-semibold pb-4 text-2xl">CONFIRMAR DELEÇÃO</DialogTitle>
                    </DialogHeader>
                    <DialogDescription>
                        Você tem certeza que deseja deletar "{selectedSumula?.name?.toUpperCase()}"?
                    </DialogDescription>
                    <DialogFooter className="gap-2">
                        <Button variant="outline" onClick={() => setIsConfirmOpen(false)}>Cancelar</Button>
                        <Button variant={"delete"} onClick={() => { handleDelete(selectedSumula.id); setIsConfirmOpen(false) }}>Confirmar</Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>
        </div>
    );
}
