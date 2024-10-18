import type { Metadata, Viewport } from "next";
import { Outfit } from "next/font/google";
import  UserContextProvider  from "@/app/contexts/UserContext";
import EventContextProvider from "./contexts/EventContext";
import { Toaster } from "react-hot-toast";
import { NextUIProvider } from "@nextui-org/react";
import "./globals.css";
const APP_NAME = "PWA Rei da derivada";
const APP_DEFAULT_TITLE = "RRDD App";
const APP_TITLE_TEMPLATE = "%s - PWA App";
const APP_DESCRIPTION = "Gerenciador de eventos!";

const outfit = Outfit({ subsets: ["latin"] });

// export const metadata: Metadata = {
//   title: "RRDD App",
//   description: "Gerenciador de eventos",
// };
export const metadata: Metadata = {
  applicationName: APP_NAME,
  title: {
    default: APP_DEFAULT_TITLE,
    template: APP_TITLE_TEMPLATE,
  },
  description: APP_DESCRIPTION,
  manifest: "/manifest.json",
  appleWebApp: {
    capable: true,
    statusBarStyle: "default",
    title: APP_DEFAULT_TITLE,
    // startUpImage: [],
  },
  formatDetection: {
    telephone: false,
  },
  openGraph: {
    type: "website",
    siteName: APP_NAME,
    title: {
      default: APP_DEFAULT_TITLE,
      template: APP_TITLE_TEMPLATE,
    },
    description: APP_DESCRIPTION,
  },
  twitter: {
    card: "summary",
    title: {
      default: APP_DEFAULT_TITLE,
      template: APP_TITLE_TEMPLATE,
    },
    description: APP_DESCRIPTION,
  },
};

export const viewport: Viewport = {
  themeColor: "#FFFFFF",
};


export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning={true}>
      <body className={outfit.className} suppressHydrationWarning={true}>
      <Toaster position="top-center" />
        <NextUIProvider>
        <UserContextProvider>
          <EventContextProvider>
            {children}
          </EventContextProvider>
        </UserContextProvider>
        </NextUIProvider>
      </body>
    </html>
  );
}
