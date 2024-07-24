import type { Metadata } from "next";
import { Outfit } from "next/font/google";
import  UserContextProvider  from "@/app/contexts/UserContext";
import EventContextProvider from "./contexts/EventContext";
import { Toaster } from "react-hot-toast";
import "./globals.css";

const outfit = Outfit({ subsets: ["latin"] });

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
      <body className={outfit.className}>
      <Toaster position="top-center" />
        <UserContextProvider>
          <EventContextProvider>
            {children}
          </EventContextProvider>
        </UserContextProvider>
      </body>
    </html>
  );
}
