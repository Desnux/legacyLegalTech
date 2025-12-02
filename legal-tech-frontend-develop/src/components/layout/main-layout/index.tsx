"use client";

import { useState, useEffect } from "react";
import classNames from "classnames";
import { usePathname, useRouter } from "next/navigation";
import { Header, Footer, Menu, SidebarMenu } from "@/components/layout";
import { AuthProvider } from "@/contexts/auth-context";
import { LOGIN_ROUTE } from "@/utils/auth-token";
import { IconHome } from "@tabler/icons-react";

const MainLayout = ({ children }: { children: React.ReactNode }) => {
  const [isMenuOpen, setMenuOpen] = useState<boolean>(false);
  const [isDesktopMenuOpen, setIsDesktopMenuOpen] = useState<boolean>(true);
  const [showButton, setShowButton] = useState(false);
  const pathname = usePathname();
  const router = useRouter();
  const isLoginPage = pathname === LOGIN_ROUTE;
  const isHomePage = pathname === '/';

  useEffect(() => {
    const handleScroll = () => setShowButton(window.scrollY > 50);
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const handleHomeRedirect = () => {
    router.push('/');
  };

  return (
    <AuthProvider>
      <div className="flex flex-col h-full">
        {!isLoginPage && (
          <Header 
            isMenuOpen={isMenuOpen} 
            setMenuOpen={setMenuOpen}
            isSidebarOpen={isDesktopMenuOpen}
            setSidebarOpen={setIsDesktopMenuOpen}
          />
        )}
        <div className="flex flex-1 flex-col">
          {/* Sidebar Menu */}
          {!isLoginPage && (
            <SidebarMenu 
              isOpen={isDesktopMenuOpen} 
              onToggle={() => setIsDesktopMenuOpen(!isDesktopMenuOpen)} 
            />
          )}
          {/* Contenido principal */}
          <main className={classNames(
            "flex flex-col items-center text-charcoal-gray mt-14 bg-light-gray flex-1 transition-all duration-300",
            { "lg:ml-80": isDesktopMenuOpen && !isLoginPage }
          )}>
            <div className="flex flex-col justify-stretch items-stretch max-w-screen-xl w-full flex-1">
              {children}
            </div>
          </main>
        </div>
        {!isLoginPage && <Footer />}
        {showButton && (
          <button
            onClick={scrollToTop}
            className={classNames(
              "fixed right-5 bg-teal-green hover:bg-teal-green/90 text-pure-white font-bold py-3 px-4 rounded-full shadow-lg z-50 transition-all duration-300",
              isHomePage ? "bottom-5" : "bottom-[72px]"
            )}
          >
            ↑ Subir
          </button>
        )}
        {!isLoginPage && !isHomePage && (
          <div className="fixed bottom-5 right-5 bg-teal-green hover:bg-teal-green/90 text-pure-white font-bold py-3 px-4 rounded-full shadow-lg z-50 transition-all duration-300">
            <button onClick={handleHomeRedirect} className="flex items-center gap-1">
              <IconHome size={16} />
              <span>Inicio</span>
            </button>
          </div>
        )}
      </div>
    </AuthProvider>
  );
};
  
export default MainLayout;