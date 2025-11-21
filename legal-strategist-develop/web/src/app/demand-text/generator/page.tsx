"use client";

import { useCallback, useRef, useState } from "react";
import { toast, ToastContainer } from "react-toastify";
import { Tab, Tabs, TabList, TabPanel } from "react-tabs";
import { debounce, isEqual } from "lodash";
import { PDFViewer, pdf } from "@react-pdf/renderer";
import { DemandTextAnalyzer } from "@/components/analyzer";
import { DemandTextInputExtractor, DemandTextInputExtractorInputs } from "@/components/extractor";
import { DemandTextGenerator } from "@/components/generator";
import { FileItem } from "@/components/input";
import { DemandTextSender } from "@/components/sender";
import { FullPageOverlay } from "@/components/loading";
import { PDFDemandText } from "@/components/pdf";
import { Spinner } from "@/components/state";
import {
  DemandTextSenderRequest,
  analyzeDemandTextFromStructure,
  extractDemandTextInput,
  generateDemandTextFromStructure,
  sendDemandText,
} from "@/services/demand-text";
import { DemandTextAnalysis, DemandTextInputInformation, DemandTextStructure } from "@/types/demand-text";
import { FileWithContext } from "@/types/file";
import { Output } from "@/types/output";
import { formatRut } from "@/utils/rut";

const TAB_CLASSNAME = "-mb-[1px] font-semibold py-1 text-sm md:text-base select-none cursor-pointer hover:text-gray-900";
const TAB_CLASSNAME_DISABLED = "-mb-[1px] font-semibold py-1 text-sm md:text-base select-none";

