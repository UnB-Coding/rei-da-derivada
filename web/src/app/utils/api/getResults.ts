import { settingsWithAuth } from "../settingsWithAuth";
import request from "../request";

export default async function getFinalResults(eventId: string, access_token?: string) {
    try {
        const response = await request.get(`/api/results/?event_id=${eventId}`, settingsWithAuth(access_token));
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
