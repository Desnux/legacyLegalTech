"use client";

import { useRouter } from "next/navigation";
import { useContext, useState, useEffect } from "react";
import { 
  IconGavel, 
  IconUsers, 
  IconChartBar, 
  IconBuildingBank, 
  IconUserPlus, 
  IconList, 
  IconHome, 
  IconFileText, 
  IconScale,
  IconChevronDown,
  IconChevronRight,
  IconMenu2,
  IconX
} from "@tabler/icons-react";
import { AuthContext } from "@/contexts/auth-context";

interface SidebarMenuProps {
  isOpen: boolean;
  onToggle: () => void;
}

const SidebarMenu = ({ isOpen, onToggle }: SidebarMenuProps) => {
  const router = useRouter();
  const { group, token, isLoading } = useContext(AuthContext);
  const [expandedSections, setExpandedSections] = useState<{ [key: string]: boolean }>({});

  const canViewSection = (requiredRole: string) => {
    const canView = group === requiredRole || group === "admin";
    return canView;
  };

  useEffect(() => {
    if (Object.keys(expandedSections).length === 0 && group) {
      let firstSection = null;
      
      if (canViewSection("admin")) {
        firstSection = "admin";
      } else if (canViewSection("supervisor")) {
        firstSection = "supervisor";
      } else if (canViewSection("lawyer")) {
        firstSection = "lawyer";
      } else if (canViewSection("bank")) {
        firstSection = "bank";
      }
      
      if (firstSection) {
        setExpandedSections(prev => ({
          ...prev,
          [firstSection]: true
        }));
      }
    }
  }, [group]);

  const toggleSection = (section: string) => {
    setExpandedSections(prev => {
      const isCurrentlyExpanded = prev[section] !== undefined ? prev[section] : true;
      
      if (isCurrentlyExpanded) {
        return {
          ...prev,
          [section]: false
        };
      } else {
        const newState = { ...prev };
        Object.keys(newState).forEach(key => {
          newState[key] = false;
        });
        newState[section] = true;
        return newState;
      }
    });
  };

  const openSection = (sectionKey: string) => {
    setExpandedSections(prev => {
      const newState = { ...prev };
      Object.keys(newState).forEach(key => {
        newState[key] = false;
      });
      newState[sectionKey] = true;
      return newState;
    });
  };

  const handleDemandGenerator = () => {
    if (!canViewSection("lawyer")) {
      alert("No tienes permisos para acceder a esta funcionalidad");
      return;
    }
    
    if (!router) {
      console.error("Router no disponible");
      return;
    }
    
    try {
      setTimeout(() => {
        router.push('/demand-text/generator');
      }, 100);
      onToggle();
    } catch (error) {
      console.error("Error en navegación:", error);
    }
  };

  const handleDemandManagement = () => {
    if (!canViewSection("lawyer")) {
      alert("No tienes permisos para acceder a esta funcionalidad");
      return;
    }
    
    if (!router) {
      console.error("Router no disponible");
      return;
    }
    
    try {
      setTimeout(() => {
        router.push('/case/actions');
      }, 100);
      onToggle();
    } catch (error) {
      console.error("Error en navegación:", error);
    }
  };

  const handleDemandStatus = () => {
    if (!canViewSection("supervisor") && !canViewSection("lawyer")) {
      alert("No tienes permisos para acceder a esta funcionalidad");
      return;
    }
    openSection("supervisor");
    
    if (!router) {
      console.error("Router no disponible");
      return;
    }
    
    try {
      setTimeout(() => {
        router.push('/supervisor/status');
      }, 100);
    onToggle();
    } catch (error) {
      console.error("Error en navegación:", error);
    }
  };

  const handleCreateUser = () => {
    if (!canViewSection("admin")) {
      alert("No tienes permisos para acceder a esta funcionalidad");
      return;
    }
    openSection("admin");
    try {
      setTimeout(() => {
        router.push('/users/create');
      }, 100);
      onToggle();
    } catch (error) {
      console.error("Error en navegación:", error);
    }
  };

  const handleListUsers = () => {
    if (!canViewSection("admin")) {
      alert("No tienes permisos para acceder a esta funcionalidad");
      return;
    }
    openSection("admin");
    try {
      setTimeout(() => {
        router.push('/users');
      }, 100);
      onToggle();
    } catch (error) {
      console.error("Error en navegación:", error);
    }
  };

  const handleStatistics = () => {
    if (!canViewSection("supervisor")) {
      alert("No tienes permisos para acceder a esta funcionalidad");
      return;
    }
    openSection("supervisor");
    try {
      setTimeout(() => {
        router.push('/supervisor/statistics');
      }, 100);
      onToggle();
    } catch (error) {
      console.error("Error en navegación:", error);
    }
  };

  const handleHome = () => {
    onToggle();
    try {
      setTimeout(() => {
        router.push('/');
      }, 100);
    } catch (error) {
      console.error("Error en navegación:", error);
    }
  };

  if (isLoading) {
    return (
      <div className={`fixed top-0 left-0 h-full bg-pure-white shadow-lg transition-all duration-300 z-50 ${
        isOpen ? 'w-80' : 'w-0'
      } overflow-hidden`}>
        <div className="flex items-center justify-center h-full">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-green mx-auto mb-4"></div>
            <p className="text-charcoal-gray">Cargando...</p>
          </div>
        </div>
      </div>
    );
  }

  const MenuSection = ({ 
    sectionKey, 
    title, 
    icon: Icon, 
    gradientFrom, 
    gradientTo, 
    children,
    isOpen,
  }: {
    sectionKey: string;
    title: string;
    icon: any;
    gradientFrom: string;
    gradientTo: string;
    children: React.ReactNode;
    isOpen: boolean;
  }) => {
    const canView = canViewSection(sectionKey);
    
    if (!canView) return null;

    const isExpanded = expandedSections[sectionKey] !== undefined 
      ? expandedSections[sectionKey] 
      : isOpen;

    return (
      <div className="mb-2">
        <button
          onClick={() => toggleSection(sectionKey)}
          className={`w-full flex items-center justify-between px-3 py-2 bg-gradient-to-r ${gradientFrom} ${gradientTo} text-pure-white rounded-md hover:opacity-90 transition-colors duration-200`}
        >
          <div className="flex items-center gap-2">
            <Icon size={16} className="text-pure-white" />
            <span className="font-medium text-sm leading-none">{title}</span>
          </div>
          <div className={`transition-transform duration-200 ease-in-out ${
            isExpanded ? 'rotate-90' : 'rotate-0'
          }`}>
            <IconChevronRight size={16} className="text-pure-white" />
          </div>
        </button>
        
        <div 
          className={`overflow-hidden transition-[max-height,opacity] duration-200 ease-in-out ${
            isExpanded ? 'max-h-80 opacity-100' : 'max-h-0 opacity-0'
          }`}
        >
          <div className={`mt-1 space-y-1 pl-3`}>
            {children}
          </div>
        </div>
      </div>
    );
  };

  const MenuItem = ({ 
    onClick, 
    icon: Icon, 
    title, 
    bgColor = "bg-petroleum-blue",
    hoverColor = "hover:bg-petroleum-blue/90",
    delay = 0,
    isExpanded = true
  }: {
    onClick: () => void;
    icon: any;
    title: string;
    bgColor?: string;
    hoverColor?: string;
    delay?: number;
    isExpanded?: boolean;
  }) => (
    <div 
      className={`${isExpanded ? 'opacity-100' : 'opacity-0'} transition-opacity duration-200`}
      style={{ transitionDelay: `${delay}ms` }}
    >
      <button
        onClick={onClick}
        className={`w-full flex items-center gap-2 px-3 py-2 ${bgColor} text-pure-white rounded-md ${hoverColor} transition-colors duration-200 text-left`}
      >
        <Icon size={16} />
        <div className="flex-1 min-w-0">
          <div className="font-medium text-sm truncate">{title}</div>
        </div>
      </button>
    </div>
  );

  return (
    <>
      {isOpen && (
        <div 
          className="fixed top-14 left-0 right-0 bottom-0 bg-black bg-opacity-50 z-30 lg:hidden"
          onClick={onToggle}
        />
      )}
      
      <div className={`fixed top-14 mt-1 left-0 h-[calc(100vh-56px)] bg-gray-50 border-r border-gray-200 transition-all duration-300 z-40 ${
        isOpen ? 'w-60' : 'w-0'
      } overflow-hidden`}>
        <div className="h-full flex flex-col">
          <div className="flex-1 overflow-y-auto px-1 mt-1 [&::-webkit-scrollbar]:hidden [-ms-overflow-style:none] [scrollbar-width:none]">

            <div className="mt-0 space-y-2">
              <MenuSection
                sectionKey="lawyer"
                title="Abogado"
                icon={IconGavel}
                gradientFrom="from-petroleum-blue"
                gradientTo="to-petroleum-blue/90"
                isOpen={true}
              >
                <MenuItem
                  onClick={handleDemandGenerator}
                  icon={IconFileText}
                  title="Gestionar Demanda"
                  bgColor="bg-teal-green"
                  hoverColor="hover:bg-teal-green/90"
                  delay={100}
                  isExpanded={expandedSections["lawyer"]}
                />
                <MenuItem
                  onClick={handleDemandManagement}
                  icon={IconScale}
                  title="Gestionar Juicios"
                  delay={200}
                  isExpanded={expandedSections["lawyer"]}
                />
                <MenuItem
                  onClick={handleDemandStatus}
                  icon={IconChartBar}
                  title="Estado de avance"
                  delay={300}
                  isExpanded={expandedSections["lawyer"]}
                />
              </MenuSection>

              <MenuSection
                sectionKey="supervisor"
                title="Supervisor"
                icon={IconUsers}
                gradientFrom="from-teal-green"
                gradientTo="to-teal-green/90"
                isOpen={false}
              >
                <MenuItem
                  onClick={handleStatistics}
                  icon={IconChartBar}
                  title="Estadísticas de Juicios"
                  bgColor="bg-teal-green"
                  hoverColor="hover:bg-teal-green/90"
                  delay={100}
                  isExpanded={expandedSections["supervisor"]}
                />
                <MenuItem
                  onClick={handleDemandStatus}
                  icon={IconChartBar}
                  title="Estado de Avance"
                  delay={200}
                  isExpanded={expandedSections["supervisor"]}
                />
              </MenuSection>

              <MenuSection
                sectionKey="bank"
                title="Banco"
                icon={IconBuildingBank}
                gradientFrom="from-soft-gold"
                gradientTo="to-soft-gold/90"
                isOpen={false}
              >
                <MenuItem
                  onClick={() => {}}
                  icon={IconBuildingBank}
                  title="Comercial"
                  bgColor="bg-teal-green"
                  hoverColor="hover:bg-teal-green/90"
                  delay={100}
                  isExpanded={expandedSections["bank"]}
                />
                <MenuItem
                  onClick={() => {}}
                  icon={IconChartBar}
                  title="Operaciones"
                  delay={200}
                  isExpanded={expandedSections["bank"]}
                />
              </MenuSection>

              <MenuSection
                sectionKey="admin"
                title="Administración"
                icon={IconUsers}
                gradientFrom="from-charcoal-gray"
                gradientTo="to-charcoal-gray/90"
                isOpen={false}
              >
                <MenuItem
                  onClick={handleCreateUser}
                  icon={IconUserPlus}
                  title="Crear Usuario"
                  bgColor="bg-teal-green"
                  hoverColor="hover:bg-teal-green/90"
                  delay={100}
                  isExpanded={expandedSections["admin"]}
                />
                <MenuItem
                  onClick={handleListUsers}
                  icon={IconList}
                  title="Listar Usuarios"
                  delay={200}
                  isExpanded={expandedSections["admin"]}
                />
              </MenuSection>
            </div>

            {!group && !isLoading && (
              <div className="mt-6 p-3 bg-light-gray rounded-lg">
                <div className="text-center">
                  <div className="w-8 h-8 bg-medium-gray rounded-full flex items-center justify-center mx-auto mb-2">
                    <IconUsers size={16} className="text-charcoal-gray" />
                  </div>
                  <h3 className="text-xs font-semibold text-petroleum-blue mb-1">Sin permisos asignados</h3>
                  <p className="text-xs text-charcoal-gray">Contacta al administrador para obtener acceso.</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </>
  );
};

export default SidebarMenu;
