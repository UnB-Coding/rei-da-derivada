import request from "../request";
import { settingsWithAuth } from "../settingsWithAuth";
import toast from "react-hot-toast";

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
    } catch(error){
        console.log(error)
        toast.error("Token inválido.")
    }
}