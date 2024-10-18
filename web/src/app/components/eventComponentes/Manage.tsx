import React, { useEffect, useState, useContext, use } from "react";
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
import { usePathname } from "next/navigation";
import toast from "react-hot-toast";
import { isAxiosError } from "axios";

interface ManageProps {
    isAdmin: boolean;
}

export default function Manage(props: ManageProps) {
    const { user } = useContext(UserContext);
    const [isClassifiedOpen, setIsClassifiedOpen] = useState<boolean>(false);
    const [isStartOpen, setIsStartOpen] = useState<boolean>(false);
    const [confirmStart, setConfirmStart] = useState<boolean>(false);
    const eventId = usePathname().split("/")[1];

    const handleStartEvent = async () => {
        try {
            await toast.promise(
                request.post(`/api/sumula/generate/?event_id=${eventId}`, {}, settingsWithAuth(user.access)),
                {
                    loading: "Criando súmulas...",
                    success: "Súmulas criadas com sucesso.",
                    error: ({ response }) => {
                        let errorMessage = "Erro ao criar súmulas.";
                        if (response?.data?.errors) {
                            errorMessage = response.data.errors;
                        }
                        return errorMessage;
                    }
                }
            );
        } catch (error: unknown) {
            if (isAxiosError(error)) {
                const errorMessage = error.response?.data.errors || "Erro desconhecido";
            }
            console.error("Erro ao fazer a requisição:", error);
        }
        setIsStartOpen(false);
    }

    const handleDownload = async () => {
        try {
            const response = await request.get(`/api/players/export/?event_id=${eventId}`, {
                ...settingsWithAuth(user.access),
                responseType: "blob"
            });
            const blob = new Blob([response.data], { type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" });
            const downloadUrl = URL.createObjectURL(blob);

            const a = document.createElement("a");
            a.href = downloadUrl;
            a.download = "jogadores_classificados.xlsx";
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(downloadUrl);

            toast.success("Arquivo baixado com sucesso!");
        } catch (error: unknown) {
            if (isAxiosError(error)) {
                const errorMessage = error.response?.data.errors || "Erro desconhecido";
                toast.error(errorMessage);
            }
            console.error("Erro ao fazer a requisição:", error);

        }
        setIsClassifiedOpen(false);
    }

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
                        <Button onClick={() => handleDownload()} className="text-base font-semibold">
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
                <DialogContent className="rounded-lg" onCloseAutoFocus={() => setConfirmStart(false)}>
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
                        <Button variant={"green"} className="text-base font-semibold" disabled={!confirmStart} onClick={() => handleStartEvent()}>
                            <CheckCircle size={24} className="mr-2" />
                            Criar
                        </Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>)}
        </div>
    );
}
