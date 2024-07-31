import React, { useContext, useState } from "react";
import { isAxiosError } from "axios";
import { UserContext } from "../../contexts/UserContext";
import { usePathname } from "next/navigation";
import request from "@/app/utils/request";
import { settingsWithAuth } from "@/app/utils/settingsWithAuth";
import toast from "react-hot-toast";
import { formDataSettings } from "@/app/utils/formDataSettings";

export default function SubmitFileComponent() {
    const [playerFile, setPlayerFile] = useState<File | null>(null);
    const [staffFile, setStaffFile] = useState<File | null>(null);
    const currentId = usePathname().split("/")[1];
    const { user } = useContext(UserContext);

    const handlePlayerFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        if (event.target.files) {
            setPlayerFile(event.target.files[0]);
        }
    }
    const handleStaffFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        if (event.target.files) {
            setStaffFile(event.target.files[0]);
        }
    }

    const handlePlayerSubmit = async () => {
        if (playerFile) {
            const formData = new FormData();
            formData.append("file", playerFile);
            try {
                const response = await request.post(`/api/upload-player/?event_id=${currentId}`, formData, formDataSettings(user.access));
                if(response.status === 201){
                    toast.success(response.data);
                }
            } catch (error) {
                toast.error("Dados inválidos!");
            }
        } else {
            toast.error("Selecione um arquivo para enviar!");
        }
    }

    const handleStaffSubmit = async () => {
        if (staffFile) {
            const formData = new FormData();
            formData.append("file", staffFile);
            try {
                const response = await request.post(`/api/upload-staff/?event_id=${currentId}`, formData, formDataSettings(user.access));
                console.log(response.data);
                if(response.status === 201){
                    toast.success(response.data);
                }
            } catch (error) {
                toast.error("Dados inválidos!");
            }
        } else {
            toast.error("Selecione um arquivo para enviar!");
        }
    }
    return (
        <div className="grid justify-center items-center gap-5 pt-32">
            <div className="grid gap-4 bg-neutral-100 rounded-2xl px-4 py-6 shadow-sm">
                <p className="font-semibold text-primary pl-4">ADICIONAR JOGADORES</p>
                <input className="pl-4" type="file" onChange={handlePlayerFileChange}/>
                <button className="bg-primary font-medium text-white rounded-md mx-4 p-2" onClick={handlePlayerSubmit}>Enviar</button>
            </div>
            <div className="grid gap-4 bg-neutral-100 rounded-2xl px-4 py-6 shadow-sm">
                <p className="font-semibold text-primary pl-4">ADICIONAR STAFF</p>
                <input className="pl-4" type="file" onChange={handleStaffFileChange}/>
                <button className="bg-primary font-medium text-white rounded-md mx-4 py-2" onClick={handleStaffSubmit}>Enviar</button>
            </div>
        </div>
    );
}