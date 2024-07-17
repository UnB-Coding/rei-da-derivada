import request from "../request";
import { settingsWithAuth } from "../settingsWithAuth";

export default async function getEvents(access_token?: string){
    const response = await request.get("/api/event/",(settingsWithAuth(access_token)));
    if(response.status === 200){
        const data = response.data;
        return data;
    } else {
        return [];
    }
}