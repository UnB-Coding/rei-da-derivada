import request from "../request";
import { settingsWithAuth } from "../settingsWithAuth";

export default async function getStaffList(eventId: string, access_token?: string) {
    const response = await request.get(`/api/staff/?event_id=${eventId}`, settingsWithAuth(access_token));
    if (response.status === 200) {
        return response.data;
    } else {
        return [];
    }
}