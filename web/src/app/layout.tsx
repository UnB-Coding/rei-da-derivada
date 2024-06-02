import type { Metadata } from "next";
import { Inter } from "next/font/google";
import  UserContextProvider  from "@/app/contexts/UserContext";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "RRDD App",
  description: "Gerenciador de eventos",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <UserContextProvider>
        {children}
        </UserContextProvider>
      </body>
    </html>
  );
}
