import classNames from "classnames";
import { ModalAddItem } from "@/components/modal";
import { DemandTextRequestNature } from "@/types/request";

const OPTIONS: { id: number, label: string, value: DemandTextRequestNature, help: string }[] = [
  {
    id: 1,
    label: "Señala bienes para la traba del embargo",
    value: "indicate_asset_seizure_goods_for_lockdown",
    help: "Señala bienes de los demandados, ya sea en su totalidad o mediante una lista de bienes específicos.",
  },
  { 
    id: 2,
    label: "Designa depositario provisional",
    value: "appoint_provisional_depositary",
    help: "Designa depositario provisional de los bienes que se embarguen al propio ejecutado, bajo su responsabilidad civil y criminal.",
  },
  { 
    id: 3,
    label: "Acompaña documentos",
    value: "include_documents",
    help: "Indica los documentos que se van a entregar al tribunal, por ejemplo, pagarés y certificados varios.",
  },
  { 
    id: 4,
    label: "Señala correos electrónicos",
    value: "indicate_emails",
    help: "Señala direcciones de correo electrónico de abogados para fines de notificación.",
  },
  { 
    id: 5,
    label: "Acredita personería",
    value: "accredit_personality",
    help: "Acredita personería para actuar en representación de uno o más demandantes, normalmente respaldada por una escritura pública.",
  },
  {
    id: 6,
    label: "Patrocinio y poder",
    value: "sponsorship_and_power",
    help: "Asume patrocionio y poder de la causa como abogado habilitado y, opcionalmente, delega poder a otro abogado, entregando sus datos.",
  },
  { 
    id: 7,
    label: "Solicita exhorto",
    value: "request_exhortation",
    help: "Justifica y solicita que se realice exhorto de la causa a un tribunal externo."
  },
  { 
    id: 8,
    label: "Notificación Art. 44 CPC.",
    value: "cpc_notification",
    help: "Solicita que el ministro de fe notifique a los demandados sobre el procedimiento."
  },
  { 
    id: 9,
    label: "Otro",
    value: "other",
    help: "Generado en base al contexto proporcionado."
  },
]

interface ModalDemandTextRequestsProps {
  isVisible: boolean;
  onClose: () => void;
  onAddItem: (label: string, value: DemandTextRequestNature, text: string, id: string) => void;
  className?: string;
  exclude?: DemandTextRequestNature[];
}

const ModalDemandTextRequests = ({ isVisible, onClose, onAddItem, className, exclude = [] }: ModalDemandTextRequestsProps) => {
  const handleAddItem = (value: DemandTextRequestNature, additionalText?: string) => {
    const option = OPTIONS.find(opt => opt.value === value);
    if (option) {
      onAddItem(option.label, value, additionalText || "", option.id.toString());
    }
  };

  return (
    <ModalAddItem<DemandTextRequestNature>
      className={classNames(className)}
      title="Agregar otrosí"
      isVisible={isVisible}
      onClose={onClose}
      options={OPTIONS.filter(({ value }) => value === "other" || !exclude.includes(value))}
      onAddItem={handleAddItem}
      additionalLabel="Contexto"
      additionalPlaceholder="Contexto del otrosí (opcional)"
    />
  );
};

export default ModalDemandTextRequests;
export { OPTIONS as MODAL_DEMAND_TEXT_REQUESTS_OPTIONS };
