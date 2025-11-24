
export interface UserFormData {
    name: string;
    password: string;
    confirmPassword: string;
    role: string;
    law_firm_id: string;
  }
  
  export const ROLE_OPTIONS = [
    { value: "admin", label: "Administrador" },
    { value: "supervisor", label: "Supervisor" },
    { value: "lawyer", label: "Abogado" },
    { value: "bank", label: "Banco" },
  ];
