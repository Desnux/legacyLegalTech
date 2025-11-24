"use client";

import CaseList from "@/components/case/list";
import { fetchCaseStats, fetchCaseStatsCSV } from "@/services/information";

export default function SupervisorBankCases({ params }: { params: { bank: string } }) {
  const { bank } = params;
  const title = "Casos históricos";
  const subtitle = "";

  const onDownload = async () => {
    const blob = await fetchCaseStatsCSV({ bank: bank });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "casos.zip";
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
  }

  return (
    <CaseList
      title={title}
      subtitle={subtitle}
      onDownload={onDownload} 
      onFetch={fetchCaseStats} 
      params={params}
    />
  );
}
