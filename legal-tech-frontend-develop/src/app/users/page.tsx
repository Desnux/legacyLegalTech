"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { toast } from "react-toastify";
import classNames from "classnames";
import { 
  IconPlus, 
  IconEdit, 
  IconTrash, 
  IconUser,
  IconUserCheck,
  IconUserX,
  IconShield,
  IconShieldCheck,
  IconShieldLock,
  IconShieldStar
} from "@tabler/icons-react";
import Button from "@/components/button";
import { Spinner } from "@/components/state";
import { sendGetUsersRequest, User } from "@/services/auth/get-users";
import { formatDate } from "@/utils/date";

const ROLE_ICONS = {
  guest: IconUser,
  user: IconUserCheck,
  admin: IconShieldCheck,
  supervisor: IconShieldStar,
};

const ROLE_LABELS = {
  guest: "Invitado",
  user: "Usuario",
  admin: "Administrador",
  supervisor: "Supervisor",
  developer: "Desarrollador",
  tester: "Tester",
  client: "Cliente",
  bot: "Bot",
  lawyer: "Abogado",
  entity: "Banco",
};

const ROLE_COLORS = {
  guest: "bg-light-gray text-charcoal-gray",
  user: "bg-teal-green/10 text-teal-green",
  admin: "bg-petroleum-blue/10 text-petroleum-blue",
  supervisor: "bg-soft-gold/10 text-soft-gold",
  developer: "bg-teal-green/10 text-teal-green",
  tester: "bg-soft-gold/10 text-soft-gold",
  client: "bg-teal-green/10 text-teal-green",
  bot: "bg-medium-gray text-charcoal-gray",
  lawyer: "bg-petroleum-blue/10 text-petroleum-blue",
  entity: "bg-soft-gold/10 text-soft-gold",
};

