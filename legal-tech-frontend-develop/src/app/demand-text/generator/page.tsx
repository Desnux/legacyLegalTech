"use client";

import { useCallback, useRef, useState } from "react";
import { ToastContainer, toast } from "react-toastify";
import { Tab, Tabs, TabList, TabPanel } from "react-tabs";
import { debounce, isEqual, cloneDeep } from "lodash";
import { PDFViewer, pdf } from "@react-pdf/renderer";
import { DemandTextAnalyzer } from "@/components/analyzer";
import { DemandTextInputExtractor, DemandTextInputExtractorInputs } from "@/components/extractor";
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
import { DemandTextAnalysis, DemandTextInputInformation, DemandTextStructure, ParticipantRole } from "@/types/demand-text";
import { FileWithContext } from "@/types/file";
import { Output } from "@/types/output";
import { formatRutForDemand } from "@/utils/rut";
import { MODAL_DEMAND_TEXT_REQUESTS_OPTIONS } from "@/components/modal/modal-demand-text-requests";
import { DemandTextChanges } from "@/components/analyzer/demand-text-changes";
import { IconFileText, IconEye, IconEdit, IconSend, IconArrowRight } from "@tabler/icons-react";
import Button from "@/components/button";
import { useRouter } from "next/navigation";
import { DEFAULT_PARTICIPANTS } from "@/utils/demand-text-input-data";

const TAB_CLASSNAME = "flex items-center space-x-2 px-4 py-3 text-body-sm font-medium text-charcoal-gray hover:text-teal-green hover:bg-light-gray rounded-lg transition-all duration-200 cursor-pointer select-none";
const TAB_CLASSNAME_DISABLED = "flex items-center space-x-2 px-4 py-3 text-body-sm font-medium text-medium-gray cursor-not-allowed select-none";

