import { toast } from "react-toastify";

export function handleError(response: Response): never {
    if (response.status === 401) {
      throw new Error("Error de credenciales. Por favor, inicia sesión.");
    }
    if (response.status === 404) {
      throw new Error("Caso no encontrado. Por favor, verifica el ID.");
    }
    if (response.status === 500) {
      throw new Error("Error interno del servidor. Intenta nuevamente más tarde.");
    }
    throw new Error(`Error inesperado: ${response.statusText}`);
  }
  
  export function handleErrorStatus(status: number) {
    switch (status) {
      case 400:
        toast.error("Solicitud inválida. Verifique los datos enviados.");
        break;
      case 401:
        toast.error("No autorizado. Inicie sesión nuevamente.");
        break;
      case 402:
        toast.error("Error de pago. Contacte al soporte.");
        break;
      case 404:
        toast.error("Recurso no encontrado.");
        break;
      case 500:
        toast.error("Error interno del servidor. Intente más tarde.");
        break;
      default:
        toast.error(`Error inesperado (${status}).`);
        break;
    }
  }
