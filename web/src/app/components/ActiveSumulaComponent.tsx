import React, { useState, useEffect, useContext } from "react";
import { UserContext } from "@/app/contexts/UserContext";
import JoinBoxComponent from "./JoinBoxComponent";
import { usePathname } from "next/navigation";
import request from "@/app/utils/request";
import { settingsWithAuth } from "../utils/settingsWithAuth";
import Loading from "./LoadingComponent";
import { useRouter } from "next/navigation";
import toast from "react-hot-toast";

const ActiveSumulaComponent = () => {
    const [sumulas, setSumulas] = useState<any[]>([]);
    const [canSee, setCanSee] = useState<boolean>(false);
    const { user } = useContext(UserContext);
    const eventId = usePathname().split("/")[1];
    const router = useRouter();

    const fetchSumulas = async () => {
        let allSumulas: any[];
        const response = await request.get(`/api/sumula/ativas/?event_id=${eventId}`, settingsWithAuth(user.access));
    
        if (response.status === 200) {
            const classificatoria = response.data.sumulas_classificatoria.map((sumula: any) => ({
                ...sumula,
                is_imortal: false
            }));
            const imortal = response.data.sumulas_imortal.map((sumula: any) => ({
                ...sumula,
                is_imortal: true
            }));
            allSumulas = classificatoria.concat(imortal);
            setSumulas(allSumulas);
        }
        setCanSee(true);
    }

    useEffect(() => {
        fetchSumulas();
    }, []);

    async function handleClick(id: number) {
        const current = sumulas[id];
        window.localStorage.removeItem("current_sumula");
        try {
            const body = {
                sumula_id: current.id,
                is_imortal: current.is_imortal
            };
            const response = await request.put(
                `/api/sumula/add-referee/?event_id=${eventId}`,
                body,
                settingsWithAuth(user.access)
            );
    
            if (response.status === 200) {
                window.localStorage.setItem("current_sumula", JSON.stringify(current));
                router.push(`/${eventId}/sumula/${current.id}`);
            }
        } catch (error: unknown) {
            console.error("Erro ao fazer a requisição:", error);
            toast.error("Permissão negada");
        }
    }

    if (!canSee) {
        return <Loading />
    }

    return (
        <div className="grid justify-center items-center py-32">
            <p className="text-primary font-semibold pb-4">SÚMULAS ATIVAS</p>
            <div className="grid gap-4">
                {sumulas.map((sumula, index) => {
                    return <JoinBoxComponent key={index} name={sumula.name} active={true} isEvent={false} onClick={() => handleClick(index)} />
                })}
            </div>
        </div>
    );
};

export default ActiveSumulaComponent;