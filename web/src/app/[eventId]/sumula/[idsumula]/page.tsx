'use client'
import { useRouter } from "next/navigation";
import React, { useContext, useEffect, useState } from "react";
import { UserContext } from "@/app/contexts/UserContext";
import { usePathname } from "next/navigation";
import validatePath from "@/app/utils/validadePath";
import getBasePath from "@/app/utils/getBasePath";
import LoadingComponent from "@/app/components/LoadingComponent";
import { ChevronLeft, ChevronRight, Trash2, CheckCircle } from "lucide-react";
import { Button } from "@/app/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/app/components/ui/card";
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from "@/app/components/ui/dialog";


export default function SumulaId() {
    const { user, loading } = useContext(UserContext);
    const [currentSumula, setCurrentSumula] = useState<any>(null);
    const [ isDialogOpen, setIsDialogOpen ] = useState(false);
    const [canSee, setCanSee] = useState<boolean>(false);
    const [currentPage, setCurrentPage] = useState(0);
    const [rounds, setRounds] = useState<any>([]);
    const router = useRouter();
    const params = usePathname().split("/");
    const currentId = parseInt(params[1]);
    const currentPath = params[2];

    async function validateSumula() {
        const sumula = window.localStorage.getItem("current_sumula");
        if (sumula) {
            const auxSumula = JSON.parse(sumula);
            if (auxSumula.id === parseInt(params[3])) {
                setRounds(auxSumula.rounds);
                setCurrentSumula(auxSumula);
                setCanSee(true);
            } else {
                router.push(`/${currentId}/sumula`);
            }
        } else {
            router.push(`/${currentId}/sumula`);
        }
    }

    useEffect(() => {
        if (!user.access && !loading) {
            router.push("/");
        } else if (user.all_events) {
            const current = user.all_events.find(elem => elem.event?.id === currentId);
            if (current && current.role) {
                validatePath(current.role, currentPath) === true ?
                    validateSumula() : router.push(`/${currentId}/${getBasePath(current.role)}`);
            } else {
                router.push("/contests");
            }
        }
    }, [user]);

    if (!canSee || loading) {
        return <LoadingComponent />;
    }

    const capitalize = (fullName: any) => {
        return fullName
            .split(' ')
            .map((word: any) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
            .join(' ');
    };

    return (
        <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100 p-4">
            <h1 className="text-3xl font-bold mb-6">Rodada {currentPage + 1}</h1>
            <div className="w-full max-w-5xl grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                {rounds[currentPage].map((pair: any, index: number) => (
                    <Card key={index} className="w-full">
                        <CardHeader>
                            <CardTitle className="text-center text-lg">Dupla {index + 1}</CardTitle>
                        </CardHeader>
                        <CardContent className="flex flex-col items-center space-y-4">
                            <p className="text-md sm:text-lg font-semibold text-center">{}{capitalize(pair.player1.player.full_name)}</p>
                            <p className="text-md sm:text-lg font-semibold text-center">{capitalize(pair.player2.player.full_name)}</p>
                            <div className="flex space-x-4">
                                <Button size="lg"  className="text-xl font-semibold" onClick={() => console.log(pair)}> +1</Button>
                                <Button size="lg" className="text-xl font-semibold" onClick={() => console.log(1)}> +3</Button>
                            </div>
                        </CardContent>
                    </Card>
                ))}
            </div>
            <div className="flex justify-center items-center mt-6 space-x-4">
                <Button variant="outline" size="sm" onClick={() => currentPage > 0 ? setCurrentPage(currentPage - 1) : null}>
                    <ChevronLeft className="h-6 w-6" />
                    Anterior
                </Button>
                <span className="text-sm">
                    Página {currentPage + 1} de {rounds.length}
                </span>
                <Button variant="outline" size="sm" onClick={() => currentPage < rounds.length - 1 ? setCurrentPage(currentPage + 1) : null}>
                    Próximo
                    <ChevronRight className="h-6 w-6" />
                </Button>
            </div>

            <div className="flex gap-2 justify-center items-center mt-4 space-x-4">
                <Button className="bg-red-500 text-white" variant={"destructive"}>
                    <Trash2 className="h-6 w-6" />
                    Limpar pontuação
                </Button>
                {currentPage === rounds.length - 1 && (
                    <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
                    <DialogTrigger asChild>
                      <Button variant="default">
                        <CheckCircle className="h-4 w-4 mr-2" />
                        Finalizar Súmula
                      </Button>
                    </DialogTrigger>
                    <DialogContent className="sm:max-w-[425px] rounded-lg">
                      <DialogHeader>
                        <DialogTitle>Finalizar Súmula</DialogTitle>
                        <DialogDescription>
                          Tem certeza que deseja encerrar a súmula? Esta ação não pode ser desfeita.
                        </DialogDescription>
                      </DialogHeader>
                      <DialogFooter className="gap-4">
                        <Button variant="outline" onClick={() => setIsDialogOpen(false)}>Cancelar</Button>
                        <Button onClick={() => console.log("Aqui vai a rota de encerrar a súmula")}>Confirmar</Button>
                      </DialogFooter>
                    </DialogContent>
                  </Dialog>
                )}
            </div>
        </div>
    );
};