import React from "react";
import ListObjectComponent from "./ListObjectComponent";
import { Button } from "@/app/components/ui/button";
import { RotateCw } from "lucide-react"

const Contests = () => {
    return (
        <div className="grid justify-center text-center items-center pb-24 pt-36">
            <Button onClick={() => {window.location.reload()}} className="text-lg font-medium gap-2" size={"lg"}>
                <RotateCw/>
                Atualizar lista
            </Button>
            <ListObjectComponent title="eventos ativos" live={true}/>
            <ListObjectComponent title="eventos passados" live={false}/>
        </div>
    );
};

export default Contests;