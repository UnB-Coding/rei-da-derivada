import request from "../request";
import { settingsWithAuth } from "../settingsWithAuth";
import { isAxiosError } from "axios";

export default async function getAllSumulas(event_id: string, access_token?: string) {
    const response = await request.get(`/api/sumula/ativas/?event_id=${event_id}`, settingsWithAuth(access_token));
    if(response.status === 200){
        return response.data;
    } else {
        return [];
    }
}