export default function UsersPage() {
  const router = useRouter();
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      setError(null);
      const usersData = await sendGetUsersRequest();
      setUsers(usersData);
    } catch (error) {
      console.error("Error fetching users:", error);
      const errorMessage = error instanceof Error ? error.message : "Error al obtener usuarios";
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateUser = () => {
    router.push("/users/create");
  };

  const handleEditUser = (userId: string) => {
    console.log("Edit user:", userId);
    toast.info("Funcionalidad de edición en desarrollo");
  };

  const handleDeleteUser = (userId: string) => {
    console.log("Delete user:", userId);
    toast.info("Funcionalidad de eliminación en desarrollo");
  };

  const getRoleIcon = (role: string) => {
    const IconComponent = ROLE_ICONS[role as keyof typeof ROLE_ICONS] || IconUser;
    return <IconComponent size={16} />;
  };

  const getRoleColor = (role: string) => {
    return ROLE_COLORS[role as keyof typeof ROLE_COLORS] || ROLE_COLORS.guest;
  };

  const getRoleLabel = (role: string) => {
    return ROLE_LABELS[role as keyof typeof ROLE_LABELS] || role;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-light-gray py-8">
        <div className="max-w-7xl mx-auto px-4">
          <div className="bg-pure-white rounded-xl shadow-sm border border-medium-gray p-6">
            <div className="flex items-center justify-center h-64">
              <Spinner className="w-8 h-8" />
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-light-gray py-8">
        <div className="max-w-7xl mx-auto px-4">
          <div className="bg-pure-white rounded-xl shadow-sm border border-medium-gray p-6">
            <div className="text-center">
              <h2 className="text-h3 font-semibold text-red-600 mb-2">Error</h2>
              <p className="text-body text-charcoal-gray mb-4">{error}</p>
              <Button
                variant="danger"
                onClick={fetchUsers}
                className="px-4 py-2"
              >
                Reintentar
              </Button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-light-gray py-8">
      <div className="max-w-7xl mx-auto px-4">
        <div className="bg-pure-white rounded-xl shadow-sm border border-medium-gray">
          {/* Header */}
          <div className="px-6 py-4 border-b border-medium-gray">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-h2 font-serif text-petroleum-blue">
                  Gestión de Usuarios
                </h1>
                <p className="text-body text-charcoal-gray mt-1">
                  Administra los usuarios del sistema
                </p>
              </div>
              <button
                onClick={handleCreateUser}
                className="flex items-center gap-2 bg-teal-green hover:bg-teal-green/90 text-pure-white py-2 px-4 rounded-lg text-button font-medium transition-colors duration-200"
              >
                <IconPlus size={20} />
                Crear Usuario
              </button>
            </div>
          </div>

          {/* Content */}
          <div className="p-6">
            {users && users.length === 0 ? (
              <div className="text-center py-12">
                <IconUser size={48} className="mx-auto text-medium-gray mb-4" />
                <h3 className="text-h3 font-semibold text-petroleum-blue mb-2">
                  No hay usuarios
                </h3>
                <p className="text-body text-charcoal-gray mb-6">
                  Comienza creando el primer usuario del sistema.
                </p>
                <button
                  onClick={handleCreateUser}
                  className="flex items-center gap-2 bg-teal-green hover:bg-teal-green/90 text-pure-white py-2 px-4 rounded-lg text-button font-medium transition-colors duration-200 mx-auto"
                >
                  <IconPlus size={20} />
                  Crear Primer Usuario
                </button>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-medium-gray">
                  <thead className="bg-light-gray">
                    <tr>
                      <th className="px-6 py-3 text-left text-small font-medium text-petroleum-blue uppercase tracking-wider">
                        Usuario
                      </th>
                      <th className="px-6 py-3 text-left text-small font-medium text-petroleum-blue uppercase tracking-wider">
                        Rol
                      </th>
                      <th className="px-6 py-3 text-left text-small font-medium text-petroleum-blue uppercase tracking-wider">
                        Estado
                      </th>
                      <th className="px-6 py-3 text-left text-small font-medium text-petroleum-blue uppercase tracking-wider">
                        Firma Abogados
                      </th>
                      <th className="px-6 py-3 text-left text-small font-medium text-petroleum-blue uppercase tracking-wider">
                        Fecha de Creación
                      </th>
                      <th className="px-6 py-3 text-right text-small font-medium text-petroleum-blue uppercase tracking-wider">
                        Acciones
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-pure-white divide-y divide-medium-gray">
                    {users && users.map((user) => (
                      <tr key={user.id} className="hover:bg-light-gray transition-colors duration-200">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center">
                            <div className="flex-shrink-0 h-10 w-10">
                              <div className="h-10 w-10 rounded-full bg-teal-green/10 flex items-center justify-center">
                                <IconUser size={20} className="text-teal-green" />
                              </div>
                            </div>
                            <div className="ml-4">
                              <div className="text-body-sm font-medium text-charcoal-gray">
                                {user.name}
                              </div>
                              <div className="text-small text-medium-gray">
                                ID: {user.id}
                              </div>
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center">
                            <span className={classNames(
                              "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium",
                              getRoleColor(user.role)
                            )}>
                              {getRoleIcon(user.role)}
                              <span className="ml-1">{getRoleLabel(user.role)}</span>
                            </span>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center">
                            {user.active ? (
                              <IconUserCheck size={16} className="text-teal-green mr-2" />
                            ) : (
                              <IconUserX size={16} className="text-red-500 mr-2" />
                            )}
                            <span className={classNames(
                              "text-body-sm font-medium",
                              user.active ? "text-teal-green" : "text-red-600"
                            )}>
                              {user.active ? "Activo" : "Inactivo"}
                            </span>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-body-sm text-black">
                          {user.law_firm ? user.law_firm.name : "No tiene firma"}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-body-sm text-black">
                          {formatDate(user.created_at)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-body-sm font-medium">
                          <div className="flex items-center justify-end space-x-2">
                            <button
                              onClick={() => handleEditUser(user.id)}
                              className="text-petroleum-blue hover:text-petroleum-blue/80 p-1 rounded hover:bg-petroleum-blue/10 transition-colors duration-200"
                              title="Editar usuario"
                            >
                              <IconEdit size={16} />
                            </button>
                            <button
                              onClick={() => handleDeleteUser(user.id)}
                              className="text-red-600 hover:text-red-500 p-1 rounded hover:bg-red-50 transition-colors duration-200"
                              title="Eliminar usuario"
                            >
                              <IconTrash size={16} />
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          {/* Footer */}
          {users && users.length > 0 ? (
            <div className="px-6 py-4 border-t border-medium-gray bg-light-gray">
              <div className="flex items-center justify-between text-body-sm text-charcoal-gray">
                <span>
                  Total de usuarios: {users.length}
                </span>
                <span>
                  Última actualización: {new Date().toLocaleString('es-CL')}
                </span>
              </div>
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
}
