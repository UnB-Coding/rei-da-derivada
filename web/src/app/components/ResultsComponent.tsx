import React, { use, useContext, useEffect } from "react";
import { useState } from "react";
import DisplayComponent from "./DisplayPlayerComponent";
import NoResults from "./NoResults";
import { UserContext } from "../contexts/UserContext";
import request from "@/app/utils/request";
import { settingsWithAuth } from "@/app/utils/settingsWithAuth";
import { usePathname } from "next/navigation";
import capitalize from "@/app/utils/capitalize";
import { isAxiosError } from "axios";
import Loading from "./LoadingComponent";

interface ResultsComponentProps {
    isPlayer: boolean,
}

export default function ResultsComponent({ isPlayer }: ResultsComponentProps) {
    const { user } = useContext(UserContext);
    const [published, setPublished] = useState<boolean>(false);
    const [canSee, setCanSee] = useState<boolean>(false);
    const [results, setResults] = useState<any>();
    const [playerResults, setPlayerResults] = useState<any>();
    const currentId = usePathname().split('/')[1];

    const fetchResults = async () => {
        try {
            const response = await request.get(`/api/results/?event_id=${currentId}`, settingsWithAuth(user.access));
            if (response.status === 200) {
                setResults(response.data);
            }
            if (isPlayer) {
                const playerResponse = await request.get(`/api/results/player/?event_id=${currentId}`, settingsWithAuth(user.access));
                if (playerResponse.status === 200) {
                    setPlayerResults(response.data);
                }
            }
            setPublished(true);
            setCanSee(true);
        } catch (error: unknown) {
            if (isAxiosError(error)) {
                const errorMessage = error.response?.data.errors || "Erro desconhecido";
                console.log(errorMessage, "bigodee");
            }
            setCanSee(true)
            console.log(published)
        }
    }

    useEffect(() => {
        fetchResults();
    }, [user])

    const playerMock = {
        "id": 0,
        "total_score": 32767,
        "full_name": "string",
        "social_name": "string"
    }

    const mock = {
        "id": 5,
        "top4": [
            {
                "id": 5,
                "total_score": 98,
                "full_name": "JOÃO DA SILVA",
                "social_name": "João"
            },
            {
                "id": 6,
                "total_score": 98,
                "full_name": "JOÃO DA SILVA",
                "social_name": "João"
            },
            {
                "id": 5,
                "total_score": 98,
                "full_name": "JOÃO DA SILVA",
                "social_name": "João"
            },
            {
                "id": 5,
                "total_score": 98,
                "full_name": "JOÃO DA SILVA",
                "social_name": "João"
            },
        ],
        "paladin": {
            "id": 0,
            "total_score": 98,
            "full_name": "JOÃO DA SILVA",
            "social_name": "João"
        },
        "ambassor": {
            "id": 0,
            "total_score": 98,
            "full_name": "JOÃO DA SILVA",
            "social_name": "João"
        },
        "imortals": [
            {
                "id": 5,
                "total_score": 98,
                "full_name": "ALEXANDRE TOSTES SALIN E SOUZA",
                "social_name": "João"
            },
            {
                "id": 5,
                "total_score": 98,
                "full_name": "JOÃO DA SILVA",
                "social_name": "João"
            },
            {
                "id": 5,
                "total_score": 98,
                "full_name": "JOÃO DA SILVA",
                "social_name": "João"
            },
        ]
    }

    if(!canSee) {
        return <Loading />
    }

    return !published ? <NoResults /> :
        <>
            <div className="grid justify-center items-center gap-5 py-32">
                {isPlayer &&
                    <div>
                        <p className="font-semibold text-slate-700 md:text-2xl">SEU DESEMPENHO</p>
                        <DisplayComponent playerName={capitalize(playerResults.full_name)} points={playerResults.total_score} />
                    </div>}
                <div className="grid gap-3">
                    <p className="font-semibold text-slate-700 md:text-2xl">TOP 4</p>
                    {results.top4 ? results.top4.map((player: any, index: number) => {
                        return <DisplayComponent key={index} playerName={capitalize(player.full_name)} points={player.total_score} />
                    }) : <p className="text-lg md:text-xl">Ainda não divulgado</p>}
                </div>
                <div className="grid gap-3">
                    <p className="font-semibold text-slate-700 md:text-2xl">IMORTAIS</p>
                    {results.imortals ? results.imortals.map((player: any, index: number) => {
                        return <DisplayComponent key={index} playerName={capitalize(player.full_name)} points={player.total_score} />
                    }) : <p className="text-lg md:text-xl">Ainda não divulgado</p>}
                </div>
                <div className="grid gap-3">
                    <p className="font-semibold text-slate-700 md:text-2xl">PALADINO</p>
                    {results.paladin && results.paladin.full_name ? <DisplayComponent playerName={capitalize(results.paladin.full_name)} points={results.paladin.total_score} /> :
                        <p className="text-lg md:text-xl">Ainda não divulgado</p>}
                </div>
                <div className="grid gap-3">
                    <p className="font-semibold text-slate-700 md:text-2xl">EMBAIXADOR</p>
                    {results.ambassor && results.ambassor.full_name ? <DisplayComponent playerName={capitalize(results.ambassor.full_name)} points={results.ambassor.total_score} /> :
                        <p className="text-lg md:text-xl">Ainda não divulgado</p>}
                </div>
            </div>
        </>
};
