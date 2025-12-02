export const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat("es-CL", {
        style: "currency",
        currency: "CLP",
        minimumFractionDigits: 0,
        maximumFractionDigits: 0,
    }).format(amount);
}


export const formatInputCurrency = (value: string): string => {
    // Remover todo excepto números
    const numbersOnly = value.replace(/\D/g, '');
    if (!numbersOnly) return '';
    
    // Formatear con separadores de miles
    return numbersOnly.replace(/\B(?=(\d{3})+(?!\d))/g, '.');
  };