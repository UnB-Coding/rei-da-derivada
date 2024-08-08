import request from "../request";
import { settingsWithAuth } from "../settingsWithAuth";
import toast from "react-hot-toast";
import { isAxiosError } from 'axios';

export default async function setAsManager(email: string, eventId: string, access_token?: string){
    const body = {
        "email": email
    }
    try {
        const response = await request.post(`/api/staff-manager/?event_id=${eventId}`, body, settingsWithAuth(access_token));
        if (response.status === 200) {
            toast.success("Gerente adicionado com sucesso.");
        }
    } catch (error: unknown) {
        if (isAxiosError(error)) {
            const { data } = error.response || {};
            const errorMessage = data.errors || "Erro desconhecido.";
            toast.error(`${errorMessage}`);
        } else {
            toast.error("Erro desconhecido.");
        }
        
    }
}
