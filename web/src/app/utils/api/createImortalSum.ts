import toast from "react-hot-toast";
import request from "../request";
import { settingsWithAuth } from "../settingsWithAuth";
import { isAxiosError } from "axios";

export default async function createImortalSum(sumulaName: string, eventId: string, players: any[], staff: any[], access_token?: string) {
    if(players.length < 4){
        toast.error("A súmula deve conter no mínimo 4 jogadores.");
        return;
    }
    const body = {
        "name": sumulaName,
        "players": players,
        "referees": staff
    }
    try {
        const response = await request.post(`/api/sumula/imortal/?event_id=${eventId}`, body, settingsWithAuth(access_token));
        if(response.status === 201){
            toast.success("Súmula criada com sucesso.");
        }
    } catch (error: unknown) {
        if(isAxiosError(error)){
            const { data } = error.response || {};
            const errorMessage = data.errors || "Erro desconhecido.";
            toast.error(errorMessage);
        }
    }
}