export default function DemandTextGeneratorPage() {
  const [activeTab, setActiveTab] = useState(0);
  const [demandTextAnalyzerResponse, setDemandTextAnalyzerResponse] = useState<DemandTextAnalysis | null>(null);
  const [demandTextGeneratorResponse, setDemandTextGeneratorResponse] = useState<DemandTextStructure | null>(null);
  const [demandTextInputExtractorResponse, setDemandTextInputExtractorResponse] = useState<DemandTextInputInformation | null>(null);
  const [dollarCertificate, setDollarCertificate] = useState<File | undefined>(undefined);
  const [loading, setLoading] = useState<boolean>(false);
  const [loadingAnalysis, setLoadingAnalysis] = useState<boolean>(false);
  const [lockedGenerationFiles, setLockedGenerationFiles] = useState<FileWithContext[]>([]);
  const [toastMessage, setToastMessage] = useState<string>("");
  const demandTextPDF = useRef<Blob | null>(null);

  const onAnalyzerSubmit = async (data: DemandTextStructure | null) => {
    if (loadingAnalysis || loading) {
      return;
    }

    const information = data ? data : demandTextGeneratorResponse;
    if (information === null) {
      toast.warning("Falta información necesaria para analizar el texto de demanda.");
    }

    setLoadingAnalysis(true);

    try {
      setToastMessage("Analizando texto de demanda...");
      const res = await analyzeDemandTextFromStructure(information!);
      setDemandTextAnalyzerResponse(res.structured_output);
      toast.success("Análisis exitoso.");
    } catch (e) {
      toast.error(`${e}`, { autoClose: 10000 });
    } finally {
      setToastMessage("");
      setLoadingAnalysis(false);
    }
  };

  const onExtractorSubmit = async (data: DemandTextInputExtractorInputs) => {
    if (loading) {
      return;
    }

    const reasonsPerDocument = Array.from(data.files.map(({ context }) => context.trim() || ""));
    const additionalData: Record<string, string[] | Record<string, string>[]> = {};
    let contentToSend = `${data.bankContent}\n${data.reasonContent}`;

    if (reasonsPerDocument) {
      additionalData["reasons_per_document"] = reasonsPerDocument;
    }

    if (data.requests) {
      additionalData["secondary_requests"] = data.requests.map(({ value, text }) => { return { nature: value, context: text } });
    }

    contentToSend += JSON.stringify(additionalData);

    setLoading(true);

    let res: Output<DemandTextInputInformation> | null = null;

    try {
      if (data.dollarCertificate) {
        setDollarCertificate(data.dollarCertificate);
      }
      setToastMessage("Extrayendo información...");
      res = await extractDemandTextInput(contentToSend, data.files);
      setDemandTextInputExtractorResponse(res.structured_output);
      setLockedGenerationFiles(data.files);
      toast.success("Extracción exitosa.");
      setActiveTab(3);
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
    debounce((formData: DemandTextInputInformation) => {
      if (!isEqual(formData, demandTextInputExtractorResponse)) {
        setDemandTextInputExtractorResponse(formData);
      }
    }, 300),
    []
  );

  const onGeneratorSubmit = async (data: DemandTextInputInformation | null) => {
    if (loading) {
      return;
    }

    const information = data ? data : demandTextInputExtractorResponse;
    if (information === null) {
      toast.warning("Falta información necesaria para generar el texto de demanda.");
    }

    if (data) {
      setDemandTextInputExtractorResponse(data);
    }

    setLoading(true);

    let res: Output<DemandTextStructure> | null = null;

    try {
      setToastMessage("Generando texto de demanda...");
      res = await generateDemandTextFromStructure(information!);
      setDemandTextGeneratorResponse(res.structured_output);
      if (res.structured_output) {
        const pdfInstance = pdf(<PDFDemandText {...res.structured_output}/>);
        const blob = await pdfInstance.toBlob();
        demandTextPDF.current = blob;
      } else {
        console.warn("Could not bind generated PDF file");
      }
      toast.success("Generación exitosa.");
      setActiveTab(1);
    } catch (e) {
      toast.error(`${e}`, { autoClose: 10000 });
    } finally {
      setToastMessage("");
      setLoading(false);
    }

    if (res?.structured_output) {
      onAnalyzerSubmit(res.structured_output);
    }
  };

  const onSendSubmit = async (data: { contract: FileList | null, mandate: FileList | null, password: string, rut: string }, files: FileItem[]): Promise<boolean> => {
    if (!demandTextPDF?.current) {
      toast.error("Debe adjuntar un texto de demanda.");
      return false;
    }
    if (lockedGenerationFiles.length > 10) {
      toast.error("No se permite adjuntar más de 10 archivos de deuda.");
      return false;
    }
    if (lockedGenerationFiles.length < 1) {
      toast.error("Debe adjuntar al menos un archivo de deuda.");
      return false;
    }
    if (demandTextGeneratorResponse === null) {
      toast.error("Debe volver a generar el texto de demanda.");
      return false;
    }
    if (demandTextInputExtractorResponse === null) {
      toast.error("Debe volver a extraer información.");
      return false;
    }
    if (!demandTextInputExtractorResponse.plaintiff) {
      toast.error("Debe indicar un demandante.");
      return false;
    }
    if ((demandTextInputExtractorResponse.sponsoring_attorneys || []).length === 0) {
      toast.error("Debe indicar al menos un abogado por los demandantes.");
      return false;
    }
    if ((demandTextInputExtractorResponse.defendants || []).length === 0) {
      toast.error("Debe indicar al menos un demandado.");
      return false;
    }

    const extraFiles = files.map((fileItem) => fileItem.file);
    const extraFilesLabels = files.map((fileItem) => fileItem.name);

    setLoading(true);
    let valid = false;

    const senderRequestBody: DemandTextSenderRequest = {
      demandTextPDF: demandTextPDF.current,
      contract: data.contract,
      mandate: data.mandate!,
      password: data.password,
      rut: formatRut(data.rut),
      structure: demandTextGeneratorResponse,
      information: demandTextInputExtractorResponse,
      extraFiles: extraFiles,
      extraFilesLabels: extraFilesLabels,
      dollarCertificate: dollarCertificate,
    }

    let promissoryNoteCount = 0;
    let billCount = 0;
    let bondCount = 0;

    lockedGenerationFiles.forEach((fileWithContext) => {
      senderRequestBody.extraFiles.push(fileWithContext.file);
      
      if (fileWithContext.fileType === "promissory_note") {
        senderRequestBody.extraFilesLabels.push(`Pagaré ${++promissoryNoteCount}`);
      } else if (fileWithContext.fileType === "bill") {
        senderRequestBody.extraFilesLabels.push(`Factura ${++billCount}`);
      } else if (fileWithContext.fileType === "bond") {
        senderRequestBody.extraFilesLabels.push(`Fianza ${++bondCount}`);
      }
    });

    setLoading(true);

    try {
      setToastMessage("Enviando texto de demanda...");
      const res = await sendDemandText(senderRequestBody);
      if (res?.status === 200) { 
        valid = true;     
        toast.success("Envío exitoso, puede revisar en \"Estado de avance\".");
      } else {
        toast.warning(`${res?.message}`, { autoClose: 10000 });
      }
    } catch (e) {
      toast.error(`${e}`, { autoClose: 10000 });
    } finally {
      setToastMessage("");
      setLoading(false);
    }
    return valid;
  };

  return (
    <div className="flex flex-col md:my-4 flex-1 w-full">
      <div className="bg-white md:rounded-xl flex flex-col flex-1 w-full p-8 md:shadow-lg">
        <h1 className="text-lg md:text-xl font-semibold mb-2 md:mb-4">Texto de demanda</h1>
        <Tabs 
          className="flex flex-col flex-1"
          selectedTabClassName="text-gray-900 border-b-2 border-blue-600 outline-none"
          selectedTabPanelClassName="h-full"
          selectedIndex={activeTab}
          onSelect={index => setActiveTab(index)}
        >
          <TabList className="flex gap-x-4 mb-4 border-b border-gray-200 text-gray-600">
            <Tab className={TAB_CLASSNAME}>Generar</Tab>
            <Tab
              className={!demandTextGeneratorResponse ? TAB_CLASSNAME_DISABLED : TAB_CLASSNAME}
              disabled={!demandTextGeneratorResponse}
            >
              Resultado
            </Tab>
            <Tab
              className={!demandTextGeneratorResponse ? TAB_CLASSNAME_DISABLED : TAB_CLASSNAME}
              disabled={!demandTextGeneratorResponse}
            >
              Análisis
            </Tab>
            <Tab
              className={!demandTextGeneratorResponse ? TAB_CLASSNAME_DISABLED : TAB_CLASSNAME}
              disabled={!demandTextGeneratorResponse}
            >
              Ajustar
            </Tab>
            <Tab 
              className={!demandTextGeneratorResponse ? TAB_CLASSNAME_DISABLED : TAB_CLASSNAME}
              disabled={!demandTextGeneratorResponse}
            >
              Enviar
            </Tab>
          </TabList>
          <TabPanel forceRender>
            <DemandTextInputExtractor
              className={activeTab === 0 ? "" : "hidden"}
              loading={loading}
              onExtractorSubmit={onExtractorSubmit}
            />
          </TabPanel>
          <TabPanel>
            <div className="flex-1 flex flex-col bg-zinc-700 h-full w-full relative">
              {loading && <Spinner className="flex-1 w-full h-full"/>}
              {!loading && demandTextGeneratorResponse && (
                <PDFViewer className="h-full">
                  <PDFDemandText {...demandTextGeneratorResponse}/>
                </PDFViewer>
              )}
            </div>
          </TabPanel>
          <TabPanel>
            { demandTextGeneratorResponse && demandTextAnalyzerResponse ? (
              <DemandTextAnalyzer className="flex-1 h-full" input={demandTextGeneratorResponse} analysis={demandTextAnalyzerResponse}/>
            ) : (
              <>
                {loadingAnalysis || loading ? <Spinner className="flex-1 w-full h-full"/> : (
                  <div className="flex-1 text-gray-600 flex h-full justify-center text-sm md:text-base items-center text-center p-8">
                    {demandTextGeneratorResponse 
                      ? "No fue posible analizar el texto de demanda generado."
                      : "Genere un texto de demanda para obtener un análisis detallado."
                    }
                  </div>
                )}
              </>
            )}
          </TabPanel>
          <TabPanel forceRender>
            <DemandTextGenerator
              className={activeTab === 3 ? "" : "hidden"}
              loading={loading}
              information={demandTextInputExtractorResponse ?? undefined}
              onGeneratorSubmit={onGeneratorSubmit}
              onChange={onGeneratorInputChange}
            />
          </TabPanel>
          <TabPanel forceRender>
            <DemandTextSender
              className={activeTab === 4 ? "" : "hidden"}
              filled={demandTextGeneratorResponse !== null}
              loading={loading}
              onSenderSubmit={onSendSubmit}
            />
          </TabPanel>
        </Tabs>
        <ToastContainer toastStyle={{ zIndex: 9999 }}/>
        <FullPageOverlay isVisible={loading} toastMessage={toastMessage} />
      </div>
    </div>
  );
}
