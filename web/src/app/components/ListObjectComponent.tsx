import React from "react";
import JoinBoxComponent from "./JoinBoxComponent";

interface ListObjectComponentProps {
    title: string;
    active?: boolean;
}

const ListObjectComponent = (props: ListObjectComponentProps) => {
    return(
        <div className="grid justify-center items-center gap-4 pb-4 pt-10">
            <p className="text-xl font-semibold text-primary ">{props.title.toUpperCase()}</p>
            <JoinBoxComponent title="unb-rrdd-24" active={props.active}/>
            <JoinBoxComponent title="unb-rrdd-25" active={props.active}/>
            <JoinBoxComponent title="unb-rrdd-26" active={props.active}/>
            <JoinBoxComponent title="unb-rrdd-27" active={props.active}/>
        </div>
    );
}

export default ListObjectComponent;