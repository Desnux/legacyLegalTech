"use client";

import { useState } from "react";
import classNames from "classnames";
import { usePathname } from "next/navigation";
import { Header, Footer, Menu } from "@/components/layout";
import { LOGIN_ROUTE } from "@/utils/auth-token";

const MainLayout = ({ children }: { children: React.ReactNode }) => {
  const [isMenuOpen, setMenuOpen] = useState<boolean>(false);
  const pathname = usePathname(); // Obtiene la ruta actual
  const isLoginPage = pathname === LOGIN_ROUTE; // Detecta si es la página de login

  return (
    <div className="flex flex-col h-full relative">
      {!isLoginPage && <Header isMenuOpen={isMenuOpen} setMenuOpen={setMenuOpen} />}
      <div className="flex flex-1 relative">
        {/* Menú lateral */}
        {!isLoginPage && <span className="fixed top-0 left-0 hidden md:block h-full mt-14"><Menu /></span>}
        {/* Contenido principal */}
        <main className={classNames("flex flex-col flex-1 items-center text-gray-900 pt-14", { "md:ml-64": !isLoginPage })}>
          <div className="flex flex-col flex-1 justify-stretch items-stretch md:px-4 max-w-screen-xl w-full">
            {children}
          </div>
        </main>
      </div>
      {!isLoginPage && <Footer />}
      {/* Menú deslizable */}
      {isMenuOpen && !isLoginPage && (
        <>
          <div className="fixed top-0 left-0 w-64 h-screen bg-gray-100 border-r border-gray-200 z-30 md:hidden">
            <Menu closeMenu={() => setMenuOpen(false)} />
          </div>
          <div
            className="absolute inset-0 bg-black bg-opacity-50 z-20 md:hidden"
            onClick={() => setMenuOpen(false)}
          />
        </>
      )}
    </div>
  );
};
  
export default MainLayout;
