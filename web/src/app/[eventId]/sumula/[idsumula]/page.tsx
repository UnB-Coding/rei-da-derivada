'use client'
import { useRouter } from "next/navigation";
import React, { useContext, useEffect, useState } from "react";
import { UserContext } from "@/app/contexts/UserContext";
import { usePathname } from "next/navigation";
import validatePath from "@/app/utils/validadePath";
import getBasePath from "@/app/utils/getBasePath";
import LoadingComponent from "@/app/components/LoadingComponent";
import { ChevronLeft, ChevronRight, Trash2, CheckCircle, ArrowRight } from "lucide-react";
import { Button } from "@/app/components/ui/button";
import { Checkbox } from "@nextui-org/checkbox";
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
import request from "@/app/utils/request";
import { settingsWithAuth } from "@/app/utils/settingsWithAuth";
import toast from "react-hot-toast";

// se você está lendo isso, eu sinto muito pelo código que você vai ver...
// dei uma documentada básica nas funções utilitárias pra tentar ajudar
// TODO: componentizar, tem muita repetição de código desnecessária aqui e dá pra melhorar a lógica
interface Points {
    pageNumber: number;
    player1Id: number;
    player2Id: number;
    points: number;
}

export default function SumulaId() {
    const { user, loading } = useContext(UserContext);
    const [ currentSumula, setCurrentSumula ] = useState<any>(null); // conteúdo da súmula atual
    const [ isDialogOpen, setIsDialogOpen ] = useState(false);
    const [ isLeaveOpen, setIsLeaveOpen ] = useState(false); // dialog de sair da súmula
    const [ canSee, setCanSee ] = useState<boolean>(false);
    const [ currentPage, setCurrentPage ] = useState(0); // paǵina atual das rodadas
    const [ rounds, setRounds ] = useState<any>([]); // aqui que estão os rounds, eles saem da currentSumula
    const [ playersScore, setPlayersScore ] = useState<any>([]);
    const [ sumulaPoints, setSumulaPoints ] = useState<Points[]>([]); // aqui faz parte da gambiarra pra guardar as pontuações
    const [ isFinishDialogOpen, setIsFinishDialogOpen ] = useState(false);
    const [ click3Disabled, setClick3Disabled ] = useState<boolean>(false);
    const [ click1Disabled, setClick1Disabled ] = useState<boolean>(false);
    const [ finishConfirm, setFinishConfirm ] = useState<boolean>(false); // checkbox de confirmar finalização da súmula
    const [ duplaPontuacoes, setDuplaPontuacoes ] = useState<{ [key: number]: number }>({});
    const [ imortalPlayers, setImortalPlayers ] = useState<any>([]); // aqui é pra enviar os imortais pro backend
    const [ sumulaPointsAux, setSumulaPointsAux ] = useState<any>([]);
    const router = useRouter();
    const params = usePathname().split("/");
    const currentId = parseInt(params[1]);
    const currentPath = params[2];

    async function validateSumula() {
        const sumula = window.localStorage.getItem("current_sumula");
        if (sumula) {
            const auxSumula = JSON.parse(sumula);
            if (auxSumula.id === parseInt(params[3])) {
                console.log(auxSumula.players_score)
                setPlayersScore(auxSumula.players_score);
                setRounds(auxSumula.rounds);
                setCurrentSumula(auxSumula);
                setCanSee(true);
                console.log(auxSumula);
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

    // aqui é só pq o nome vem do sigaa e fica em caixa alta (tenebroso)
    const capitalize = (fullName: any) => {
        return fullName
            .split(' ')
            .map((word: any) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
            .join(' ');
    };

    // aqui é pra apagar a pontuação da página atual e permitir o click nos botões de pontuação
    const clearPagePoints = (pageNumber: number) => {
        setSumulaPoints(sumulaPoints.filter((point) => point.pageNumber !== pageNumber));
        setDuplaPontuacoes({});
        setClick1Disabled(false);
        setClick3Disabled(false);
    }

    // aqui é crio um novo objeto com as pontuações da rodada atual e altero a pontuação da dupla no card
    const handleAddPoints = (pageIndex: number, points: number, pair: any, index: number) => {
        const player1Id = pair.player1.player.id;
        const player2Id = pair.player2.player.id;
        const newPoints = {
            pageNumber: pageIndex,
            player1Id: player1Id,
            player2Id: player2Id,
            points: points,
        };
        setSumulaPoints([...sumulaPoints, newPoints]);
        setDuplaPontuacoes((prev) => ({
            ...prev,
            [index]: (prev[index] || 0) + points,
        }));
        points === 1 ? setClick1Disabled(true) : setClick3Disabled(true);
    }

    // aqui é onde a rodada é finalizada e a próxima é aberta
    const finishRound = () => {
        setCurrentPage(currentPage + 1);
        setIsFinishDialogOpen(false);
        setClick1Disabled(false);
        setClick3Disabled(false);
        setDuplaPontuacoes({});
    }

    // aqui é onde o request de finalizar a súmula será enviado 
    const handleFinishSumula = async () => {
        const updatedPlayersScore = playersScore.map((currentPlayer: any) => {
            const playerPoints = sumulaPoints.filter((point: Points) => point.player1Id === currentPlayer.player.id || point.player2Id === currentPlayer.player.id);
            const points = playerPoints.reduce((acc, current) => acc + current.points, 0);
            return {
                ...currentPlayer,
                points: points,
            };
        });
        const ids = playersScore.map((currentPlayer: any) => {
            return {
                id: currentPlayer.player.id
            }
        });
        const removed = ids.filter((item: any) => !imortalPlayers.some((player: any) => player.id === item.id));
        const body = {
            "id": currentSumula.id,
            "name": currentSumula.name,
            "description": currentSumula.description,
            "referee": currentSumula.referee,
            "players_score": updatedPlayersScore,
            "imortal_players": removed,
        }
        try {
            const response = await request.put(`/api/sumula/${currentSumula.is_imortal ? "imortal" : "classificatoria"}/?event_id=${currentId}`, body, settingsWithAuth(user.access));
            if (response.status === 200) {
                toast.success("Súmula finalizada com sucesso");
                router.push(`/${currentId}/sumula`);
            }
        } catch (error) {
            console.log(error);
            toast.error("Erro ao finalizar a súmula");
        }
        setIsDialogOpen(false)
    }

    // aqui é onde mostra a pontuação final no dialog de finalizar a súmula
    const seeFinalScore = () => {
        const scores = playersScore.map((currentPlayer: any) => {
            const playerPoints = sumulaPoints.filter((point: Points) => point.player1Id === currentPlayer.player.id || point.player2Id === currentPlayer.player.id);
            const points = playerPoints.reduce((acc, current) => acc + current.points, 0);
            return {
                ...currentPlayer,
                points: points,
            };
        });
        setSumulaPointsAux(scores);
    };

    // aqui é pra quando clicar em voltar no topo da súmula
    const leaveSumula = () => {
        window.localStorage.removeItem("current_sumula");
        router.push(`/${currentId}/sumula`);
    };

    // aq é quando marca o checkbox no dialog de finalizar a súmula
    const handleIsImortalChange = (playerId: string, isChecked: boolean) => {
        setImortalPlayers((prev: any) => {
            if(isChecked){
                return [...prev, {id: playerId}];
            } else {
                return prev.filter((player: any) => player.id !== playerId);
            }
        })
    }

    const closeDialog = () => {
        setIsDialogOpen(false);
        setImortalPlayers([]);
        setFinishConfirm(false);
    }

    return (
        <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100 p-4">
            <Dialog open={isLeaveOpen} onOpenChange={setIsLeaveOpen}>
                <DialogTrigger asChild>
                    <Button variant="outline" onClick={() => console.log("sair da sumula")} className="mb-4 absolute top-4 left-4">
                        <ChevronLeft className="h-4 w-4 mr-2" />
                        Voltar
                    </Button>
                </DialogTrigger>
                <DialogContent className="sm:max-w-[425px] rounded-lg">
                    <DialogHeader>
                        <DialogTitle>Sair da súmula</DialogTitle>
                        <DialogDescription>
                            Tem certeza que deseja sair da súmula? Nenhuma alteração será salva.
                        </DialogDescription>
                    </DialogHeader>
                    <DialogFooter className="gap-4">
                        <Button variant="outline" onClick={() => setIsLeaveOpen(false)}>Cancelar</Button>
                        <Button onClick={leaveSumula}>Confirmar</Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>
            <h1 className="text-3xl font-bold mb-6">Rodada {currentPage + 1}</h1>
            <div className="w-full max-w-5xl grid gap-4 sm:grid-cols-2 lg:grid-cols-2">
                {rounds[currentPage].map((pair: any, index: number) => (
                    <Card key={index} className="w-full bg-white">
                        <CardHeader>
                            <CardTitle className="text-center text-lg">Dupla {index + 1}</CardTitle>
                        </CardHeader>
                        <CardContent className="flex flex-col items-center space-y-4">
                            <p className="text-md sm:text-lg font-semibold text-center">{capitalize(pair.player1.player.full_name)}</p>
                            <p className="text-md sm:text-lg font-semibold text-center">{capitalize(pair.player2.player.full_name)}</p>
                            <p className="text-md sm:text-lg">Pontuação: {duplaPontuacoes[index] || 0}</p>
                            <div className="flex space-x-4">
                                <Button disabled={duplaPontuacoes[index] !== undefined || click1Disabled} size="lg" className="text-xl font-semibold" onClick={() => handleAddPoints(currentPage, 1, pair, index)}>+1</Button>
                                <Button disabled={duplaPontuacoes[index] !== undefined || click3Disabled} size="lg" className="text-xl font-semibold" onClick={() => handleAddPoints(currentPage, 3, pair, index)}>+3</Button>
                            </div>
                        </CardContent>
                    </Card>
                ))}
            </div>
            <div className="flex justify-center items-center mt-6 space-x-4">
                {currentPage !== rounds.length - 1 && (
                    <Dialog open={isFinishDialogOpen} onOpenChange={setIsFinishDialogOpen}>
                        <DialogTrigger asChild>
                            <Button variant="default">
                                <ArrowRight className="h-4 w-4 mr-2" />
                                Finalizar Rodada
                            </Button>
                        </DialogTrigger>
                        <DialogContent className="sm:max-w-[425px] rounded-lg">
                            <DialogHeader>
                                <DialogTitle>Finalizar Rodada</DialogTitle>
                                <DialogDescription>
                                    Tem certeza que deseja avançar para a próxima rodada? Esta ação não pode ser desfeita.
                                </DialogDescription>
                            </DialogHeader>
                            <DialogFooter>
                                <Button variant="outline" onClick={() => setIsFinishDialogOpen(false)}>Cancelar</Button>
                                <Button onClick={finishRound}>Confirmar</Button>
                            </DialogFooter>
                        </DialogContent>
                    </Dialog>
                )}
            </div>
            <div className="flex gap-2 justify-center items-center mt-4 space-x-4">
                <Button className="bg-red-500 text-white" variant={"destructive"} onClick={() => clearPagePoints(currentPage)}>
                    <Trash2 className="h-6 w-6" />
                    Limpar pontuação
                </Button>
                {currentPage === rounds.length - 1 && (
                    <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
                        <DialogTrigger asChild>
                            <Button variant="default" onClick={seeFinalScore}>
                                <CheckCircle className="h-4 w-4 mr-2" />
                                Finalizar Súmula
                            </Button>
                        </DialogTrigger>
                        <DialogContent className="sm:max-w-[80%] lg:max-w-[800px] rounded-lg">
                            <DialogHeader>
                                <DialogTitle>Finalizar Súmula</DialogTitle>
                                <DialogDescription className="text-[1rem]">
                                    Confira as pontuações{!currentSumula.is_imortal && ", selecione os participantes que se classificaram"} e finalize a súmula. Esta ação não pode ser desfeita.
                                </DialogDescription>
                            </DialogHeader>
                            <div>
                                {sumulaPointsAux.sort((a: any, b: any) => b.points - a.points).map((player: any, index: number) => (
                                    <div key={index} className="flex items-center justify-between">
                                        {!currentSumula.is_imortal && (<Checkbox onChange={(e) => handleIsImortalChange(player.player.id, e.target.checked)}/>)}
                                        <p className={`${player.player.full_name.length > 30 ? "text-[1rem]" : "text-md"} md:text-lg`}>{capitalize(player.player.full_name)}</p>
                                        <p>{player.points} pts</p>
                                    </div>
                                ))}
                            </div>
                            <Checkbox className="mt-2" defaultSelected size="md" radius="sm" isSelected={finishConfirm} onValueChange={setFinishConfirm}>
                                Confirmo que as pontuações estão corretas
                            </Checkbox>
                            <DialogFooter className="gap-4">
                                <Button variant="outline" onClick={closeDialog}>Cancelar</Button>
                                <Button disabled={!finishConfirm} onClick={handleFinishSumula}>Confirmar</Button>
                            </DialogFooter>
                        </DialogContent>
                    </Dialog>
                )}
            </div>
        </div>
    );
};