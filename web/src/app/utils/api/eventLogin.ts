import request from "../request";
import { settingsWithAuth } from "../settingsWithAuth";
import { toast } from "react-hot-toast";


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
            console.log(event);
            toast.success("Evento adicionado com sucesso!");
        }   
    } catch (error) {
        console.error(error);
        toast.error("Dados inválidos.");
    }
}