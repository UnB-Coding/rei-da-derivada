import request from "../request";
import { settingsWithAuth } from "../settingsWithAuth";
import toast from "react-hot-toast";
import { isAxiosError } from "axios";

export default async function addNewStaff(fullName: string, registrationEmail: string, isManager: boolean, event_id: string, access_token?: string) {
    if (fullName.length === 0 || registrationEmail.length === 0) {
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
        "registration_email": registrationEmail,
        "is_manager": isManager
    }
    try {
        const response = await request.post(`/api/staff/add?event_id=${event_id}`, body, settingsWithAuth(access_token));
        if (response.status === 201) {
            toast.success("Staff adicionado com sucesso!");
        }
    } catch (error: unknown) {
        if(isAxiosError(error)){
            const { data } = error.response || {};
            const errorMessage = data.errors || "Erro desconhecido.";
            toast.error(errorMessage);
        }
    }
}