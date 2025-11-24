"use client";

import { Suspense } from "react";
import CaseList from "@/components/case/list";
import { Spinner } from "@/components/state";
import { fetchCases } from "@/services/case";

export default function SupervisorBankCases({ params }: { params: { bank?: string } }) {
  const title = "Estado de avance";
  const subtitle = "Revisa el estado de avance de tus casos y accede a los detalles de cada caso.";
  return (
    <Suspense fallback={
      <div className="p-6 flex flex-col flex-1">
        <h1 className="text-xl md:text-2xl font-bold mb-6">Estado de avance</h1>
        <Spinner className="flex-1"/>
      </div>
    }>
      <CaseList title={title} subtitle={subtitle} linkedCases onFetch={fetchCases} params={params} />
    </Suspense>
  );
};
