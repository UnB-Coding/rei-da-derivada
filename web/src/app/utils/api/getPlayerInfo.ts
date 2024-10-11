import request from "../request";
import { settingsWithAuth } from "../settingsWithAuth";
import { isAxiosError } from "axios";

export default async function getPlayerInfo(eventId: string, access_token?: string) {
    try {
        const response = await request.get(`/api/sumula/player/?event_id=${eventId}`, settingsWithAuth(access_token));
        return response.data;
    } catch (error: unknown) {
        if(isAxiosError(error)){
            const { data } = error.response || {};
            const errorMessage = data.errors || "Erro desconhecido.";
            console.log(errorMessage);
        }
    }
}