export const formatDate = (isoDate: string) => {
  const date = new Date(isoDate);
  if (isNaN(date.getTime())) {
    return '---';
  };
  const day = date.getDate().toString().padStart(2, "0");
  const month = (date.getMonth() + 1).toString().padStart(2, "0");
  const year = date.getFullYear();
  return `${day}-${month}-${year}`;
};

/**
 * Formatea una fecha de procedimiento evitando problemas de zona horaria
 * @param procedureDate - Fecha en formato YYYY-MM-DD
 * @returns Fecha formateada en formato DD/MM/YYYY
 */
export const formatProcedureDate = (procedureDate: string) => {
  if (!procedureDate) return '-';
  
  // Agregar tiempo local para evitar problemas de zona horaria
  const date = new Date(procedureDate + 'T00:00:00');
  return date.toLocaleDateString('es-CL');
};
