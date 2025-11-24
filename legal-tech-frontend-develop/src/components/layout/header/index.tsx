"use client";

import { useEffect, useRef, useContext } from "react";
import Link from "next/link";
import Image from "next/image";
import { useRouter, usePathname } from "next/navigation";
import { IconDoorExit, IconMenu2, IconArrowLeft, IconShield, IconHome, IconLogout } from "@tabler/icons-react";
import { LOGIN_ROUTE, removeAuthTokenClient, removeRecepthorAuthTokenClient, removeUserGroupClient } from "@/utils/auth-token";
import { AuthContext } from "@/contexts/auth-context";

interface HeaderProps {
  isMenuOpen: boolean;
  setMenuOpen: (value: boolean) => void;
  isSidebarOpen?: boolean;
  setSidebarOpen?: (value: boolean) => void;
}

const Header = ({ isMenuOpen, setMenuOpen, isSidebarOpen, setSidebarOpen }: HeaderProps) => {
  const router = useRouter();
  const pathname = usePathname();
  const menuRef = useRef<HTMLButtonElement>(null);
  const { setAuth } = useContext(AuthContext);

  const handleLogout = async () => {
    try {
      await fetch("/api/logout", { method: "POST" });
      removeAuthTokenClient();
      removeRecepthorAuthTokenClient();
      removeUserGroupClient();
      setAuth({ token: null, group: null });
      router.push(LOGIN_ROUTE);
    } catch (error) {
      console.error("Error durante el logout:", error);
      removeAuthTokenClient();
      removeRecepthorAuthTokenClient();
      removeUserGroupClient();
      setAuth({ token: null, group: null });
      router.push(LOGIN_ROUTE);
    }
  };

  const handleGoBack = () => {
    router.back();
  };

  const handleGoHome = () => {
    router.push('/');
  };

  const getPageTitle = () => {
    const pathSegments = pathname.split('/').filter(Boolean);
    if (pathSegments.length === 0) return 'Inicio';
    
    const lastSegment = pathSegments[pathSegments.length - 1];
    const titleMap: { [key: string]: string } = {
      'users': 'Usuarios',
      'create': 'Crear Usuario',
      'statistics': 'Estadísticas',
      'case': 'Casos',
      'demand-text': 'Texto de Demanda',
      'preliminary-measure': 'Medida Precautoria',
      'supervisor': 'Supervisor',
      'status': 'Estado',
      'generator': 'Generador',
      'sender': 'Enviador'
    };
    
    return titleMap[lastSegment] || lastSegment.charAt(0).toUpperCase() + lastSegment.slice(1);
  };

  useEffect(() => {
    const handleOutsideClick = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setMenuOpen(false);
      }
    };

    if (isMenuOpen) {
      document.addEventListener("mousedown", handleOutsideClick);
    }

    return () => {
      document.removeEventListener("mousedown", handleOutsideClick);
    };
  }, [isMenuOpen]);

  return (
    <header className="fixed top-0 left-0 right-0 z-20 bg-pure-white/95 backdrop-blur-sm border-b border-medium-gray/50">
      <div className="flex items-center justify-between px-6 py-3">
        {/* Logo y Navegación */}
        <div className="flex items-center space-x-6">
          {/* Logo Minimalista */}
          <div className="flex items-center space-x-3">
            <div className="bg-gradient-to-r from-teal-green to-petroleum-blue rounded-lg p-2">
              <IconShield size={20} className="text-pure-white" />
            </div>
            <div className="hidden md:block">
              <h1 className="text-h3 font-serif text-petroleum-blue font-semibold">
                LegalTech
              </h1>
            </div>
          </div>

          {/* Navegación */}
          <div className="hidden md:flex items-center space-x-1">
            {/* Botón del sidebar */}
            {setSidebarOpen && (
              <button
                onClick={() => setSidebarOpen(!isSidebarOpen)}
                className="px-3 py-2 rounded-lg text-charcoal-gray hover:bg-light-gray transition-colors duration-200"
                title={isSidebarOpen ? "Ocultar menú" : "Mostrar menú"}
              >
                <IconMenu2 size={18} />
              </button>
            )}
            
            <button
              onClick={handleGoHome}
              className="px-3 py-2 rounded-lg text-charcoal-gray hover:bg-light-gray transition-colors duration-200"
              title="Inicio"
            >
              <IconHome size={18} />
            </button>
            
            <button
              onClick={handleGoBack}
              className="px-3 py-2 rounded-lg text-charcoal-gray hover:bg-light-gray transition-colors duration-200"
              title="Atrás"
            >
              <IconArrowLeft size={18} />
            </button>
          </div>
        </div>

        {/* Título de Página */}
        {/* <div className="flex-1 flex justify-center">
          <h2 className="text-h3 font-medium text-charcoal-gray">
            {getPageTitle()}
          </h2>
        </div> */}

        {/* Acciones */}
        <div className="flex items-center space-x-2">
          {/* Botón de menú móvil */}
          <button
            ref={menuRef}
            onClick={() => setMenuOpen(!isMenuOpen)}
            className="md:hidden p-2 rounded-lg text-charcoal-gray hover:bg-light-gray transition-colors duration-200"
          >
            <IconMenu2 size={20} />
          </button>

          {/* Botones de navegación móvil */}
          <div className="md:hidden flex items-center space-x-1">
            <button
              onClick={handleGoHome}
              className="p-2 rounded-lg text-charcoal-gray hover:bg-light-gray transition-colors duration-200"
              title="Inicio"
            >
              <IconHome size={18} />
            </button>
            
            <button
              onClick={handleGoBack}
              className="p-2 rounded-lg text-charcoal-gray hover:bg-light-gray transition-colors duration-200"
              title="Atrás"
            >
              <IconArrowLeft size={18} />
            </button>
          </div>

          {/* Botón de logout moderno */}
          <button
            onClick={handleLogout}
            className="group relative p-2 rounded-lg text-medium-gray hover:text-red-500 hover:bg-red-50 transition-all duration-200"
            title="Cerrar sesión"
          >
            <IconLogout size={18} />
            <span className="hidden md:block absolute right-0 top-full mt-1 px-2 py-1 bg-charcoal-gray text-pure-white text-small rounded text-center opacity-0 group-hover:opacity-100 transition-opacity duration-200 whitespace-nowrap">
              Cerrar sesión
            </span>
          </button>
        </div>
      </div>
    </header>
  );
};
  
export default Header;
