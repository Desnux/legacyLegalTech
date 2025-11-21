"use client";

import { useState, useEffect } from "react";
import classNames from "classnames";
import Link from "next/link";
import { usePathname } from "next/navigation";

interface RouteItem {
  route: string;
  name: string;
  subroutes: RouteItem[];
}

const structure: RouteItem[] = [
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
  {
    route: "/demand-text/sender",
    name: "Enviar demanda",
    subroutes: [],
  },
  {
    route: "/supervisor/status",
    name: "Estado de avance",
    subroutes: [],
  },
  /*
  {
    route: "/example",
    name: "Ejemplo",
    subroutes: [
      {
        route: "/example/sub1",
        name: "Ejemplo sub 1",
        subroutes: [],
      },
      {
        route: "/example/sub2",
        name: "Ejemplo sub 2",
        subroutes: [],
      },
    ],
  },
  */
];

const Menu = ({ closeMenu }: { closeMenu?: () => void }) => {
  const pathname = usePathname(); // Obtiene la ruta actual
  const [openSections, setOpenSections] = useState<string[]>([]);

  // Función para detectar secciones que deben estar abiertas al cargar
  useEffect(() => {
    const getOpenSections = (items: typeof structure, path: string): string[] => {
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
  }, [pathname]);

  const toggleSection = (route: string) => {
    setOpenSections((prev) =>
      prev.includes(route)
        ? prev.filter((r) => r !== route) // Cierra la sección si está abierta
        : [...prev, route] // Abre la sección si está cerrada
    );
  };

  const handleLinkClick = (item: typeof structure[0]) => {
    // Si el enlace tiene subrutas y ya está activo, no cerrar el menú
    if (item.subroutes.length > 0 && pathname === item.route) return;
    if (closeMenu) closeMenu(); // De lo contrario, cerrar el menú
  };

  const renderMenuItems = (items: typeof structure) => {
    return items.map((item) => (
      <div key={item.route}>
        {/* Enlace principal */}
        <div
          className={classNames(
            "flex items-center justify-between rounded-md md:rounded-lg text-sm md:text-base",
            { "bg-blue-600 text-white hover:bg-blue-500": pathname === item.route },
            { "text-gray-900 hover:bg-blue-100 border border-gray-200 hover:border-blue-100": pathname !== item.route },
          )}
        >
          <Link
            href={item.route}
            onClick={() => handleLinkClick(item)}
            className="flex-1 px-4 py-2 rounded-md md:rounded-lg"
          >
            {item.name}
          </Link>
          {/* Botón para expandir/cerrar submenús */}
          {item.subroutes.length > 0 && (
            <button
              onClick={() => toggleSection(item.route)}
              className="mx-2 text-gray-600"
            >
              {openSections.includes(item.route) ? "▲" : "▼"}
            </button>
          )}
        </div>

        {/* Submenús */}
        {item.subroutes.length > 0 && openSections.includes(item.route) && (
          <div className="ml-4 mt-2">
            {renderMenuItems(item.subroutes)}
          </div>
        )}
      </div>
    ));
  };

  return (
    <nav className="w-64 h-full bg-gray-100 border-r border-gray-200 p-4 flex flex-col gap-y-2">
      {renderMenuItems(structure)}
    </nav>
  );
};

export default Menu;
