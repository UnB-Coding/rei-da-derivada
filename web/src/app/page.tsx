'use client'
import { useRouter } from "next/navigation";
import { useContext, useEffect } from "react";
import { UserContext } from "@/app/contexts/UserContext";

const list: string[] = ["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email"];
const scopes = list.join(" ");

export default function Home() {
  const params = new URLSearchParams({
    client_id: "28351905545-kehhusl90e4avsgrcurrgedh6t2p1756.apps.googleusercontent.com",
    include_granted_scopes: "false",
    redirect_uri: "http://localhost:3000",
    state: "state_parameter_passthrough_value_sosalve",
    response_type: "token",
    scope: scopes,
  });
  const {setUser} = useContext(UserContext);
  const url = `https://accounts.google.com/o/oauth2/v2/auth?${params.toString()}`;
  const router = useRouter();
  useEffect(() => {
    let token = new URLSearchParams(window.location.hash).get("access_token");
    console.log(token);
    if (token){
      const myHeaders = new Headers();
      myHeaders.append("Content-Type", "application/json");
      myHeaders.append("Accept", "application/json");

      fetch("http://localhost:8000/users/register/google/", {
        method: "POST",
        headers: myHeaders,
        credentials: "include",
        body: JSON.stringify({
          access_token: token,
        }),
      }).then((res) => {
        return res.json();
      }).then((data) => {
        setUser(data);
        router.push("/home");
      }).catch((err) => {
        console.error(err);
      });
    }
    
  }, []);


  return (
    <button onClick={()=>{
      router.replace(url);
    }}>
      LOGIN COM GOOGLE
    </button>
  );
}
