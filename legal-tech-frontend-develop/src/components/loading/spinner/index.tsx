import React from "react";

const Spinner: React.FC = () => {
  return (
    <div
      style={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        position: "fixed", // Centrado absoluto en la página
        top: 0,
        left: 0,
        width: "100%",
        height: "100%",
        zIndex: 9998, // Aparece sobre FullPageOverlay
      }}
    >
      <div
        style={{
          width: "50px",
          height: "50px",
          border: "5px solid #f3f3f3", // Color del borde exterior
          borderTop: "5px solid #3498db", // Color del borde animado
          borderRadius: "50%",
          animation: "spin 1s linear infinite", // Animación de giro
        }}
      />
      <style>
        {`
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        `}
      </style>
    </div>
  );
};

export default Spinner;
