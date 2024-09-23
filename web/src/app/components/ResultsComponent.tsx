import React, { useContext, useEffect, useState } from "react";
import DisplayComponent from "./DisplayPlayerComponent";
import NoResults from "./NoResults";
import { UserContext } from "../contexts/UserContext";
import getResults from "../utils/api/getResults";
import { usePathname } from "next/navigation";
import getPlayerResult from "../utils/api/getPlayerResults";

export default function ResultsComponent() {
    const { user } = useContext(UserContext);
    const [isPlayer, setIsPlayer] = useState<boolean>(false);
    const [result, setResult] = useState<any>(null);
    const [playerResult, setPlayerResult] = useState<any>(null);
    const eventId = usePathname().split("/")[1];
    const params = usePathname().split("/");
    const eventIdNumber = parseInt(params[1]);

    // Verifique se user e user.all_events estão definidos
    if (!user || !user.all_events) {
        return <NoResults />;
    }
    const current = user.all_events.find(elem => elem.event?.id === eventIdNumber);

    useEffect(() => {
        async function fetchResults() {
            const results = await getResults(eventId, user.access);
            setResult(results);

            // Verificar se o usuário é um jogador e obter os resultados do jogador
            if (current && current?.role == "player") {
                setIsPlayer(true);
                const playerResults = await getPlayerResult(eventId, user.access);
                setPlayerResult(playerResults);
            }
        }
        fetchResults();
    }, [eventId, user.access, current]);

    if (!result) {
        return <NoResults />;
    }

    return (
        <div className="grid justify-center items-center gap-5 py-32">
            {isPlayer && playerResult && (
                <div>
                    <p className="font-semibold text-slate-700">SEU DESEMPENHO</p>
                    <DisplayComponent playerName={playerResult.full_name} points={playerResult.total_score} />
                </div>
            )}
            {result["top4"] !== null && (
                <div className="grid gap-3">
                    <p className="font-semibold text-slate-700">TOP 4</p>
                    {result.top4 && result.top4.map((player: any) => (
                        <DisplayComponent key={player.id} playerName={player.full_name} points={player.total_score} />
                    ))}
                </div>
            )}
            {result['imortals'] !== null && (<div className="grid gap-3">
                <p className="font-semibold text-slate-700">IMORTAIS</p>
                {result.imortals && result.imortals.map((player: any) => (
                    <DisplayComponent key={player.id} playerName={player.full_name} points={player.total_score} />
                ))}
            </div>)}
            {result['ambassor'] !== null && (<div className="grid gap-3">
                <p className="font-semibold text-slate-700">EMBAIXADOR</p>
                {result.ambassor && (
                    <DisplayComponent playerName={result.ambassor.full_name} points={result.ambassor.total_score} />
                )}
            </div>)}
            {result["paladin"] !== null && (<div className="grid gap-3">
                <p className="font-semibold text-slate-700">PALADINO</p>
                {result.paladin && (
                    <DisplayComponent playerName={result.paladin.full_name} points={result.paladin.total_score} />
                )}
            </div>)}
        </div>
    );
}
