import toast from "react-hot-toast";
import request from "../request";
import { settingsWithAuth } from "../settingsWithAuth";
import axios, { isAxiosError } from "axios";

export default async function staffLogin(args: any) {
    const { access, token } = args;
    const body = {
        "join_token": token
    };
    try {
        const response = await request.post("/api/staff/",body, settingsWithAuth(access));
        if(response.status === 200){
            const data = response.data;
            toast.success("Autenticado com sucesso!")
        }
    } catch (error: unknown) {
        if(isAxiosError(error)) {
            const { data } = error.response || {};
            const errorMessage = data.errors || "Erro desconhecido."
            toast.error(`${errorMessage}`)
        }
    }
}