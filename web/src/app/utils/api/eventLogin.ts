import request from "../request";
import { settingsWithAuth } from "../settingsWithAuth";
import { toast } from "react-hot-toast";
import axios, { isAxiosError } from 'axios';


export default async function eventLogin(args: any){
    const {access, email, token} = args;
    const body = {
        "email": email,
        "join_token": token
    }
    try {
        const response = await request.post("/api/players/", body, settingsWithAuth(access));
        if(response.status === 200){
            const { data } = response;
            const { event } = data;
            toast.success("Evento adicionado com sucesso!");
        }   
    } catch (error: unknown) {
        if(axios.isAxiosError(error)) {
            const { data } = error.response || {};
            const errorMessage = data.errors || "Erro desconhecido."
            toast.error(`${errorMessage}`)
        }
    }
}