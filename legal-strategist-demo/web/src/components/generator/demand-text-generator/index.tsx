"use client";

import { useRef, useState } from "react";
import { v4 as uuidv4 } from "uuid";
import { Tab, Tabs, TabList, TabPanel } from "react-tabs";
import { useForm, FieldErrors, SubmitHandler } from "react-hook-form";
import { toast, ToastContainer } from "react-toastify";
import { PDFViewer, pdf } from "@react-pdf/renderer";
import { DemandTextAnalyzer } from "@/components/analyzer";
import { ButtonCopy, ButtonGenerate, ButtonSend } from "@/components/button";
import { DemandTextCorrector } from "@/components/corrector";
import { AdditionalRequestGroup, DollarCertificate, FileExtra, FileItem, FileGroup, FileInput, LockedInput, PasswordInput, RandomSeedInput, RutInput, TextAreaInput } from "@/components/input";
import { ModalConfirm, ModalDemandTextRequests, MODAL_DEMAND_TEXT_REQUESTS_OPTIONS } from "@/components/modal";
import { PDFDemandText } from "@/components/pdf";
import { Spinner } from "@/components/state";
import { sendDemandTextAnalyzerRequest } from "@/services/analyzer";
import { caseCreateFromDemandText } from "@/services/case";
import { sendDemandTextCorrectorRequest } from "@/services/corrector";
import { sendDemandTextGeneratorRequest, DemandTextGeneratorResponse } from "@/services/generator";
import { DemandTextSenderRequest, sendDemandTextSenderRequest } from "@/services/sender";
import { DemandTextAnalysis, DemandTextCorrectionForm, DemandTextStructure } from "@/types/demand-text";
import { FileWithContext } from "@/types/file";
import { DemandTextRequestNature, Request } from "@/types/request";
import { formatRut } from "@/utils/rut";
import { FullPageOverlay } from "@/components/loading";
import "react-toastify/dist/ReactToastify.css";

interface GenerateInputs {
  dollarCertificate?: any;
  content: string;
  seed?: number;
  requests: Request[];
  files: FileWithContext[];
}

interface SendInputs {
  contract: FileList | null;
  mandate: FileList | null;
  password: string;
  rut: string;
}

