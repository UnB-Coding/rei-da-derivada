'use client'
import { useRouter } from "next/navigation";
import { useContext, useEffect } from "react";
import { UserContext } from "@/app/contexts/UserContext";
import { Button } from "@/app/components/ui/button";
import Logo from "@/app/assets/logo.png";
import Image from "next/image";

const list: string[] = ["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email"];
const scopes = list.join(" ");
const rrddUrl = 'https://www.reidaderivada.com/';

export default function Home() {
  const redirectUri = process.env.NEXT_PUBLIC_LOCAL_URL || "http://localhost:3000";
  const clientId = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID || "";
  const params = new URLSearchParams({
    client_id: clientId,
    include_granted_scopes: "false",
    redirect_uri: redirectUri,
    state: "state_parameter_passthrough_value_sosalve",
    response_type: "token",
    scope: scopes,
  });
  const { setUser } = useContext(UserContext);
  const url = `https://accounts.google.com/o/oauth2/v2/auth?${params.toString()}`;
  const router = useRouter();
  useEffect(() => {
    let token = new URLSearchParams(window.location.hash).get("access_token");
    if (token) {
      const myHeaders = new Headers();
      myHeaders.append("Content-Type", "application/json");
      myHeaders.append("Accept", "application/json");

      fetch(`${process.env.NEXT_PUBLIC_API_URL}/users/register/google/`, {
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
    <div className="grid items-center justify-center py-10">
      <Image src={Logo} alt="Logo Rei e rainha da derivada" width={150} height={150} className="top-24 mx-auto left-o right-0" />
      <div className="grid col items-center justify-center gap-8">
        <Button variant={"outline"} onClick={() => { router.replace(rrddUrl) }} className="w-60 h-12 text-base font-semibold py-2 px-4 rounded-[10px] mt-6 fixed bottom-24 md:bottom-32 mx-auto left-0 right-0 md:text-xl">Saiba mais</Button>
        <Button variant='default' onClick={() => { router.replace(url) }} className="bg-blue-500 w-60 h-12 hover:bg-sky-800 text-base text-white font-semibold py-2 px-4 rounded-[10px] fixed bottom-10 mx-auto left-0 right-0 md:w-72 md:h-16 md:text-xl">
          Continuar com Google
        </Button>
      </div>

    </div>

  );
}
