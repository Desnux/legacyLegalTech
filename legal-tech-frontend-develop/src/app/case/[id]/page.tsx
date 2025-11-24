"use client";

import React from "react";
import { useParams } from "next/navigation";
import CaseDetails from "@/components/case/details";

const CasePage: React.FC = () => {
  const params = useParams(); // Obtener el parámetro dinámico de la URL
  const { id } = params as { id: string };

  return (
    <div className="bg-white md:bg-transparent flex-1 w-full">
      <h1 className="text-2xl md:text-3xl font-semibold md:pl-0.5 border-b mx-4 md:mx-0 md:border-none md:py-4 py-2 border-gray-200">
        Detalles del caso
      </h1>
      <CaseDetails caseId={id} /> {/* Se pasa el ID al componente */}
    </div>
  );
};

export default CasePage;
