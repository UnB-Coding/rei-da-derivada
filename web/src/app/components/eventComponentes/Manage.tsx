import React, { useEffect, useState, useContext } from "react";
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
import request from "@/app/utils/request";
import { settingsWithAuth } from "@/app/utils/settingsWithAuth";
import { CheckCircle, ArrowDownToLine } from "lucide-react";
import { Checkbox } from "@nextui-org/checkbox";

interface ManageProps {
    isAdmin: boolean;
}

export default function Manage(props: ManageProps) {
    const [ isClassifiedOpen, setIsClassifiedOpen ] = useState<boolean>(false);
    const [ isStartOpen, setIsStartOpen ] = useState<boolean>(false);
    const [ confirmStart, setConfirmStart ] = useState<boolean>(false);

    return (
        <div className="mt-4 grid justify-center gap-4">
            <Dialog open={isClassifiedOpen} onOpenChange={setIsClassifiedOpen}>
                <DialogTrigger>
                    <div className="w-[300px] h-[50px] bg-primary text-white font-semibold rounded-lg flex items-center justify-center cursor-pointer">
                        Jogadores classificados
                    </div>
                </DialogTrigger>
                <DialogContent className="rounded-lg">
                    <DialogHeader>
                        <DialogTitle className="text-primary">JOGADORES CLASSIFICADOS</DialogTitle>
                    </DialogHeader>
                    <DialogDescription>
                        Clique no botão abaixo para baixar a lista de jogadores classificados.
                    </DialogDescription>
                    <DialogFooter>
                        <Button onClick={() => setIsClassifiedOpen(!isClassifiedOpen)} className="text-base font-semibold">
                            <ArrowDownToLine size={24} className="mr-2" />
                            Baixar
                        </Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>

            {props.isAdmin && (<Dialog open={isStartOpen} onOpenChange={setIsStartOpen}>
                <DialogTrigger>
                    <div className="w-[300px] h-[50px] bg-primary text-white font-semibold rounded-lg flex items-center justify-center cursor-pointer">
                        Começar evento
                    </div>
                </DialogTrigger>
                <DialogContent className="rounded-lg">
                    <DialogHeader>
                        <DialogTitle className="text-primary">GERAR SÚMULAS INICIAIS</DialogTitle>
                    </DialogHeader>
                    <DialogDescription className="text-lg">
                        Essa funcionalidade cria todas as súmulas iniciais para o evento. Utilize-a apenas para iniciar o evento.
                    </DialogDescription>
                    <Checkbox className="mt-2" size="lg" radius="sm" isSelected={confirmStart} onValueChange={setConfirmStart}>
                        Tenho certeza que desejo gerar as súmulas iniciais.
                    </Checkbox>
                    <DialogFooter>
                        <Button variant={"green"} className="text-base font-semibold" disabled={!confirmStart}>
                            <CheckCircle size={24} className="mr-2" />
                            Criar
                        </Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>)}
        </div>
    );
}