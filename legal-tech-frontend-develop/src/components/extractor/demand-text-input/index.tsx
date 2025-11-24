"use client";

import { useEffect, useState } from "react";
import { v4 as uuidv4 } from "uuid";
import { useForm, FieldErrors, SubmitHandler, useFieldArray, Controller } from "react-hook-form";
import classNames from "classnames";
import Button from "@/components/button";
import { DataSearcher, FileGroup, Dropdown } from "@/components/input";
import { RutInput } from "@/components/input";
import { Message } from "@/components/information";
import { MODAL_DEMAND_TEXT_REQUESTS_OPTIONS } from "@/components/modal";
import { DemandTextInputInformation, EntityType, Participant, ParticipantRole } from "@/types/demand-text";
import { FileWithContext } from "@/types/file";
import { Request } from "@/types/request";
import { IconChevronDown, IconChevronUp, IconAlertTriangleFilled, IconFileText, IconArrowRight } from '@tabler/icons-react';
import SubtleLoader from "@/components/loading/subtle-loader";
import { DEFAULT_PARTICIPANTS, SELECTABLE_PARTICIPANT_TYPES } from "@/utils/demand-text-input-data";
import { formatInputCurrency } from "@/utils/currency";

interface Inputs {
  dollarCertificate?: any;
  participants: Participant[];
  reasonContent: string;
  requests: Request[];
  files: FileWithContext[];
}

interface DemandTextInputExtractorProps {
  className?: string;
  loading: boolean;
  extractionLoading?: boolean;
  onExtractorSubmit: (data: Inputs) => Promise<void>;
  onExtractorPDFSubmit: (data: Inputs) => Promise<void>;
  extractedPdfInformation?: DemandTextInputInformation;  
}

const ParticipantForm = ({ 
  participant,
  onRemove,
  register, 
  errors,
  index,
  control,
  setValue,
  watch
}: { 
  participant: Participant;
  onRemove: () => void;
  register: any; 
  errors: any;
  index: number;
  control: any;
  setValue: any;
  watch: any;
}) => {
  const path = `participants.${index}`;
  const error = errors.participants?.[participant.id] || {};

  if (participant.role === 'plaintiff' || participant.role === 'sponsoring_attorney' || participant.role === 'plaintiff_legal_representative') {
    return null;
  }

  return (
    <div className="relative flex flex-col gap-y-1 border p-2 rounded-lg bg-gray-100">
      <div className="flex justify-between items-center">
        <h2 className="text-sm font-semibold"></h2>
        <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={onRemove}
              className="text-red-500 hover:text-red-700 flex items-center gap-2"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
              </svg>
              Eliminar
            </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-9 gap-3">
          <div className="col-span-3 mt-1">
            <Dropdown
              name={`${path}.role`}
              label="Rol"
              options={SELECTABLE_PARTICIPANT_TYPES as any}
              register={register}
              setValue={setValue}
              watch={watch}
              required
              error={error.role && "Rol requerido"}
            />
          </div>
      
        <div className="col-span-2">
          <RutInput
            name={`${path}.dni`}
            label="RUT *"
            register={register}
            setValue={setValue}
            errors={errors}
            required="Debe ingresar su RUT"
          />
        </div>
      
        <div className="col-span-4 flex flex-col gap-1 mt-2">
          <label htmlFor={`${path}.name`} className="text-sm font-semibold text-charcoal-gray">
            Nombre
          </label>
          <input
            {...register(`${path}.name`)}
            placeholder="Nombre"
            className={classNames(
              "border rounded-lg p-3 text-body-sm transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-teal-green/20",
              {
                "border-red-500 focus:border-red-500 focus:ring-red-500/20": error.name,
                "border-medium-gray focus:border-teal-green": !error.name
              }
            )}
          />
          {error.name && <p className="text-red-500 text-small mt-1">{error.name.message}</p>}
        </div>

        <div className="col-span-5 flex flex-col gap-1">
          <label htmlFor={`${path}.address`} className="text-sm font-semibold text-charcoal-gray">
            Dirección completa
          </label>
          <input
            {...register(`${path}.address`)}
            placeholder="Ingrese la dirección completa"
            className={classNames(
              "border rounded-lg p-3 text-body-sm transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-teal-green/20",
              {
                "border-red-500 focus:border-red-500 focus:ring-red-500/20": error.address,
                "border-medium-gray focus:border-teal-green": !error.address
              }
            )}
          />
          {error.address && <p className="text-red-500 text-small mt-1">{error.address.message}</p>}
        </div>
      </div>
    </div>
  );
};

