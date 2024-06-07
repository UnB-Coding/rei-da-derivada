import React from "react";
import ListObjectComponent from "./ListObjectComponent";

const Contests = () => {
    return (
        <div className="grid justify-center items-center pb-24 pt-20">
            <ListObjectComponent title="eventos ativos" active={true}/>
            <ListObjectComponent title="eventos passados"/>
        </div>
    );
};

export default Contests;