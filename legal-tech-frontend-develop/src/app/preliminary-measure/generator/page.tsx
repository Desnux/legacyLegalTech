"use client";

import { useCallback, useState } from "react";
import dynamic from "next/dynamic";
import { toast, ToastContainer } from "react-toastify";
import { Tab, Tabs, TabList, TabPanel } from "react-tabs";
import { debounce, isEqual } from "lodash";
import { PreliminaryMeasureInputExtractor, PreliminaryMeasureInputExtractorInputs } from "@/components/extractor";
import { PreliminaryMeasureGenerator } from "@/components/generator";
import { Message } from "@/components/information";
import { FullPageOverlay } from "@/components/loading";
import { Spinner } from "@/components/state";
import {
  extractPreliminaryMeasureInput,
  generatePreliminaryMeasureFromStructure,
} from "@/services/preliminary-measure";
import { PreliminaryMeasureInputInformation } from "@/types/preliminary-measure";
import { Output } from "@/types/output";

const TAB_CLASSNAME = "-mb-[1px] font-semibold py-1 text-sm md:text-base select-none cursor-pointer hover:text-gray-900";
const TAB_CLASSNAME_DISABLED = "-mb-[1px] font-semibold py-1 text-sm md:text-base select-none";

const PDFBlobViewer = dynamic(() => import("@/components/pdf/pdf-blob-viewer"), {
  ssr: false,
});

export default function PreliminaryMeasureGeneratorPage() {
  const [activeTab, setActiveTab] = useState(0);
  const [preliminaryMeasureGeneratorResponse, setPreliminaryMeasureGeneratorResponse] = useState<Blob | null>(null);
  const [preliminaryMeasureInputExtractorResponse, setPreliminaryMeasureInputExtractorResponse] = useState<PreliminaryMeasureInputInformation | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [toastMessage, setToastMessage] = useState<string>("");

  const onExtractorSubmit = async (data: PreliminaryMeasureInputExtractorInputs) => {
    if (loading) {
      return;
    }

    if (data.file === null) {
      toast.error("Debe adjuntar un reporte COOPEUCH.");
      return;
    }

    setLoading(true);
    let res: Output<PreliminaryMeasureInputInformation> | null = null;
    try {
      setToastMessage("Extrayendo información...");
      res = await extractPreliminaryMeasureInput(
        data.local_police_number,
        data.communication_date,
        data.file,
        data.coopeuch_registry_image,
        data.transaction_to_self_image,
        data.payment_to_account_image,
        data.user_report_image,
        data.safesigner_report_image,
        data.mastercard_connect_report_image,
        data.celmedia_report_image,
      );
      setPreliminaryMeasureInputExtractorResponse(res.structured_output);
      toast.success("Extracción exitosa.");
      setActiveTab(1);
    } catch (e) {
      toast.error(`${e}`, { autoClose: 10000 });
    } finally {
      setToastMessage("");
      setLoading(false);
    }
    if (res?.structured_output) {
      await onGeneratorSubmit(res.structured_output);
    }
  };

  const onGeneratorInputChange = useCallback(
    debounce((formData: PreliminaryMeasureInputInformation) => {
      if (!isEqual(formData, preliminaryMeasureInputExtractorResponse)) {
        setPreliminaryMeasureInputExtractorResponse(formData);
      }
    }, 300),
    []
  );

  const onGeneratorSubmit = async (data: PreliminaryMeasureInputInformation | null) => {
    if (loading) {
      return;
    }

    const information = data ? data : preliminaryMeasureInputExtractorResponse;
    if (information === null) {
      toast.warning("Falta información necesaria para generar la medida prejudicial.");
    }

    if (data) {
      setPreliminaryMeasureInputExtractorResponse(data);
    }

    setLoading(true);
    let res: Blob | null = null;
    try {
      setToastMessage("Generando medida prejudicial...");
      res = await generatePreliminaryMeasureFromStructure(information!);
      setPreliminaryMeasureGeneratorResponse(res);
      toast.success("Generación exitosa.");
      setActiveTab(2);
    } catch (e) {
      toast.error(`${e}`, { autoClose: 10000 });
    } finally {
      setToastMessage("");
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col md:my-4 flex-1 w-full">
      <div className="bg-white md:rounded-xl flex flex-col flex-1 w-full p-8 md:shadow-lg">
        <h1 className="text-lg md:text-xl font-semibold mb-2 md:mb-4">Medida prejudicial</h1>
        <Tabs 
          className="flex flex-col flex-1"
          selectedTabClassName="text-gray-900 border-b-2 border-blue-600 outline-none"
          selectedTabPanelClassName="flex-1 flex flex-col"
          selectedIndex={activeTab}
          onSelect={index => setActiveTab(index)}
        >
          <TabList className="flex gap-x-4 mb-4 border-b border-gray-200 text-gray-600">
            <Tab className={TAB_CLASSNAME}>Generar</Tab>
            <Tab
              className={!preliminaryMeasureGeneratorResponse ? TAB_CLASSNAME_DISABLED : TAB_CLASSNAME}
              disabled={!preliminaryMeasureGeneratorResponse}
            >
              Ajustar
            </Tab>
            <Tab
              className={!preliminaryMeasureGeneratorResponse ? TAB_CLASSNAME_DISABLED : TAB_CLASSNAME}
              disabled={!preliminaryMeasureGeneratorResponse}
            >
              Resultado
            </Tab>
          </TabList>
          <TabPanel forceRender>
            <PreliminaryMeasureInputExtractor
              className={activeTab === 0 ? "h-full flex flex-col" : "hidden"}
              loading={loading}
              onExtractorSubmit={onExtractorSubmit}
            />
          </TabPanel>
          <TabPanel forceRender>
            <PreliminaryMeasureGenerator
              className={activeTab === 1 ? "" : "hidden"}
              loading={loading}
              information={preliminaryMeasureInputExtractorResponse ?? undefined}
              onGeneratorSubmit={onGeneratorSubmit}
              onChange={onGeneratorInputChange}
            />
          </TabPanel>
          <TabPanel>
            <Message
              type="warning"
              message="Generación bajo evaluación: Se recomienda revisar el archivo generado."
              className="mb-6"
            />
            <div className="flex-1 flex flex-col w-full relative border bg-[#eeeeee] border-zinc-500">
              {loading && <Spinner className="flex-1 w-full h-full"/>}
              {!loading && preliminaryMeasureGeneratorResponse && (
                <PDFBlobViewer
                  blob={preliminaryMeasureGeneratorResponse}
                  className="flex-1 max-h-[calc(100vh-366px)]"
                  filename="Medida Prejudicial"
                />
              )}
            </div>
          </TabPanel>
        </Tabs>
        <ToastContainer toastStyle={{ zIndex: 9999 }}/>
        <FullPageOverlay isVisible={loading} toastMessage={toastMessage} />
      </div>
    </div>
  );
}
