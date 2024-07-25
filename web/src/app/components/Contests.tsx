import React from "react";
import ListObjectComponent from "./ListObjectComponent";

const Contests = () => {
    return (
        <div className="grid justify-center text-center items-center pb-24 pt-24">
            <ListObjectComponent title="eventos ativos" live={true}/>
            <ListObjectComponent title="eventos passados" live={false}/>
        </div>
    );
};

export default Contests;