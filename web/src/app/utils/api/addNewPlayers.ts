import request from "../request";
import { settingsWithAuth } from "../settingsWithAuth";
import toast from "react-hot-toast";
import { isAxiosError } from "axios";

export default async function addNewPlayers(fullName: string, socialName: string, registrationEmail: string, event_id: string, isImortal: boolean, access_token?: string){
    if(fullName.length === 0 || registrationEmail.length === 0){
        fullName.length === 0 ? 
        toast.error("Nome completo é obrigatório.") : 
        toast.error("Email de inscrição é obrigatório.");
        return;
    }
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(registrationEmail)) {
        toast.error("Email de inscrição inválido.");
        return;
    }
    const body = {
        "full_name": fullName,
        "social_name": socialName,
        "registration_email": registrationEmail,
        "is_imortal": isImortal
    }
    try {
        const response = await request.post(`/api/player/add/?event_id=${event_id}`,body,settingsWithAuth(access_token));
        if(response.status === 201){
            toast.success("Jogador adicionado com sucesso!");
        }
    } catch (error: unknown){
        if(isAxiosError(error)){
            const { data } = error.response || {};
            console.log(data);
            const errorMessage = data.errors || "Erro desconhecido.";
            toast.error(errorMessage);
        }
    }
}