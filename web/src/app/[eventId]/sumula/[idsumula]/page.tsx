'use client'
import { useRouter } from "next/navigation";

export default function SumulaId() {
    const router = useRouter();
    return (
        <>
            <p>Eu sou uma súmula</p>
            <button onClick={() => {router.push('../sumula')}}>Voltar</button>
        </>
    );
};