const ExtractedInformationForm = ({ register, errors, pdfInformation, control }: { register: any, errors: any, pdfInformation: DemandTextInputInformation | null, control: any }) => {
  const [documentInformation, setDocumentInformation] = useState<Record<string, any>[]>([]);
  const [isExtractedInfoExpanded, setIsExtractedInfoExpanded] = useState(false);
  const [formattedAmounts, setFormattedAmounts] = useState<Record<number, string>>({});

  useEffect(() => {
    if (pdfInformation && pdfInformation.documents && pdfInformation.documents.length > 0) {
      setDocumentInformation(pdfInformation.documents);
      // Inicializar valores formateados
      const initialFormatted: Record<number, string> = {};
      pdfInformation.documents.forEach((doc, index) => {
        if (doc.amount) {
          initialFormatted[index] = formatInputCurrency(doc.amount.toString());
        }
      });
      setFormattedAmounts(initialFormatted);
    }
  }, [pdfInformation]);


  const handleAmountChange = (index: number, value: string, onChange: any) => {
    const formatted = formatInputCurrency(value);
    setFormattedAmounts(prev => ({ ...prev, [index]: formatted }));
    
    // Guardar el valor sin formato en el formulario
    const numbersOnly = value.replace(/\D/g, '');
    onChange(numbersOnly);
  };

  return (
    <div className="flex flex-col gap-y-4 border p-4 rounded-lg bg-light-gray border-medium-gray">
      <div className="flex justify-between items-center">
        <div className="flex items-center gap-2">
          <h2 className="text-h3 font-semibold text-petroleum-blue">Información Deuda</h2>
        </div>
        <button
          type="button"
          onClick={() => setIsExtractedInfoExpanded(!isExtractedInfoExpanded)}
          className="text-charcoal-gray hover:text-petroleum-blue transition-colors flex items-center gap-2"
        >
          {isExtractedInfoExpanded ? (
            <>
              <span>Contraer</span>
              <IconChevronUp size={20} />
            </>
          ) : (
            <>
              <span>Expandir</span>
              <IconChevronDown size={20} />
            </>
          )}
        </button>
      </div>
      {isExtractedInfoExpanded && (
        <>
          {documentInformation.map((docInfo, index) => (
            <div key={index} className="border p-4 rounded-lg bg-white">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-lg font-semibold">Documento {index + 1}</h3>
                  <div className="flex items-center gap-1 text-teal-700">
                    <IconAlertTriangleFilled size={16} />
                    <span className="text-sm">Revisar monto de deuda, fecha, número e intereses del documento</span>
                  </div>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                <div className="flex flex-col gap-1">
                  <label htmlFor={`amount_${index}`} className="text-sm font-semibold text-charcoal-gray">
                    Monto de la deuda <span className="text-red-500">*</span>
                  </label>
                  <Controller
                    name={`amount_${index}`}
                    control={control}
                    rules={{
                      required: true,
                      pattern: {
                        value: /^[0-9]+$/,
                        message: "Solo se permiten números"
                      }
                    }}
                    defaultValue={docInfo.amount || ''}
                    render={({ field: { onChange, value } }) => (
                      <input
                        type="text"
                        placeholder="Monto de la deuda"
                        value={formattedAmounts[index] || formatInputCurrency(value?.toString() || '')}
                        onChange={(e) => handleAmountChange(index, e.target.value, onChange)}
                        className={classNames(
                          "border rounded-lg p-3 text-body-sm transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-teal-green/20",
                          {
                            "border-red-500 focus:border-red-500 focus:ring-red-500/20": errors[`amount_${index}`],
                            "border-medium-gray focus:border-teal-green": !errors[`amount_${index}`]
                          }
                        )}
                      />
                    )}
                  />
                  {errors[`amount_${index}`] && <p className="text-red-500 text-small mt-1">Monto de la deuda requerido</p>}
                </div>
                <div className="flex flex-col gap-1">
                  <label htmlFor={`creation_date_${index}`} className="text-sm font-semibold text-charcoal-gray">
                    Fecha de Documento <span className="text-red-500">*</span>
                  </label>
                  <input
                    {...register(`creation_date_${index}`, { 
                      required: true
                    })}
                    type="date"
                    className={classNames(
                      "border rounded-lg p-3 text-body-sm transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-teal-green/20",
                      {
                        "border-red-500 focus:border-red-500 focus:ring-red-500/20": errors[`creation_date_${index}`],
                        "border-medium-gray focus:border-teal-green": !errors[`creation_date_${index}`]
                      }
                    )}
                    defaultValue={docInfo.creation_date || ''}
                  />
                  {errors[`creation_date_${index}`] && <p className="text-red-500 text-small mt-1">Fecha de creación requerida</p>}
                </div>
                <div className="flex flex-col gap-1">
                  <label htmlFor={`identifier_${index}`} className="text-sm font-semibold text-charcoal-gray">
                    Numero de Documento
                  </label>
                  <input
                    {...register(`identifier_${index}`)}
                    placeholder="Numero de Serie"
                    className={classNames(
                      "border rounded-lg p-3 text-body-sm transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-teal-green/20",
                      {
                        "border-red-500 focus:border-red-500 focus:ring-red-500/20": errors[`identifier_${index}`],
                        "border-medium-gray focus:border-teal-green": !errors[`identifier_${index}`]
                      }
                    )}
                    defaultValue={docInfo.identifier || ''}
                  />
                  {errors[`identifier_${index}`] && <p className="text-red-500 text-small mt-1">{errors[`identifier_${index}`]?.message}</p>}
                </div>
                <div className="flex flex-col gap-1">
                  <label htmlFor={`interest_rate_${index}`} className="text-sm font-semibold text-charcoal-gray">
                    Porcentaje de intereses
                  </label>
                  <input
                    {...register(`interest_rate_${index}`, {
                      validate: (value: any) => {
                        if (!value || value === '') {
                          return true;
                        }
                        
                        const stringValue = String(value);
                        if (stringValue.trim() === '') {
                          return true;
                        }
                        
                        const numValue = parseFloat(stringValue);
                        if (isNaN(numValue)) {
                          return 'Debe ser un número válido';
                        }
                        
                        if (numValue < 0 || numValue > 100) {
                          return 'El porcentaje debe estar entre 0 y 100';
                        }
                        
                        return true;
                      }
                    })}
                    placeholder="Porcentaje de intereses"
                    className={classNames(
                      "border rounded-lg p-3 text-body-sm transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-teal-green/20",
                      {
                        "border-red-500 focus:border-red-500 focus:ring-red-500/20": errors[`interest_rate_${index}`],
                        "border-medium-gray focus:border-teal-green": !errors[`interest_rate_${index}`]
                      }
                    )}
                    defaultValue={docInfo.interest_rate || ''}
                  />
                  {errors[`interest_rate_${index}`] && <p className="text-red-500 text-small mt-1">{errors[`interest_rate_${index}`]?.message}</p>}
                </div>
              </div>
            </div>
          ))}
        </>
      )}
    </div>
  );
};

