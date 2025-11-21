"use client";

import { useEffect, useState, useRef } from "react";
import { useRouter, usePathname } from "next/navigation";
import { IconDoorExit, IconMenu2 } from "@tabler/icons-react";
import Link from "next/link";
import Image from "next/image";
import { LOGIN_ROUTE, getAuthToken, removeAuthToken, setPreviousRoute, removePreviousRoute } from "@/utils/auth-token";

interface HeaderProps {
  isMenuOpen: boolean;
  setMenuOpen: (value: boolean) => void;
}

const Header = ({ isMenuOpen, setMenuOpen }: HeaderProps) => {
  const router = useRouter();
  const pathname = usePathname(); // Captura la ruta actual

  const [token, setToken] = useState<string | null>(null);
  const menuRef = useRef<HTMLDivElement>(null); // Referencia para el menú

  const handleLogout = () => {
    removePreviousRoute();
    removeAuthToken();
    setToken(null);
  };

  // Detecta clics fuera del menú
  useEffect(() => {
    const handleOutsideClick = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setMenuOpen(false); // Cierra el menú si el clic fue fuera del menú
      }
    };

    if (isMenuOpen) {
      document.addEventListener("mousedown", handleOutsideClick);
    }

    return () => {
      document.removeEventListener("mousedown", handleOutsideClick);
    };
  }, [isMenuOpen]);

  useEffect(() => {
    setPreviousRoute(pathname); // Guarda la ruta anterior en sessionStorage
    const storedToken = getAuthToken();

    if (storedToken === null) {
      router.push(LOGIN_ROUTE); // Redirige a la página de login si no hay token
    } else {
      setToken(storedToken);
    }
  }, [token]);

  return (
    <header className="fixed top-0 left-0 right-0 z-20 flex flex-col grow-0 shrink-0 basis-auto min-h-[56px] bg-gray-100 items-center border-b border-gray-200">
      <div className="flex flex-1 items-center justify-between px-4 w-full">
        {/* Botón burger */}
        <button
          onClick={() => setMenuOpen(!isMenuOpen)}
          className="block md:hidden bg-gray-600 hover:bg-gray-500 p-2 rounded-lg items-center gap-x-2"
        >
          <IconMenu2 size={18}/>
        </button>
        <div className="flex flex-1 md:flex-initial items-center justify-center md:justify-start">
          <Link href="/">
            <Image src="/logo-header.png" className="block w-auto h-10" alt="Titan Group Logo" width={192} height={80}/>
          </Link>
        </div>
        <button className="bg-gray-600 hover:bg-gray-500 p-2 rounded-lg flex gap-x-2 items-center" onClick={handleLogout}>
          <div className="hidden md:block">Salir</div>
          <IconDoorExit size={18}/>
        </button>
      </div>
    </header>
  );
};
  
export default Header;