export default function DemandTextGeneratorPage() {
  const [activeTab, setActiveTab] = useState(0);
  const [demandTextAnalyzerResponse, setDemandTextAnalyzerResponse] = useState<DemandTextAnalysis | null>(null);
  const [demandTextGeneratorResponse, setDemandTextGeneratorResponse] = useState<DemandTextStructure | null>(null);
  const [demandTextInputExtractorResponse, setDemandTextInputExtractorResponse] = useState<DemandTextInputInformation | null>(null);
  const [modifiedContent, setModifiedContent] = useState<DemandTextStructure | null>(null);
  const [showModifiedValues, setShowModifiedValues] = useState<boolean>(false);
  const [dollarCertificate, setDollarCertificate] = useState<File | undefined>(undefined);
  const [loading, setLoading] = useState<boolean>(false);
  const [loadingAnalysis, setLoadingAnalysis] = useState<boolean>(false);
  const [loadingExtraction, setLoadingExtraction] = useState<boolean>(false);
  const [debug, setDebug] = useState<boolean>(false);
  const [lockedGenerationFiles, setLockedGenerationFiles] = useState<FileWithContext[]>([]);
  const [toastMessage, setToastMessage] = useState<string>("");
  const demandTextPDF = useRef<Blob | null>(null);
  const router = useRouter();


  const onAnalyzerSubmit = async (data: DemandTextStructure | null) => {
    if (loadingAnalysis || loading) {
      return;
    }

    const information = data ? data : demandTextGeneratorResponse;
    if (information === null) {
      return;
    }

    setLoadingAnalysis(true);

    try {
      setToastMessage("Analizando texto de demanda...");
      const res = await analyzeDemandTextFromStructure(information!);
      setDemandTextAnalyzerResponse(res.structured_output);
    } catch (e) {
      console.error("Error en análisis:", e);
    } finally {
      setToastMessage("");
      setLoadingAnalysis(false);
    }
  };

  const onContentChange = (updatedContent: DemandTextStructure) => {
    setModifiedContent(updatedContent);
    if (updatedContent) {
      const pdfInstance = pdf(<PDFDemandText {...updatedContent}/>);
      pdfInstance.toBlob().then(blob => {
        demandTextPDF.current = blob;
      }).catch(err => {
        console.warn("Could not update PDF file:", err);
      });
    }
  };

  const onReset = () => {
    if (demandTextGeneratorResponse) {
      setModifiedContent(demandTextGeneratorResponse);
      setShowModifiedValues(false);
      const pdfInstance = pdf(<PDFDemandText {...demandTextGeneratorResponse}/>);
      pdfInstance.toBlob().then(blob => {
        demandTextPDF.current = blob;
      }).catch(err => {
        console.warn("Could not update PDF file:", err);
      });
    }
  };

  const onExtractorPDFSubmit = async (data: DemandTextInputExtractorInputs) => {
    if (loadingExtraction) {
      return;
    }
    const ALLOWED_REQUEST_IDS = [1, 2, 3, 5, 6]; 
    const reasonsPerDocument = Array.from(data.files.map(({ context }) => ({
      reason: context.trim() || "",
      pending_amount: null,
      capital_amount: null,
      interest_amount: null,
      debt_amount: null
    })));
    const requests = MODAL_DEMAND_TEXT_REQUESTS_OPTIONS
    .filter(({ id }) => ALLOWED_REQUEST_IDS.includes(id))
    .map(({ label, value }) => ({
      nature: value,
      context: label
    }));
    const plaintiff = DEFAULT_PARTICIPANTS.find(p => p.role === ParticipantRole.PLAINTIFF);
    const legalRepresentatives = DEFAULT_PARTICIPANTS
      .filter(p => p.role === ParticipantRole.PLAINTIFF_LEGAL_REPRESENTATIVE)
      .map(({ name, dni, address }) => ({
        name,
        identifier: dni,
        address,
        occupation: "Abogado"
      }));
    const sponsoringAttorneys = DEFAULT_PARTICIPANTS
      .filter(p => p.role === ParticipantRole.SPONSORING_ATTORNEY)
      .map(({ name, dni, address }) => ({
        name,
        identifier: dni,
        address
      }));

    const participants = {
      plaintiff: plaintiff ? {
        name: plaintiff.name,
        identifier: plaintiff.dni,
        address: plaintiff.address
      } : null,
      legal_representatives: legalRepresentatives,
      sponsoring_attorneys: sponsoringAttorneys
    };
    let contentToSend = JSON.stringify({
        reasons_per_document: reasonsPerDocument,
        participants: participants,
        secondary_requests: requests,
    });
    setLoadingExtraction(true);
    try {
      const res = await extractDemandTextInput(contentToSend, data.files);
      setLockedGenerationFiles(data.files);
      if (res?.structured_output) {
        setDemandTextInputExtractorResponse(res.structured_output);
      }
    } catch (e) {
      console.error("Error en extracción:", e);
    } finally {
      setLoadingExtraction(false);
    }
  };

  const onExtractorSubmit = async (data: DemandTextInputExtractorInputs) => {
    if (loading) {
      return;
    }

    let sendData = demandTextInputExtractorResponse ? cloneDeep(demandTextInputExtractorResponse) : null;
    
    if (sendData?.documents?.length) {
      let totalAmount = 0;
      
      sendData.documents.forEach((doc, index) => {
        const amountValue = (data as any)[`amount_${index}`];
        const identifierValue = (data as any)[`identifier_${index}`];
        const interestRateValue = (data as any)[`interest_rate_${index}`];
        const creationDateValue = (data as any)[`creation_date_${index}`];
        
        if (amountValue !== undefined && amountValue !== null && amountValue !== '') {
          const parsedAmount = Number(amountValue);
          if (!isNaN(parsedAmount)) {
            doc.amount = parsedAmount;
            totalAmount += parsedAmount;
          }
        } else if (doc.amount && !isNaN(Number(doc.amount))) {
          totalAmount += Number(doc.amount);
        }
        
        if (identifierValue !== undefined && identifierValue !== null && identifierValue !== '') {
          doc.identifier = identifierValue;
        }
        if (interestRateValue !== undefined && interestRateValue !== null && interestRateValue !== '') {
          doc.interest_rate = interestRateValue;
        }
        if (creationDateValue !== undefined && creationDateValue !== null && creationDateValue !== '') {
          doc.creation_date = creationDateValue;
        }
      });
      
      if (sendData) {
        sendData.amount = totalAmount;
      }
    }

    if (sendData && data.requests && data.requests.length > 0) {
      sendData.secondary_requests = data.requests.map(request => ({
        context: request.text || "",
        nature: request.value,
      }));
    }

    const debtorParticipants = data.participants.filter(({ role }) => role === 'defendant' || role === 'guarantee');
    const legalRepParticipants = data.participants.filter(({ role }) => role === 'legal_representative');

    const defendants = debtorParticipants.map(debtor => ({
      name: debtor.name,
      identifier: debtor.dni,
      occupation: null,
      address: debtor.address,
      legal_representatives: debtor.role === 'guarantee' ? null : legalRepParticipants.map(legalRep => ({
        name: legalRep.name,
        identifier: legalRep.dni,
        occupation: "",
        address: legalRep.address
      })),
      type: debtor.role === 'defendant' ? 'debtor' : 'co_debtor',
      entity_type: debtor.entity_type || 'natural'
    }));

    if (sendData) {
      sendData.defendants = defendants;
      await onGeneratorSubmit(sendData);
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
      return;
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
        setModifiedContent(res.structured_output);
        const pdfInstance = pdf(<PDFDemandText {...res.structured_output}/>);
        const blob = await pdfInstance.toBlob();
        demandTextPDF.current = blob;
      } else {
        console.warn("Could not bind generated PDF file");
      }
      setActiveTab(1);
    } catch (e) {
      console.error("Error en generación:", e);
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
      console.error("No se encontró el archivo de demanda.");
      return false;
    }
    if (lockedGenerationFiles.length > 10) {
      console.error("Se han adjuntado más de 10 archivos.");
      return false;
    }
    if (lockedGenerationFiles.length < 1) {
      console.error("No se han adjuntado archivos.");
      return false;
    }
    if (demandTextGeneratorResponse === null) {
      console.error("No se encontró el texto de demanda generado.");
      return false;
    }
    if (demandTextInputExtractorResponse === null) {
      console.error("No se encontró la información extraída.");
      return false;
    }
    if (!demandTextInputExtractorResponse.plaintiff) {
      console.error("No se encontró el demandante.");
      return false;
    }
    if ((demandTextInputExtractorResponse.sponsoring_attorneys || []).length === 0) {
      console.error("No se encontraron abogados patrocinantes.");
      return false;
    }
    if ((demandTextInputExtractorResponse.defendants || []).length === 0) {
      console.error("No se encontraron demandados.");
      return false;
    }
    if (modifiedContent === null) {
      console.error("No se encontró el contenido modificado.");
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
      rut: formatRutForDemand(data.rut),
      structure: modifiedContent,
      information: demandTextInputExtractorResponse,
      extraFiles: extraFiles,
      extraFilesLabels: extraFilesLabels,
      dollarCertificate: dollarCertificate,
      debug: debug,
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
      } else {
        console.warn("Envío con advertencia:", res?.message);
      }

      const caseId = res?.case_id || res?.caseId;
      if (caseId) {
        router.push(`/case/${caseId}`);
      } else {
        router.push("/supervisor/status");
      }
    } catch (e: any) {
      // Manejar error 504 (Gateway Timeout)
      if (e?.status === 504) {
        const message = "La demanda se está procesando en segundo plano. Serás redirigido a la lista de casos.";
        console.log(message);
        toast.info(message);
        router.push("/supervisor/status");
      } else {
        console.error("Error en envío:", e);
      }
    } finally {
      setToastMessage("");
      setLoading(false);
    }
    return valid;
  };

  return (
    <div className="min-h-full bg-light-gray py-8 flex flex-col w-full">
      <div className="w-full px-2 flex-1 flex flex-col">
        {/* Header */}
        <div className="text-center mb-4">
          <div className="flex items-center justify-center mb-2">
            <div className="bg-gradient-to-r from-teal-green to-petroleum-blue rounded-full p-2 mr-3">
              <IconFileText size={24} className="text-pure-white" />
            </div>
          </div>
          <h1 className="text-h2 font-serif text-petroleum-blue mb-1">
            Generador de Texto de Demanda
          </h1>
          <p className="text-body-sm text-charcoal-gray max-w-4xl mx-auto">
            Crea, analiza y envía textos de demanda de manera eficiente y profesional
          </p>
        </div>

        {/* Contenido Principal */}
        <div className="bg-pure-white rounded-2xl shadow-lg border border-medium-gray overflow-hidden flex flex-col flex-1 w-full">
          {/* Tabs */}
          <Tabs 
            className="flex flex-col h-full"
            selectedTabClassName="text-teal-green bg-teal-green/10 border-b-2 border-teal-green"
            selectedTabPanelClassName="h-full flex-1"
            selectedIndex={activeTab}
            onSelect={index => setActiveTab(index)}
          >
            <TabList className="flex gap-x-1 p-6 border-b border-medium-gray bg-light-gray">
              <Tab className={TAB_CLASSNAME}>
                <IconFileText size={18} />
                <span>Generar</span>
              </Tab>
              <Tab
                className={!demandTextGeneratorResponse ? TAB_CLASSNAME_DISABLED : TAB_CLASSNAME}
                disabled={!demandTextGeneratorResponse}
              >
                <IconEye size={18} />
                <span>Resultado</span>
              </Tab>
              <Tab
                className={!demandTextGeneratorResponse ? TAB_CLASSNAME_DISABLED : TAB_CLASSNAME}
                disabled={!demandTextGeneratorResponse}
              >
                <IconEdit size={18} />
                <span>Análisis y Ajustes</span>
              </Tab>
              <Tab 
                className={!demandTextGeneratorResponse ? TAB_CLASSNAME_DISABLED : TAB_CLASSNAME}
                disabled={!demandTextGeneratorResponse}
              >
                <IconSend size={18} />
                <span>Enviar</span>
              </Tab>
            </TabList>

            {/* Paneles de Contenido */}
            <div className="p-4 flex-1 flex flex-col">
              <TabPanel forceRender>
                <DemandTextInputExtractor
                  className={activeTab === 0 ? "" : "hidden"}
                  loading={loading}
                  extractionLoading={loadingExtraction}
                  onExtractorPDFSubmit={onExtractorPDFSubmit}
                  onExtractorSubmit={onExtractorSubmit}
                  extractedPdfInformation={demandTextInputExtractorResponse ?? undefined}
                />
              </TabPanel>
              
              <TabPanel>
                <div className="flex flex-col h-full w-full pb-24">
                  <div className="flex-1 flex flex-col bg-charcoal-gray w-full relative rounded-xl overflow-hidden border border-medium-gray" style={{ minHeight: 'calc(100vh - 150px)' }}>
                    {loading && (
                      <div className="flex items-center justify-center h-full">
                        <Spinner className="w-8 h-8 text-teal-green"/>
                      </div>
                    )}
                    {!loading && modifiedContent && (
                      <PDFViewer className="h-full w-full" style={{ height: '100%', width: '100%' }}>
                        <PDFDemandText {...modifiedContent}/>
                      </PDFViewer>
                    )}
                  </div>
                  
                  {/* Botón para avanzar a la siguiente pestaña */}
                  <div className="fixed bottom-12 left-1/2 transform -translate-x-1/2 z-20">
                    <Button
                      variant="primary"
                      onClick={() => setActiveTab(2)}
                      className="flex items-center gap-2"
                    >
                      <span>Continuar a Análisis y Ajustes</span>
                      <IconArrowRight size={16} />
                    </Button>
                  </div>
                </div>
              </TabPanel>
              
              <TabPanel>
                { demandTextGeneratorResponse && demandTextAnalyzerResponse && modifiedContent ? (
                  <div className="flex flex-col h-full pb-24">
                    <div className="flex-1 flex flex-col space-y-6">
                      <DemandTextChanges
                        originalContent={demandTextGeneratorResponse}
                        modifiedContent={modifiedContent}
                        showModifiedValues={showModifiedValues}
                        onToggleComparison={() => setShowModifiedValues(!showModifiedValues)}
                        onReset={onReset}
                      />
                      <div className="flex-1 bg-light-gray rounded-xl p-4">
                        <DemandTextAnalyzer 
                          className="h-full" 
                          input={modifiedContent} 
                          analysis={demandTextAnalyzerResponse}
                          onContentChange={onContentChange}
                        />
                      </div>
                    </div>
                    
                    {/* Botón para avanzar a la siguiente pestaña */}
                    <div className="fixed bottom-12 left-1/2 transform -translate-x-1/2 z-20">
                      <Button
                        variant="primary"
                        onClick={() => setActiveTab(3)}
                        className="flex items-center gap-2"
                      >
                        <span>Continuar a Enviar</span>
                        <IconArrowRight size={16} />
                      </Button>
                    </div>
                  </div>
                ) : (
                  <>
                    {loadingAnalysis || loading ? (
                      <div className="flex items-center justify-center h-64">
                        <Spinner className="w-8 h-8 text-teal-green"/>
                      </div>
                    ) : (
                      <div className="flex-1 text-charcoal-gray flex h-64 justify-center text-body items-center text-center p-8 bg-light-gray rounded-xl">
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
                <DemandTextSender
                  className={activeTab === 3 ? "" : "hidden"}
                  filled={demandTextGeneratorResponse !== null}
                  loading={loading}
                  debug={debug}
                  setDebug={setDebug}
                  onSenderSubmit={onSendSubmit}
                />
              </TabPanel>
            </div>
          </Tabs>
        </div>

        {/* Toast y Overlay */}
        <ToastContainer toastStyle={{ zIndex: 9999 }}/>
        <FullPageOverlay isVisible={loading && activeTab !== 0} toastMessage={toastMessage} />
      </div>
    </div>
  );
}
