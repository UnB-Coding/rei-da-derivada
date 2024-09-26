"use client"

import { Home, User, Trophy, Clipboard, Shield, CalendarDays } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";

type UserType = 'player' | 'staff' | 'manager' | 'admin' | 'common';

type NavItem = {
    icon: React.ReactNode
    label: string
    href: string
}

const navItems: Record<UserType, NavItem[]> = {
    player: [
        { icon: <Home className="h-6 w-6" />, label: 'Home', href: '/' },
        { icon: <User className="h-6 w-6" />, label: 'Profile', href: '/profile' },
        { icon: <Trophy className="h-6 w-6" />, label: 'Trophies', href: '/trophies' },
    ],
    staff: [
        { icon: <Home className="h-6 w-6" />, label: 'Home', href: '/' },
        { icon: <Trophy className="h-6 w-6" />, label: 'Trophies', href: '/trophies' },
        { icon: <Clipboard className="h-6 w-6" />, label: 'Tasks', href: '/tasks' },
    ],
    admin: [
        { icon: <Shield className="h-6 w-6" />, label: 'Admin', href: '/admin' },
        { icon: <Clipboard className="h-6 w-6" />, label: 'Tasks', href: '/tasks' },
        { icon: <Trophy className="h-6 w-6" />, label: 'Trophies', href: '/trophies' },
        { icon: <Home className="h-6 w-6" />, label: 'Home', href: '/' },
    ],
    manager: [
        { icon: <Shield className="h-6 w-6" />, label: 'Admin', href: '/admin' },
        { icon: <Clipboard className="h-6 w-6" />, label: 'Tasks', href: '/tasks' },
        { icon: <Trophy className="h-6 w-6" />, label: 'Trophies', href: '/trophies' },
        { icon: <Home className="h-6 w-6 " />, label: 'Home', href: '/' },
    ],
    common: [
        { icon: <Home className="h-6 w-6 bg-primary" />, label: 'Home', href: '/home' },
        { icon: <CalendarDays className="h-6 w-6 bg-primary" />, label: 'Events', href: '/contests' },
    ]
}

export default function Navbar({ userType = 'player' }: { userType?: UserType }) {
    const items = navItems[userType];
    const pathname = usePathname().split('/')[2];

    return (
        <nav className="fixed bottom-0 left-0 right-0 md:static md:mx-auto md:my-4 md:max-w-2xl md:rounded-full bg-secondary shadow-lg">
            <div className="flex justify-evenly items-center h-16 px-4">
                {items.map((item, index) => {
                    const isActive = pathname === item.href
                    return (
                        <Link
                            key={index}
                            href={item.href}
                            className={`flex flex-col items-center transition-colors ${isActive
                                    ? 'text-secondary font-bold'
                                    : 'text-primary-foreground hover:text-primary-foreground/80'
                                }`}
                            aria-current={isActive ? 'page' : undefined}
                        >
                            {item.icon}
                            <span className="text-xs mt-1">{item.label}</span>
                            {isActive && (
                                <span className="sr-only">(current page)</span>
                            )}
                        </Link>
                    )
                })}
            </div>
        </nav>
    );
}

