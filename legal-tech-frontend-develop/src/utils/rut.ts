export const removeSeparators = (rut: string | null): string => {
  if (!rut) {
    return "";
  }
  return rut.replace(/[^0-9kK]/g, "").replace(/[kK]{1,}$/, "K");
};

export const prettifyRut = (rut: string | null): string => {
  if (!rut) {
    return "";
  }
  const cleanRut = removeSeparators(rut);
  if (cleanRut.slice(0, -1).toUpperCase().includes("K")) {
    return "";
  }
  const dv = cleanRut.charAt(cleanRut.length - 1).toUpperCase();
  const rutWithoutDv = cleanRut.slice(0, -1).replace(/^0+/, "");
  const formattedRut = rutWithoutDv.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".");
  if (formattedRut === "") {
    return `${dv}`;
  }
  return `${formattedRut}-${dv}`;
};

export const formatRut = (rut: string | null, withoutDv: boolean = false): string => {
  if (!rut) {
    return "";
  }
  const cleanRut = removeSeparators(rut);
  if (cleanRut.slice(0, -1).toUpperCase().includes("K")) {
    return "";
  }
  const dv = cleanRut.charAt(cleanRut.length - 1).toUpperCase();
  const rutWithoutDv = cleanRut.slice(0, -1).replace(/^0+/, "");
  if (rutWithoutDv === "") {
    if (withoutDv) {
      return "";
    }
    return `0-${dv}`;
  }
  if (withoutDv) {
    return `${rutWithoutDv}`;
  }
  return `${rutWithoutDv}-${dv}`;
};

type RutDv = "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9" | "K";

export const calculateDv = (rut: number): RutDv => {
  const rutArr = Math.abs(rut).toString().split("");
  const digits = rutArr.map((digit) => parseInt(digit, 10)).reverse();
  const sum = digits.reduce((acc, digit, idx) => {
    const weightedDigit = digit * ((idx % 6) + 2);
    return acc + weightedDigit;
  }, 0);
  const modulo = 11 - (sum % 11);
  if (modulo === 11) {
    return "0";
  } else if (modulo === 10) {
    return "K";
  } else {
    return modulo.toString() as RutDv;
  }
};

export const checkRut = (rut: string | null): boolean => {
  if (!rut) {
    return false;
  }
  const cleanRut = removeSeparators(rut);
  if (cleanRut.length < 2) {
    return false;
  }
  const rutWithoutDv = parseInt(cleanRut.slice(0, -1));
  const dv = cleanRut.charAt(cleanRut.length - 1).toUpperCase();
  return calculateDv(rutWithoutDv) === dv;
};

export const removeSeparatorsForDemand = (rut: string | null): string => {
  if (!rut) {
    return "";
  }
  return rut.replace(/[^0-9]/g, "");
};

export const formatRutForDemand = (rut: string | null): string => {
  if (!rut) {
    return "";
  }
  const cleanRut = removeSeparatorsForDemand(rut);
  const rutFormatted = cleanRut.replace(/^0+/, "");
  return rutFormatted || "";
};

export const prettifyRutForDemand = (rut: string | null): string => {
  if (!rut) {
    return "";
  }
  const cleanRut = removeSeparatorsForDemand(rut);
  const rutFormatted = cleanRut.replace(/^0+/, "");
  return rutFormatted || "";
};

export const checkRutForDemand = (rut: string | null): boolean => {
  if (!rut) {
    return false;
  }
  const cleanRut = removeSeparatorsForDemand(rut);
  if (cleanRut.length < 1) {
    return false;
  }
  
  if (!/^[0-9]+$/.test(cleanRut)) {
    return false;
  }
  
  return true;
};
