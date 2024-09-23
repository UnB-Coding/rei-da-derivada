import { settingsWithAuth } from "../settingsWithAuth";
import request from "../request";

export default async function getPlayerResult(eventId: string, access_token?: string) {
    try {
        const response = await request.get(`/api/results/player/?event_id=${eventId}`, settingsWithAuth(access_token));
        if (response.status === 200) {
            return response.data;
        } else {
            return null;
        }
    }
    catch (error) {
        console.error(error);
        return null;
    }
}
