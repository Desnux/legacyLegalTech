"use client";

import { useContext, useEffect, useState } from "react";
import { AuthContext } from "@/contexts/auth-context";
import classNames from "classnames";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { IconCaretDownFilled, IconCaretUpFilled } from "@tabler/icons-react";

interface RouteItem {
  route: string;
  name: string;
  subroutes: RouteItem[];
}

const executiveStructure: RouteItem[] = [
  {
    route: "/",
    name: "Portada",
    subroutes: [],
  },
  {
    route: "/demand-text/generator",
    name: "Generar demanda",
    subroutes: [],
  },
  /*
  {
    route: "/demand-text/sender",
    name: "Enviar demanda",
    subroutes: [],
  },
  */
  {
    route: "/supervisor/status",
    name: "Estado de avance",
    subroutes: [
      {
        route: "/supervisor/banco-bci/status",
        name: "Banco BCI",
        subroutes: [],
      },
      {
        route: "/supervisor/banco-consorcio/status",
        name: "Banco Consorcio",
        subroutes: [],
      },
      {
        route: "/supervisor/banco-de-chile/status",
        name: "Banco de Chile",
        subroutes: [],
      },
      {
        route: "/supervisor/banco-estado/status",
        name: "Banco Estado",
        subroutes: [],
      },
      {
        route: "/supervisor/banco-itau/status",
        name: "Banco Itaú",
        subroutes: [],
      },
      {
        route: "/supervisor/banco-santander/status",
        name: "Banco Santander",
        subroutes: [],
      },
      {
        route: "/supervisor/banco-security/status",
        name: "Banco Security",
        subroutes: [],
      },
      {
        route: "/supervisor/scotiabank/status",
        name: "Scotiabank",
        subroutes: [],
      },
    ],
  },
];

const inHouseStructure: RouteItem[] = [
  {
    route: "/",
    name: "Portada",
    subroutes: [],
  },
  {
    route: "/preliminary-measure/generator",
    name: "Generar medida",
    subroutes: [],
  },
];

const Menu = ({ closeMenu }: { closeMenu?: () => void }) => {
  const pathname = usePathname(); // Obtiene la ruta actual
  const [openSections, setOpenSections] = useState<string[]>([]);
  const { group } = useContext(AuthContext);

  let structure = inHouseStructure;
  if (group === "executive_case") {
    structure = executiveStructure;
  }

  // Función para detectar secciones que deben estar abiertas al cargar
  useEffect(() => {
    const getOpenSections = (items: RouteItem[], path: string): string[] => {
      let sections: string[] = [];

      items.forEach((item) => {
        if (item.subroutes.length > 0) {
          // Si la ruta actual está en algún submenú, agrega la sección padre
          const isSubrouteActive = item.subroutes.some(
            (sub) => sub.route === path || path.startsWith(sub.route)
          );
          if (isSubrouteActive) {
            sections.push(item.route);
          }

          // Recursivamente busca en los submenús
          sections = [...sections, ...getOpenSections(item.subroutes, path)];
        }
      });

      return sections;
    };

    // Establecer las secciones abiertas según la ruta actual
    const initialOpenSections = getOpenSections(structure, pathname);
    setOpenSections(initialOpenSections);
  }, [structure, pathname]);

  const toggleSection = (route: string) => {
    setOpenSections((prev) =>
      prev.includes(route)
        ? prev.filter((r) => r !== route) // Cierra la sección si está abierta
        : [...prev, route] // Abre la sección si está cerrada
    );
  };

  const handleLinkClick = (item: RouteItem) => {
    // Si el enlace tiene subrutas y ya está activo, no cerrar el menú
    if (item.subroutes.length > 0 && pathname === item.route) return;
    if (closeMenu) closeMenu(); // De lo contrario, cerrar el menú
  };

  const hasCurrentInSubroutes = (subroutes: RouteItem[]): boolean => {
    return subroutes.some(
      (sub) => sub.route === pathname || (sub.subroutes && hasCurrentInSubroutes(sub.subroutes))
    );
  };

  const renderMenuItems = (items: RouteItem[]) => {
    return items.map((item) => {
      const isCurrent = pathname === item.route;
      const isParent = hasCurrentInSubroutes(item.subroutes) && !isCurrent;
      return (
      <div key={item.route}>
        {/* Enlace principal */}
        <div
          className={classNames(
            "flex items-center justify-between border rounded-md md:rounded-lg text-sm md:text-base",
            { "bg-blue-600 text-white border-blue-600 hover:bg-blue-500": isCurrent },
            { "text-gray-900 hover:bg-blue-100 border-blue-600 hover:border-blue-500": isParent },
            { "text-gray-900 hover:bg-blue-100 border-gray-200 hover:border-blue-100": !isCurrent && !isParent },
          )}
        >
          <Link
            href={item.route}
            onClick={() => handleLinkClick(item)}
            className="flex-1 px-4 py-1 rounded-md md:rounded-lg"
          >
            {item.name}
          </Link>
          {/* Botón para expandir/cerrar submenús */}
          {item.subroutes.length > 0 && (isParent || isCurrent) && (
            <div className={classNames(
              "mx-2 flex items-center justify-center pl-2 border-l",
              { "text-white border-white" : isCurrent },
              { "text-blue-600 border-blue-600" : isParent },
              { "text-gray-600 border-transparent" : !isCurrent && !isParent },
            )}>
              <button onClick={() => toggleSection(item.route)}>
                {openSections.includes(item.route) 
                  ? <IconCaretUpFilled className="translate-y-px"/>
                  : <IconCaretDownFilled/>
                }
              </button>
            </div>
          )}
        </div>

        {/* Submenús */}
        {item.subroutes.length > 0 && openSections.includes(item.route) && (
          <div className="ml-4 mt-2 flex flex-col gap-y-2">
            {renderMenuItems(item.subroutes)}
          </div>
        )}
      </div>
    )});
  };

  return (
    <nav className="w-64 h-full bg-gray-100 border-r border-gray-200 p-4 flex flex-col gap-y-2 overflow-y-auto">
      {renderMenuItems(structure)}
    </nav>
  );
};

export default Menu;