const DemandTextGenerator = () => {
  const [isModalConfirmOpen, setIsModalConfirmOpen] = useState(false);
  const [isModalDemandTextRequestsOpen, setIsModalDemandTextRequestsOpen] = useState(false);
  const [activeTab, setActiveTab] = useState(0);
  const [textGeneratorResponse, setTextGeneratorResponse] = useState<DemandTextGeneratorResponse | null>(null);
  const [textAnalyzerResponse, setTextAnalyzerResponse] = useState<DemandTextAnalysis | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [loadingAnalysis, setLoadingAnalysis] = useState<boolean>(false);
  const [textAreaInputHeight, setTextAreaInputHeight] = useState("auto");
  const [textAreaInputScrollPosition, setTextAreaInputScrollPosition] = useState(0);
  const [lockedGenerationFiles, setLockedGenerationFiles] = useState<FileWithContext[]>([]);
  const demandTextPDF = useRef<Blob | null>(null);
  const [files, setFiles] = useState<FileItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [toastMessage, setToastMessage] = useState<string>("");
  const [dollarCertificate, setDollarCertificate] = useState<File | undefined>(undefined);

  const { 
    register: registerGenerate,
    handleSubmit: handleGenerateSubmit,
    setValue: setGenerateValue,
    watch: watchGenerate,
    formState: { errors: generateErrors },
  } = useForm<GenerateInputs>({
    defaultValues: {
      requests: MODAL_DEMAND_TEXT_REQUESTS_OPTIONS.filter((_, index) => { return index < 3; }).map(({ label, value }) => { 
        return { label, value, text: "", id: uuidv4() }; 
      }),
      files: [],
    },
  });

  const { 
    register: registerSend,
    handleSubmit: handleSendSubmit,
    setValue: setSendValue,
    watch: watchSend,
    reset: resetSend,
    formState: { errors: sendErrors },
  } = useForm<SendInputs>({
    defaultValues: { contract: null, mandate: null, password: "", rut: "" },
  });

  const openModalDemandTextRequests = () => setIsModalDemandTextRequestsOpen(true);
  const closeModalDemandTextRequests = () => setIsModalDemandTextRequestsOpen(false);

  const analyzeResponse = async (input: DemandTextStructure) => {
    setTextAnalyzerResponse(null);
    setLoadingAnalysis(true);

    try {
      const res = await sendDemandTextAnalyzerRequest(input);
      console.log("Response from the API:", res);
      setTextAnalyzerResponse(res);
      toast.success("Análisis exitoso.");
    } catch (e) {
      toast.error(`${e}`, { autoClose: 10000 });
    } finally {
      setLoadingAnalysis(false);
    }
  };

  const onGenerateSubmit: SubmitHandler<GenerateInputs> = async (data) => {
    if (data.files.length > 10) {
      toast.error("No se permite adjuntar más de 10 archivos de deuda.");
      return;
    }

    if (data.files.length < 1) {
      toast.error("Debe adjuntar al menos un archivo de deuda.");
      return;
    }

    const reasonsPerDocument = Array.from(data.files.map(({ context }) => context.trim() || ""));
    const additionalData: Record<string, string[] | Record<string, string>[]> = {};
    let contentToSend = data.content;

    if (reasonsPerDocument) {
      additionalData["reasons_per_document"] = reasonsPerDocument;
    }

    if (data.requests) {
      additionalData["secondary_requests"] = data.requests.map(({ value, text }) => { return { nature: value, context: text } });
    }

    contentToSend += JSON.stringify(additionalData);

    setLoading(true);
    setActiveTab(1);

    try {
      if (data.dollarCertificate) {
        setDollarCertificate(data.dollarCertificate);
      }
      
      setToastMessage('Generando texto de demanda...');
      setIsLoading(true);
      const res = await sendDemandTextGeneratorRequest(contentToSend, data.files, data.seed, data.dollarCertificate);
      console.log("Response from the API:", res);
      setTextGeneratorResponse(res);
      setLockedGenerationFiles(data.files);
      toast.success("Generación exitosa.");

      if (res.structured_output) {
        const pdfInstance = pdf(<PDFDemandText {...res.structured_output}/>);
        const blob = await pdfInstance.toBlob();
        demandTextPDF.current = blob;
        analyzeResponse(res.structured_output);
      } else {
        console.warn("Could not bind generated PDF file");
      }
    } catch (e) {
      setActiveTab(0);
      toast.error(`${e}`, { autoClose: 10000 });
    } finally {
      setIsLoading(false);
      setToastMessage("");
      setLoading(false);
    }
  };

  const onSendSubmit: SubmitHandler<SendInputs> = async (data) => {
    if (!demandTextPDF?.current) {
      toast.error("Debe adjuntar un texto de demanda.");
      return;
    }

    if (!data.contract) {
      toast.error("Debe adjuntar un contrato causal.");
      return;
    }

    if (!data.mandate) {
      toast.error("Debe adjuntar un mandato.");
      return;
    }

    if (lockedGenerationFiles.length > 10) {
      toast.error("No se permite adjuntar más de 10 archivos de deuda.");
      return;
    }

    if (lockedGenerationFiles.length < 1) {
      toast.error("Debe adjuntar al menos un archivo de deuda.");
      return;
    }
    
    if (textGeneratorResponse === null) {
      toast.error("Debe volver a generar el texto de demanda.");
      return;
    }
    
    if ((textGeneratorResponse.structured_output?.sponsoring_attorneys || []).length === 0) {
      toast.error("Debe indicar al menos un abogado por los demandantes.");
      return;
    }
    if ((textGeneratorResponse.structured_output?.plaintiffs || []).length === 0) {
      toast.error("Debe indicar al menos un demandante.");
      return;
    }
    if ((textGeneratorResponse.structured_output?.defendants || []).length === 0) {
      toast.error("Debe indicar al menos un demandado.");
      return;
    }

    const extraFiles = files.map((fileItem) => fileItem.file);
    const extraFilesLabels = files.map((fileItem) => fileItem.name);

    setIsModalConfirmOpen(false);
    setLoading(true);

    const senderRequestBody: DemandTextSenderRequest = {
      demandTextPDF: demandTextPDF.current,
      contract: data.contract,
      mandate: data.mandate,
      password: data.password,
      rut: formatRut(data.rut),
      legalSubject: textGeneratorResponse.structured_output?.legal_subject || "general_collection",
      extraFiles: extraFiles,
      extraFilesLabels: extraFilesLabels,
      sponsoringAttorneys: textGeneratorResponse.structured_output?.sponsoring_attorneys || [],
      plaintiffs: textGeneratorResponse.structured_output?.plaintiffs || [],
      defendants: textGeneratorResponse.structured_output?.defendants || [],
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

    try {
      setToastMessage("Enviando texto de demanda a PJUD...");
      setIsLoading(true);
      const res = await sendDemandTextSenderRequest(senderRequestBody);
      console.log("Response from the API:", res);
      
      if (res?.status === 200) {      
        try {
          const caseObject = await caseCreateFromDemandText(textGeneratorResponse);
          console.log(caseObject);
        } catch (e) {
          console.log(e);
        }
        resetSend();
        toast.success("Envío exitoso a PJUD, vaya a \"Enviar demanda\" para enviar al tribunal.");
      } else {
        toast.warning(`${res?.message}`, { autoClose: 10000 });
      }
    } catch (e) {
      toast.error(`${e}`, { autoClose: 10000 });
    } finally {
      setToastMessage("");
      setIsLoading(false);
      setLoading(false);
    }
  };

  const onGenerateError = (errors: FieldErrors<GenerateInputs>) => {
    if (errors.content) {
      toast.error("Debe indicar contenido del texto de demanda.");
    }
  };

  const onSendError = (errors: FieldErrors<SendInputs>) => {
    if (errors.contract) {
      toast.error("Debe adjuntar un contrato causal.");
    }
    
    if (errors.mandate) {
      toast.error("Debe adjuntar un mandato.");
    }
    
    if (errors.password) {
      toast.error("Debe ingresar una contraseña.");
    }
    
    if (errors.rut) {
      toast.error("Debe ingresar un RUT válido.");
    }
  };

  const handleAddRequest = (label: string, value: DemandTextRequestNature, text: string, id: string) => {
    setGenerateValue("requests", [...watchGenerate("requests"), { label, value, text, id }]);
  };

  const onCorrectSubmit = async (data: DemandTextCorrectionForm) => {
    if (textGeneratorResponse?.structured_output === undefined) {
      toast.error("Debe volver a generar el texto de demanda.");
      return;
    }

    setLoading(true);
    setActiveTab(1);

    try {
      setToastMessage("Ajustando texto de demanda...");
      setIsLoading(true);
      const res = await sendDemandTextCorrectorRequest(textGeneratorResponse.structured_output, data);
      console.log("Response from the API:", res);
      setTextGeneratorResponse(res);
      toast.success("Ajuste exitoso.");
      
      if (res.structured_output) {
        const pdfInstance = pdf(<PDFDemandText {...res.structured_output}/>);
        const blob = await pdfInstance.toBlob();
        demandTextPDF.current = blob;
        analyzeResponse(res.structured_output);
      } else {
        console.warn("Could not bind generated PDF file");
      }
    } catch (e) {
      setActiveTab(3);
      toast.error(`${e}`, { autoClose: 10000 });
    } finally {
      setToastMessage("");
      setIsLoading(false);
      setLoading(false);
    }
  };

  // TODO: Rework demo only functionality
  const handleIncorporate = (content: string) => {
    const requests = watchGenerate("requests");
    const originalDocumentRequestIndex = requests.findIndex(({ value }) => value === "indicate_asset_seizure_goods_for_lockdown");
    if (originalDocumentRequestIndex !== -1) {
      const updatedRequests = [...requests];
      const existingRequest = updatedRequests[originalDocumentRequestIndex];
      if (!existingRequest.text?.includes(content)) {
        if (existingRequest.text.length > content.length) {
          updatedRequests[originalDocumentRequestIndex] = {
            ...existingRequest,
            text: existingRequest.text
              ? content + "\n" + existingRequest.text
              : content,
          };
        } else {
          updatedRequests[originalDocumentRequestIndex] = {
            ...existingRequest,
            text: existingRequest.text
              ? existingRequest.text + "\n" + content
              : content,
          };
        }
        setGenerateValue("requests", updatedRequests);
      }
    } else {
      setGenerateValue("requests", requests.concat({
        value: "indicate_asset_seizure_goods_for_lockdown",
        label: "Señala bienes para la traba del embargo",
        text: content,
        id: uuidv4(),
      }));
    }
  }

  return (
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
          <Tab className="-mb-[1px] font-semibold py-1 text-sm md:text-base cursor-pointer hover:text-gray-900">
            Generar
          </Tab>
          <Tab className="-mb-[1px] font-semibold py-1 text-sm md:text-base cursor-pointer hover:text-gray-900">
            Resultado
          </Tab>
          <Tab className="-mb-[1px] font-semibold py-1 text-sm md:text-base cursor-pointer hover:text-gray-900">
            Análisis
          </Tab>
          <Tab className="-mb-[1px] font-semibold py-1 text-sm md:text-base cursor-pointer hover:text-gray-900">
            Ajustar
          </Tab>
          <Tab className="-mb-[1px] font-semibold py-1 text-sm md:text-base cursor-pointer hover:text-gray-900">
            Enviar
          </Tab>
        </TabList>
        <TabPanel>
          <form onSubmit={handleGenerateSubmit(onGenerateSubmit, onGenerateError)} encType="multipart/form-data" className="flex flex-col gap-y-8 h-full">
            <div className="flex flex-col gap-y-8 flex-1">
              <TextAreaInput
                name="content"
                label="Contenido"
                register={registerGenerate}
                errors={generateErrors}
                required
                height={textAreaInputHeight}
                onHeightChange={(newHeight) => setTextAreaInputHeight(newHeight)}
                scrollPosition={textAreaInputScrollPosition}
                onScrollChange={setTextAreaInputScrollPosition}
              />
              <AdditionalRequestGroup 
                label="Otrosíes"
                requests={watchGenerate("requests")}
                setRequests={(r) => setGenerateValue("requests", r)}
                onAdd={openModalDemandTextRequests}
              />
              <FileGroup
                label="Archivos de deuda"
                filesWithContext={watchGenerate("files")}
                setFilesWithContext={(f) => setGenerateValue("files", f)}
                accept="application/pdf"
              />
              <DollarCertificate
                label="Certificado de dólar"
                register={registerGenerate}
                setValue={setGenerateValue}
                watch={watchGenerate}
                errors={generateErrors}
                onIncorporate={handleIncorporate}
              />
            </div>
            <div className="border-t border-gray-300 h-[1px]"/>
            <RandomSeedInput
              className="hidden"
              name="seed"
              register={registerGenerate}
              setValue={setGenerateValue}
              errors={generateErrors}
            />
            <ButtonGenerate className="w-full" disabled={loading}/>
          </form>
          <ModalDemandTextRequests
            isVisible={isModalDemandTextRequestsOpen}
            onClose={closeModalDemandTextRequests}
            onAddItem={handleAddRequest}
            exclude={watchGenerate("requests").map(({ value }) => value)}
          />
        </TabPanel>
        <TabPanel className="flex flex-col">
          <div className="flex-1 flex flex-col bg-zinc-700 w-full relative">
            {loading && <Spinner className="flex-1 w-full h-full"/>}
            {!loading && textGeneratorResponse?.structured_output && (
              <>
                <PDFViewer className="h-full">
                  <PDFDemandText {...textGeneratorResponse.structured_output}/>
                </PDFViewer>
                <div className="absolute bottom-4 left-4 hidden">
                  <ButtonCopy textToCopy={JSON.stringify(textGeneratorResponse.structured_output, (key, value) => {
                    const fieldsToExclude = ["sponsoring_attorneys", "plaintiffs", "defendants"];
                    return fieldsToExclude.includes(key) ? undefined : value;
                  })}/>
                </div>
              </>
            )}
          </div>
        </TabPanel>
        <TabPanel className="flex flex-col">
          { textGeneratorResponse?.structured_output && textAnalyzerResponse ? (
            <DemandTextAnalyzer className="flex-1" input={textGeneratorResponse?.structured_output} analysis={textAnalyzerResponse}/>
          ) : (
            <>
              {loadingAnalysis ? <Spinner className="flex-1 w-full h-full"/> : (
                <div className="flex-1 text-gray-600 flex justify-center text-sm md:text-base items-center text-center p-8">
                  {textGeneratorResponse?.structured_output 
                    ? "No fue posible analizar el texto de demanda generado."
                    : "Genere un texto de demanda para obtener un análisis detallado."
                  }
                </div>
              )}
            </>
          )}
        </TabPanel>
        <TabPanel className="flex flex-col">
          {textGeneratorResponse?.correction_form ? (
            <DemandTextCorrector 
              analysis={textAnalyzerResponse ?? undefined}
              correctionForm={textGeneratorResponse?.correction_form}
              onSubmit={onCorrectSubmit}
            />
          ) : (
            <div className="flex-1 text-gray-600 flex justify-center text-sm md:text-base items-center text-center p-8">
              Genere un texto de demanda antes de ajustar valores.
            </div>
          )}
        </TabPanel>
        <TabPanel>
          <form onSubmit={() => {}} encType="multipart/form-data" className="flex flex-col gap-y-8 h-full">
            <div className="flex flex-col gap-y-8 flex-1">
              <LockedInput 
                label="Texto de demanda"
                placeholder="Debe generar un texto de demanda"
                value={textGeneratorResponse?.structured_output && "Texto de demanda generado"}
              />
              <FileInput
                name="contract"
                label="Contrato causal"
                register={registerSend}
                errors={sendErrors}
                currentFiles={watchSend("contract")}
                accept="application/pdf"
                setValue={setSendValue}
              />
              <FileInput
                name="mandate"
                label="Mandato"
                register={registerSend}
                errors={sendErrors}
                currentFiles={watchSend("mandate")}
                accept="application/pdf"
                setValue={setSendValue}
              />
              <FileExtra
                name="extraFiles"
                label="Archivos adicionales"
                filesWithContext={files}
                setFilesWithContext={setFiles}
                accept="application/pdf"
              />
            </div>
            <div className="border-t border-gray-300 h-[1px]"/>
            <RutInput
              name="rut"
              register={registerSend}
              setValue={setSendValue}
              errors={sendErrors}
              required="Debe ingresar su RUT"
              help="Necesario para automatizar el envío via PJUD"
            />
            <PasswordInput
              name="password"
              label="Clave Poder Judicial"
              register={registerSend}
              errors={sendErrors}
              help="Necesaria para automatizar el envío via PJUD"
            />
            <ButtonSend onClick={() => setIsModalConfirmOpen(true)} className="w-full" disabled={loading || !textGeneratorResponse?.structured_output}/>
          </form>
          <ModalConfirm
            isVisible={isModalConfirmOpen}
            title="Confirmar"
            onCancel={() => setIsModalConfirmOpen(false)}
            onConfirm={handleSendSubmit(onSendSubmit, onSendError)}
            message="¿Confirma que desea enviar el texto de demanda y todos los documentos asociados a PJUD?"
          />
        </TabPanel>
      </Tabs>
      <ToastContainer toastStyle={{ zIndex: 9999 }}/> {/* Aparece sobre FullPageOverlay y Spinner */}
      <FullPageOverlay isVisible={isLoading} toastMessage={toastMessage} />
    </div>
  )
};

export default DemandTextGenerator;
