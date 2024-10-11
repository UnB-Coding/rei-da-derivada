import request from "../request";
import { settingsWithAuth } from "../settingsWithAuth";
import toast from "react-hot-toast";
import { isAxiosError } from 'axios';

export default async function createEvent(args: any){
    const {access, token, name} = args;
    const body = {
        "name": name,
        "token_code": token
    };
    try {
        const response = await request.post("/api/event/",body, settingsWithAuth(access));
        if(response.status === 200) toast.error("O evento já existe.")
        else if(response.status === 201){
            toast.success("Evento criado com sucesso!");
        }
    } catch(error: unknown){
        if(isAxiosError(error)) {
            const { data } = error.response || {};
            const errorMessage = data.errors || "Erro desconhecido."
            toast.error(`${errorMessage}`);
        } else {
            toast.error("Erro desconhecido.")
        }
        
    }
}