import toast from "react-hot-toast";
import request from "../request";
import { settingsWithAuth } from "../settingsWithAuth";

export default async function staffLogin(args: any) {
    const { access, token } = args;
    const body = {
        "join_token": token
    };
    try {
        const response = await request.post("/api/staff/",body, settingsWithAuth(access));
        if(response.status === 200){
            const data = response.data;
            console.log(data);
            toast.success("Autenticado com sucesso!")
        }
    } catch (error) {
        console.log(error)
        toast.error("Token inválido.")
    }
}