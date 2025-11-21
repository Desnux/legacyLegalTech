import React, { useEffect } from "react";
import { toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import Spinner from "../spinner";

const FullPageOverlay: React.FC<{ isVisible: boolean; toastMessage?: string; loadingMessage?: string }> = ({
  isVisible,
  toastMessage = "Procesando información...",
  loadingMessage = "Procesando...",
}) => {
  useEffect(() => {
    const handleBeforeUnload = (event: BeforeUnloadEvent) => {
      event.preventDefault();
    };

    let toastId: string | number | undefined;

    if (isVisible) {
      window.addEventListener("beforeunload", handleBeforeUnload); // Registra el evento
      toastId = toast.info(toastMessage, { autoClose: false }); // El toast permanece visible
    } else {
      window.removeEventListener("beforeunload", handleBeforeUnload); // Elimina el evento
      if (toastId) {
        toast.dismiss(toastId); // Cierra el toast si el overlay se oculta
      }
    }

    return () => {
      window.removeEventListener("beforeunload", handleBeforeUnload); // Limpieza al desmontar el componente
      if (toastId) {
        toast.dismiss(toastId); // Asegura que el toast se cierre al desmontar
      }
    };
  }, [isVisible, toastMessage]); // Se ejecuta cada vez que `isVisible` o `toastMessage` cambian

  if (!isVisible) {
    return null; // No renderiza nada si no está visible
  }

  return (
    <div
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        width: "100%",
        height: "100%",
        backgroundColor: "rgba(0, 0, 0, 0.8)", // Fondo semitransparente
        zIndex: 9997, // Asegura que esté por encima de otros elementos
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        backdropFilter: "blur(2px)",
        WebkitBackdropFilter: "blur(2px)"
      }}
    >
      <Spinner /> {/* Spinner de carga */}
      <div className="text-white text-lg md:text-xl text-center mt-24">
        {loadingMessage} {/* Texto de carga */}
      </div>
    </div>
  );
};

export default FullPageOverlay;
