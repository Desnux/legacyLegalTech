"use client";

import { useState, useEffect } from "react";
import classNames from "classnames";
import { usePathname } from "next/navigation";
import { Header, Footer, Menu } from "@/components/layout";
import { AuthProvider } from "@/contexts/auth-context";
import { LOGIN_ROUTE } from "@/utils/auth-token";

const MainLayout = ({ children }: { children: React.ReactNode }) => {
  const [isMenuOpen, setMenuOpen] = useState<boolean>(false);
  const [showButton, setShowButton] = useState(false);
  const pathname = usePathname(); // Obtiene la ruta actual
  const isLoginPage = pathname === LOGIN_ROUTE; // Detecta si es la página de login

  useEffect(() => {
    const handleScroll = () => setShowButton(window.scrollY > 50);
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  return (
    <AuthProvider>
      <div className="flex flex-col h-full relative">
        {!isLoginPage && <Header isMenuOpen={isMenuOpen} setMenuOpen={setMenuOpen} />}
        <div className="flex flex-1 flex-col relative">
          {/* Menú lateral */}
          {!isLoginPage && <span className="fixed top-0 left-0 hidden z-20 md:block h-[calc(100vh-56px)] mt-14"><Menu /></span>}
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
              className="fixed inset-0 bg-black bg-opacity-50 z-20 md:hidden"
              onClick={() => setMenuOpen(false)}
            />
          </>
        )}
        {showButton && (
          <button
            onClick={scrollToTop}
            className="fixed bottom-5 right-5 bg-blue-600 hover:bg-blue-500 text-white font-bold py-3 px-4 rounded-full shadow-lg z-50 transition-all duration-300"
          >
            ↑ Subir
          </button>
        )}
      </div>
    </AuthProvider>
  );
};
  
export default MainLayout;