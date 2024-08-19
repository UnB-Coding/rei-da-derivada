import request from "../request";
import { settingsWithAuth } from "../settingsWithAuth"; 

export default async function getAllPlayers(eventId: string, access_token?: string){
    const response = await request.get(`/api/players/?event_id=${eventId}`, settingsWithAuth(access_token));
    if(response.status === 200){
        return response.data;
    } else {
        return [];
    }
}