const EXTRACTOR_STAGES = [
  { text: 'Extrayendo texto y metadatos del lote.', delay: 2000 },
  { text: 'Aplicando limpieza y segmentación del contenido.', delay: 2000 },
  { text: 'Enviando documentos a motor de IA.', delay: 2000 },
  { text: 'Analizando cada documento en paralelo con el motor de IA.', delay: 10000 },
  { text: 'Ejecución concurrente en curso; validando respuesta.', delay: 10000 },
  { text: 'Análisis por documento completado.', delay: 5000 },
  { text: 'Procesando información visual.', delay: 2000 },
];

const DemandTextInputExtractor = ({ className, loading, extractionLoading = false, onExtractorSubmit, onExtractorPDFSubmit, extractedPdfInformation }: DemandTextInputExtractorProps) => {
  const [extractionError, setExtractionError] = useState<string | null>(null);
  const [pdfInformation, setPdfInformation] = useState<DemandTextInputInformation | null>(null);
  const [isParticipantsExpanded, setIsParticipantsExpanded] = useState(false);
  const [currentMessageIndex, setCurrentMessageIndex] = useState(0);

  const ALLOWED_REQUEST_IDS = [1, 2, 3, 5, 6]; 
  const { control, register, handleSubmit, setValue, watch, getValues, reset, formState: { errors } } = useForm<Inputs>({
    defaultValues: {
      participants: DEFAULT_PARTICIPANTS,
      requests: [],
      reasonContent: "RUEGA, etc.",
      files: [],
    },
    mode: 'onChange'
  });

  useEffect(() => {
    if (extractionLoading) {
      setCurrentMessageIndex(0);
      const timeoutIds: NodeJS.Timeout[] = [];

      const scheduleNextMessage = (index: number) => {
        if (index >= EXTRACTOR_STAGES.length - 1) {
          return;
        }
        
        const nextIndex = index + 1;
        const timeoutId = setTimeout(() => {
          setCurrentMessageIndex(nextIndex);
          scheduleNextMessage(nextIndex);
        }, EXTRACTOR_STAGES[index].delay);
        
        timeoutIds.push(timeoutId);
      };

      scheduleNextMessage(0);

      return () => {
        timeoutIds.forEach(id => clearTimeout(id));
      };
    }
  }, [extractionLoading]);

  useEffect(() => {
    setPdfInformation(null);

    // Limpiar error cuando se recibe información extraída
    if (extractedPdfInformation) {
      setExtractionError(null);
    }

    const hasValidInformation = extractedPdfInformation && (
      (extractedPdfInformation.plaintiff && 
        (extractedPdfInformation.plaintiff.name || 
         extractedPdfInformation.plaintiff.identifier || 
         extractedPdfInformation.plaintiff.address)) ||
      (extractedPdfInformation.sponsoring_attorneys?.some(attorney => 
        attorney.name || attorney.identifier || attorney.address)) ||
      (extractedPdfInformation.defendants?.some(defendant => 
        defendant.name || defendant.identifier || defendant.address)) ||
      (extractedPdfInformation.legal_representatives?.some(representative => 
        representative.name || representative.identifier || representative.address))
    );

    if (hasValidInformation) {
      setPdfInformation(extractedPdfInformation);
      
      if (extractedPdfInformation.documents?.length) {
        extractedPdfInformation.documents.forEach((docInfo, index) => {
          (setValue as any)(`amount_${index}`, docInfo.amount || '', { shouldValidate: true });
          (setValue as any)(`identifier_${index}`, docInfo.identifier || '', { shouldValidate: true });
          (setValue as any)(`interest_rate_${index}`, docInfo.interest_rate || '', { shouldValidate: true });
          const currentDateValue = (getValues as any)(`creation_date_${index}`);
          if (!currentDateValue || currentDateValue.trim() === '') {
            (setValue as any)(`creation_date_${index}`, docInfo.creation_date || '', { shouldValidate: true });
          }
        });
      }

      const pdfParticipants: Participant[] = [];

      if (extractedPdfInformation.plaintiff && 
          (extractedPdfInformation.plaintiff.name || 
           extractedPdfInformation.plaintiff.identifier || 
           extractedPdfInformation.plaintiff.address)) {
        pdfParticipants.push({
          id: uuidv4(),
          name: extractedPdfInformation.plaintiff.name || '',
          dni: extractedPdfInformation.plaintiff.identifier || '',
          address: extractedPdfInformation.plaintiff.address || '',
          role: ParticipantRole.PLAINTIFF
        });
      }

      if (extractedPdfInformation.sponsoring_attorneys?.length) {
        extractedPdfInformation.sponsoring_attorneys.forEach(attorney => {
          if (attorney.name || attorney.identifier || attorney.address) {
            pdfParticipants.push({
              id: uuidv4(),
              name: attorney.name || '',
              dni: attorney.identifier || '',
              address: attorney.address || '',
              role: ParticipantRole.SPONSORING_ATTORNEY
            });
          }
        });
      }

      if (extractedPdfInformation.defendants?.length) {
        extractedPdfInformation.defendants
          .forEach(defendant => {
            if (defendant.name || defendant.identifier || defendant.address) {
              pdfParticipants.push({
                id: uuidv4(),
                name: defendant.name || '',
                dni: defendant.identifier || '',
                address: defendant.address || '',
                legal_representatives: defendant.legal_representatives || [],
                entity_type: defendant.entity_type || EntityType.NATURAL,
                role: defendant.type === 'debtor' ? ParticipantRole.DEFENDANT : ParticipantRole.GUARANTEE
              });

              if (defendant.legal_representatives?.length) {
                defendant.legal_representatives.forEach((legalRep: { name?: string; identifier?: string; address?: string }) => {
                  if (legalRep.name || legalRep.identifier || legalRep.address) {
                    pdfParticipants.push({
                      id: uuidv4(),
                      name: legalRep.name || '',
                      dni: legalRep.identifier || '',
                      address: legalRep.address || '',
                      legal_representatives: [],
                      entity_type: EntityType.NATURAL,
                      role: ParticipantRole.LEGAL_REPRESENTATIVE
                    });
                  }
                });
              }
            }
          });
      }

      if (extractedPdfInformation.legal_representatives?.length) {
        extractedPdfInformation.legal_representatives.forEach(representative => {
          if (representative.name || representative.identifier || representative.address) {
            pdfParticipants.push({
              id: uuidv4(),
              name: representative.name || '',
              dni: representative.identifier || '',
              address: representative.address || '',
              role: ParticipantRole.LEGAL_REPRESENTATIVE
            });
          }
        });
      }

      if (pdfParticipants.length > 0) {
        const mergedParticipants = [...DEFAULT_PARTICIPANTS];
        
        pdfParticipants.forEach(pdfParticipant => {
          const uniqueRoles = [ParticipantRole.PLAINTIFF, ParticipantRole.SPONSORING_ATTORNEY, ParticipantRole.PLAINTIFF_LEGAL_REPRESENTATIVE, ParticipantRole.LEGAL_REPRESENTATIVE];
          const hasRoleConflict = uniqueRoles.includes(pdfParticipant.role) && 
            mergedParticipants.some(
              defaultParticipant => defaultParticipant.role === pdfParticipant.role
            );
          
          if (!hasRoleConflict) {
            mergedParticipants.push(pdfParticipant);
          }
        });

        setValue('participants', mergedParticipants);
      }

      if (extractedPdfInformation.secondary_requests?.length) {
        const updatedRequests = MODAL_DEMAND_TEXT_REQUESTS_OPTIONS
          .filter(({ id }) => ALLOWED_REQUEST_IDS.includes(id))
          .map(({ label, value, id }) => {
            const matchingRequest = extractedPdfInformation.secondary_requests?.find(
              req => req.nature === value && req.context
            );
            return {
              label,
              value,
              text: matchingRequest?.context || "",
              id: id.toString()
            };
          });
        setValue('requests', updatedRequests);
      }
    } else {
      console.log('No valid PDF information found');
    }
  }, [extractedPdfInformation, setValue]);

  const {
    fields: participantFields,
    append,
    remove,
  } = useFieldArray({
    control,
    name: "participants",
  });

  const addParticipant = () => {
    if (participantFields.length >= 10) {
      return;
    }

    append({
      id: uuidv4(),
      name: '',
      dni: '',
      address: '',
      role: ParticipantRole.DEFENDANT
    });
  };

  const removeParticipant = (index: number) => {
    remove(index);
  };

  const onError = (errors: FieldErrors<Inputs>) => {
    if (errors.participants) {
      const invalids = Object.entries(errors.participants).map(([id, fields]) => {
        const failedFields = Object.keys(fields || {}).join(', ');
        return `Participante ${id}: ${failedFields}`;
      });
  
      console.warn("Errores de validación:", invalids.join('\n'));
    }
  };
  

  const onIncorporate = (content: string) => {
    const requests = watch("requests");
    const originalDocumentRequestIndex = requests.findIndex(
      ({ value }) => value === "indicate_asset_seizure_goods_for_lockdown"
    );
  
    if (originalDocumentRequestIndex !== -1) {
      const updatedRequests = [...requests];
      const existingRequest = updatedRequests[originalDocumentRequestIndex];
  
      updatedRequests[originalDocumentRequestIndex] = {
        ...existingRequest,
        text: content,
      };
      setValue("requests", updatedRequests);
    } else {
      console.warn("No se encontró la solicitud de embargo para incorporar el contenido.");
    }
  };

  // Función para validar si todos los campos requeridos están completos
  const isFormValid = () => {
    const formData = watch();
    
    // Verificar que hay archivos
    if (!formData.files || formData.files.length === 0) {
      return false;
    }
    
    // Verificar que todos los participantes tienen los campos requeridos
    const hasValidParticipants = formData.participants.every(participant => 
      participant.dni && participant.dni.trim() !== ''
    );
    
    return hasValidParticipants;
  };

  const onSubmit: SubmitHandler<Inputs> = async (data) => {
    if (data.files.length > 10) {
      return;
    }
    if (data.files.length < 1) {
      return;
    }

    const hasInvalidParticipants = data.participants.some(
      participant => !participant.dni
    );

    if (hasInvalidParticipants) {
      return;
    }

    await onExtractorSubmit(data);
  };

  const onSubmitPDF: SubmitHandler<Inputs> = async (data) => {
    if (data.files.length < 1) {
      setExtractionError("Debe adjuntar al menos un archivo de deuda para extraer información.");
      return;
    }
    
    // Limpiar toda la información previa excepto los archivos adjuntos
    const currentFiles = watch("files");
    setPdfInformation(null);
    reset({
      participants: DEFAULT_PARTICIPANTS,
      requests: [],
      reasonContent: "RUEGA, etc.",
      files: currentFiles || []
    });

    setExtractionError(null);
    try {
      await onExtractorPDFSubmit(data);
    } catch (error) {
      setExtractionError(error instanceof Error ? error.message : "Error al extraer información del PDF");
    }
  };

  return (
    <div className={className}>
      <Message
        type="info"
        message="Para comenzar ingrese un documento, el sistema extraerá los datos para generar un texto de demanda. Los campos marcados con * son obligatorios."
        className="mb-6"
      />
      <form onSubmit={handleSubmit(onSubmit, onError)} encType="multipart/form-data" className="flex flex-col h-full">
        <div className="flex flex-col gap-y-6 flex-1">
          <FileGroup
            label="Archivos de deuda"
            filesWithContext={watch("files")}
            setFilesWithContext={(f) => setValue("files", f)}
            accept="application/pdf"
          />
          
          {/* Botón de extracción */}
          <Button
            variant="primary"
            size="md"
            disabled={!watch("files") || watch("files").length === 0 || extractionLoading}
            onClick={handleSubmit(onSubmitPDF)}
          >
            {extractionLoading ? "Extrayendo información..." : "Extraer información de PDF"}
          </Button>

          {/* Loader sutil durante la extracción */}
          {extractionLoading && (
            <div className="bg-light-gray/50 rounded-lg border border-medium-gray">
              <SubtleLoader message={EXTRACTOR_STAGES[currentMessageIndex].text} />
            </div>
          )}

          {/* Mensaje de error */}
          {extractionError && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <div className="flex items-center gap-2">
                <IconAlertTriangleFilled size={16} className="text-red-500" />
                <p className="text-red-700 text-sm font-medium">{extractionError}</p>
              </div>
            </div>
          )}

          {pdfInformation && (
            <>
            <Message
                type="success"
                message="Revise la información extraída y modifique los datos si es necesario."
                className="mb-0"
                />
            <ExtractedInformationForm 
              register={register} 
              errors={errors} 
              pdfInformation={pdfInformation}
              control={control}
              />
            </>
          )}

          {pdfInformation && 
           (pdfInformation.plaintiff?.name || 
            pdfInformation.sponsoring_attorneys?.some(a => a.name) ||
            pdfInformation.defendants?.some(d => d.name) ||
            pdfInformation.legal_representatives?.some(r => r.name)) && (
            <div className="flex flex-col gap-y-2 border p-4 rounded-lg bg-gray-50">
              <div className="flex justify-between items-center">
                <h2 className="text-xl font-semibold">Demandados</h2>
                <button
                  type="button"
                  onClick={() => setIsParticipantsExpanded(!isParticipantsExpanded)}
                  className="text-gray-600 hover:text-gray-800 transition-colors flex items-center gap-2"
                >
                  {isParticipantsExpanded ? (
                    <>
                      <span>Contraer</span>
                      <IconChevronUp size={20} />
                    </>
                  ) : (
                    <>
                      <span>Expandir</span>
                      <IconChevronDown size={20} />
                    </>
                  )}
                </button>
              </div>
              {isParticipantsExpanded && (
                <>
                  {participantFields.map((participant, index) => (
                    <ParticipantForm
                      key={participant.id}
                      participant={participant}
                      index={index}
                      onRemove={() => removeParticipant(index)}
                      register={register}
                      errors={errors}
                      control={control}
                      setValue={setValue}
                      watch={watch}
                    />
                  ))}
                  <div className="flex justify-start mt-4">
                    <Button
                      variant="primary"
                      size="sm"
                      onClick={addParticipant}
                    >
                      Agregar Participante
                    </Button>
                  </div>
                </>
              )}

            </div>
          )}
          
          {pdfInformation && (
            <div className="flex flex-col gap-y-2 pb-24">
              <DataSearcher 
                className="border-b border-gray-300 pb-6 mb-4" 
                onIncorporate={onIncorporate}
                participants={watch("participants")}
                />
            </div>
          )}
          
          {/* Botón fijo para generar */}
          {pdfInformation && (
            <div className="fixed bottom-12 left-1/2 transform -translate-x-1/2 z-20">
              <Button
                variant="primary"
                loading={loading}
                disabled={loading || !isFormValid()}
                onClick={handleSubmit(onSubmit, onError)}
                className="flex items-center gap-2"
              >
                <span>{loading ? "Generando..." : "Generar"}</span>
                <IconArrowRight size={16} />
              </Button>
            </div>
          )}
        </div>
      </form>
    </div>
  );
};

export default DemandTextInputExtractor;
export type { Inputs };