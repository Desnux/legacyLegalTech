import { useRouter } from "next/navigation";
import { useContext, useEffect } from "react";
import { IconGavel, IconUsers, IconChartBar, IconBuildingBank, IconUserPlus, IconList, IconHome, IconFileText, IconScale } from "@tabler/icons-react";
import { AuthContext } from "@/contexts/auth-context";

const PrincipalMenu = () => {
    const router = useRouter();
    const { group, token, isLoading } = useContext(AuthContext);

    const handleDemandGenerator = () => {
      if (group !== "lawyer" && group !== "admin") {
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
      } catch (error) {
        console.error("Error en navegación:", error);
      }
    };
  
    const handleDemandStatus = () => {
      
      if (group !== "supervisor" && group !== "lawyer" && group !== "admin") {
        alert("No tienes permisos para acceder a esta funcionalidad");
        return;
      }
      
      if (!router) {
        console.error("Router no disponible");
        return;
      }
      
      try {
        setTimeout(() => {
          router.push('/supervisor/status');
        }, 100);
      } catch (error) {
        console.error("Error en navegación:", error);
      }
    };

    const handleCreateUser = () => {
      if (group !== "admin") {
        alert("No tienes permisos para acceder a esta funcionalidad");
        return;
      }
      
      try {
        setTimeout(() => {
          router.push('/users/create');
        }, 100);
      } catch (error) {
        console.error("Error en navegación:", error);
      }
    }

    const handleDemandManagement = () => {
      if (group !== "lawyer" && group !== "admin") {
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
      } catch (error) {
        console.error("Error en navegación:", error);
      }
    };

    const handleListUsers = () => {
      if (group !== "admin") {
        alert("No tienes permisos para acceder a esta funcionalidad");
        return;
      }
      
      try {
        setTimeout(() => {
          router.push('/users');
        }, 100);
      } catch (error) {
        console.error("Error en navegación:", error);
      }
    }

    const handleStatistics = () => {
      if (group !== "supervisor" && group !== "admin") {
        alert("No tienes permisos para acceder a esta funcionalidad");
        return;
      }

      try {
        setTimeout(() => {
          router.push('/supervisor/statistics');
        }, 100);
      } catch (error) {
        console.error("Error en navegación:", error);
      }
    }

    if (isLoading) {
      return (
        <div className="flex-1 h-full bg-light-gray flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-green mx-auto mb-4"></div>
            <p className="text-charcoal-gray">Cargando...</p>
          </div>
        </div>
      );
    }

    const canViewSection = (requiredRole: string) => {
      const canView = group === requiredRole || group === "admin";
      return canView;
    };

  return (
    <div className="flex-1 h-full bg-light-gray">
      <div className="container mx-auto px-4 py-12 max-w-4xl">
        <div className="text-center mb-12">
          <h1 className="text-h1 font-serif text-petroleum-blue mb-4">Bienvenido a la plataforma</h1>
          <p className="text-body text-charcoal-gray max-w-2xl mx-auto">Selecciona una opción para continuar con tus tareas legales</p>
        </div>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {canViewSection("lawyer") && (
            <div className="bg-pure-white rounded-xl shadow-sm border border-medium-gray overflow-hidden">
              <div className="bg-gradient-to-r from-petroleum-blue to-petroleum-blue/90 p-6">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-pure-white/20 rounded-lg">
                    <IconGavel size={24} className="text-pure-white" />
                  </div>
                  <h2 className="text-h2 font-semibold text-pure-white">Abogado</h2>
                </div>
              </div>
              <div className="p-6 space-y-4">
                <button 
                  onClick={handleDemandGenerator}
                  className="w-full flex items-center gap-3 p-4 bg-teal-green text-pure-white rounded-lg hover:bg-teal-green/90 transition-all duration-200 text-left group"
                >
                  <IconFileText size={20} className="group-hover:scale-110 transition-transform duration-200" />
                  <div>
                    <div className="font-medium text-button">Gestionar Demanda</div>
                    <div className="text-small opacity-90">Generar y gestionar textos de demanda</div>
                  </div>
                </button>

                <button 
                  onClick={handleDemandManagement}
                  className="w-full flex items-center gap-3 p-4 bg-petroleum-blue text-pure-white rounded-lg hover:bg-petroleum-blue/90 transition-all duration-200 text-left group"
                >
                  <IconScale size={20} className="group-hover:scale-110 transition-transform duration-200" />
                  <div>
                    <div className="font-medium text-button">Gestionar Juicios</div>
                    <div className="text-small opacity-90">Administrar casos y juicios activos</div>
                  </div>
                </button>

                <button 
                  onClick={handleDemandStatus}
                  className="w-full flex items-center gap-3 p-4 bg-petroleum-blue text-pure-white rounded-lg hover:bg-petroleum-blue/90 transition-all duration-200 text-left group"
                >
                  <IconChartBar size={20} className="group-hover:scale-110 transition-transform duration-200" />
                  <div>
                    <div className="font-medium text-button">Estado de avance</div>
                    <div className="text-small opacity-90">Seguimiento del progreso de casos</div>
                  </div>
                </button>
              </div>
            </div>
          )}

          {canViewSection("supervisor") && (
            <div className="bg-pure-white rounded-xl shadow-sm border border-medium-gray overflow-hidden">
              <div className="bg-gradient-to-r from-teal-green to-teal-green/90 p-6">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-pure-white/20 rounded-lg">
                    <IconUsers size={24} className="text-pure-white" />
                  </div>
                  <h2 className="text-h2 font-semibold text-pure-white">Supervisor</h2>
                </div>
              </div>
              <div className="p-6 space-y-4">
                <button 
                  onClick={handleStatistics}
                  className="w-full flex items-center gap-3 p-4 bg-teal-green text-pure-white rounded-lg hover:bg-teal-green/90 transition-all duration-200 text-left group"
                >
                  <IconChartBar size={20} className="group-hover:scale-110 transition-transform duration-200" />
                  <div>
                    <div className="font-medium text-button">Estadísticas de Juicios</div>
                    <div className="text-small opacity-90">Análisis y reportes de casos</div>
                  </div>
                </button>

                <button 
                  onClick={handleDemandStatus}
                  className="w-full flex items-center gap-3 p-4 bg-petroleum-blue text-pure-white rounded-lg hover:bg-petroleum-blue/90 transition-all duration-200 text-left group"
                >
                  <IconChartBar size={20} className="group-hover:scale-110 transition-transform duration-200" />
                  <div>
                    <div className="font-medium text-button">Estado de Avance</div>
                    <div className="text-small opacity-90">Supervisión del progreso general</div>
                  </div>
                </button>
              </div>
            </div>
          )}

          {canViewSection("bank") && (
            <div className="bg-pure-white rounded-xl shadow-sm border border-medium-gray overflow-hidden">
              <div className="bg-gradient-to-r from-soft-gold to-soft-gold/90 p-6">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-pure-white/20 rounded-lg">
                    <IconBuildingBank size={24} className="text-pure-white" />
                  </div>
                  <h2 className="text-h2 font-semibold text-pure-white">Banco</h2>
                </div>
              </div>
              <div className="p-6 space-y-4">
                <button 
                  className="w-full flex items-center gap-3 p-4 bg-teal-green text-pure-white rounded-lg hover:bg-teal-green/90 transition-all duration-200 text-left group"
                >
                  <IconBuildingBank size={20} className="group-hover:scale-110 transition-transform duration-200" />
                  <div>
                    <div className="font-medium text-button">Comercial</div>
                    <div className="text-small opacity-90">Gestión de operaciones comerciales</div>
                  </div>
                </button>

                <button 
                  className="w-full flex items-center gap-3 p-4 bg-petroleum-blue text-pure-white rounded-lg hover:bg-petroleum-blue/90 transition-all duration-200 text-left group"
                >
                  <IconChartBar size={20} className="group-hover:scale-110 transition-transform duration-200" />
                  <div>
                    <div className="font-medium text-button">Operaciones</div>
                    <div className="text-small opacity-90">Control de operaciones bancarias</div>
                  </div>
                </button>
              </div>
            </div>
          )}

          {canViewSection("admin") && (
            <div className="bg-pure-white rounded-xl shadow-sm border border-medium-gray overflow-hidden">
              <div className="bg-gradient-to-r from-charcoal-gray to-charcoal-gray/90 p-6">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-pure-white/20 rounded-lg">
                    <IconUsers size={24} className="text-pure-white" />
                  </div>
                  <h2 className="text-h2 font-semibold text-pure-white">Administración</h2>
                </div>
              </div>
              <div className="p-6 space-y-4">
                <button 
                  onClick={handleCreateUser}
                  className="w-full flex items-center gap-3 p-4 bg-teal-green text-pure-white rounded-lg hover:bg-teal-green/90 transition-all duration-200 text-left group"
                >
                  <IconUserPlus size={20} className="group-hover:scale-110 transition-transform duration-200" />
                  <div>
                    <div className="font-medium text-button">Crear Usuario</div>
                    <div className="text-small opacity-90">Registrar nuevos usuarios en el sistema</div>
                  </div>
                </button>

                <button 
                  onClick={handleListUsers}
                  className="w-full flex items-center gap-3 p-4 bg-petroleum-blue text-pure-white rounded-lg hover:bg-petroleum-blue/90 transition-all duration-200 text-left group"
                >
                  <IconList size={20} className="group-hover:scale-110 transition-transform duration-200" />
                  <div>
                    <div className="font-medium text-button">Listar Usuarios</div>
                    <div className="text-small opacity-90">Gestionar usuarios existentes</div>
                  </div>
                </button>
              </div>
            </div>
          )}

          {!group && !isLoading && (
            <div className="lg:col-span-2 bg-pure-white rounded-xl shadow-sm border border-medium-gray p-8">
              <div className="text-center">
                <div className="w-16 h-16 bg-medium-gray rounded-full flex items-center justify-center mx-auto mb-4">
                  <IconUsers size={32} className="text-charcoal-gray" />
                </div>
                <h3 className="text-h3 font-semibold text-petroleum-blue mb-2">Sin permisos asignados</h3>
                <p className="text-body text-charcoal-gray">Contacta al administrador para obtener acceso a las funcionalidades del sistema.</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default PrincipalMenu;