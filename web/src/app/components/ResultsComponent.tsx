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

interface ResultsComponentProps {
    isPlayer: boolean,
}

export default function ResultsComponent({isPlayer} : ResultsComponentProps) {
    const { user } = useContext(UserContext);
    const [published, setPublished] = useState<boolean>(false);
    const [results, setResults] = useState<any>();
    const [playerResults, setPlayerResults] = useState<any>();
    const currentId = usePathname().split('/')[1];

    const fetchResults = async () => {
        try {
            const response = await request.get(`/api/results/?event_id=${currentId}`, settingsWithAuth(user.access));
            if(response.status === 200) {
                setResults(response.data);
            }
            if(isPlayer){
                const playerResponse = await request.get(`/api/results/player/?event_id=${currentId}`, settingsWithAuth(user.access));
                if(playerResponse.status === 200) {
                    setPlayerResults(response.data);
                }
            }
            setPublished(true);
        } catch (error: unknown) {
            if(isAxiosError(error)){
                const errorMessage = error.response?.data.errors || "Erro desconhecido";
                console.log(errorMessage);               
            }
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

    return published ? <NoResults /> :
        <>
            <div className="grid justify-center items-center gap-5 py-32">
                {isPlayer &&
                    <div>
                        <p className="font-semibold text-slate-700">SEU DESEMPENHO</p>
                        <DisplayComponent playerName={capitalize(playerMock.full_name)} points={playerMock.total_score} />
                    </div>}
                <div className="grid gap-3">
                    <p className="font-semibold text-slate-700">TOP 4</p>
                    {mock.top4 ? mock.top4.map((player, index) => {
                        return <DisplayComponent key={index} playerName={capitalize(player.full_name)} points={player.total_score} />
                    }) : <p> Ainda não divulgado</p>}
                </div>
                <div className="grid gap-3">
                    <p className="font-semibold text-slate-700">IMORTAIS</p>
                    {mock.imortals ? mock.imortals.map((player, index) => {
                        return <DisplayComponent key={index} playerName={capitalize(player.full_name)} points={player.full_name.length} />
                    }) : <p>Ainda não divulgado</p>}
                </div>
                <div className="grid gap-3">
                    <p className="font-semibold text-slate-700">PALADINO</p>
                    {mock.paladin ? <DisplayComponent playerName={capitalize(mock.paladin.full_name)} points={mock.paladin.total_score} /> :
                        <p>Ainda não divulgado</p>}
                </div>
                <div className="grid gap-3">
                    <p className="font-semibold text-slate-700">EMBAIXADOR</p>
                    {mock.ambassor ? <DisplayComponent playerName={capitalize(mock.ambassor.full_name)} points={mock.ambassor.total_score} /> :
                        <p>Ainda não divulgado</p>}
                </div>
            </div>
        </>
};