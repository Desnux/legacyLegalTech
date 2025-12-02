import { useState } from "react";
import classNames from "classnames";
import { IconChevronDown } from "@tabler/icons-react";
import { AdditionalRequestGroup, DataSearcher, DollarCertificate, TextAreaInput } from "@/components/input";
import ModalDemandTextRequests from "@/components/modal/modal-demand-text-requests";
import { UseFormRegister, UseFormWatch } from "react-hook-form";

interface Request {
  label: string;
  value: string;
  text: string;
  id: string;
}

interface OptionalInfoProps {
  label?: string;
  setValue: any;
  watch: UseFormWatch<any>;
  register: UseFormRegister<any>;
  errors: any;
  onIncorporate?: (content: string) => void;
}

const OptionalInfo = ({ label = "Información opcional", setValue, watch, register, errors, onIncorporate }: OptionalInfoProps) => {
  const [isCollapsed, setIsCollapsed] = useState<boolean>(true);
  const [isModalDemandTextRequestsOpen, setIsModalDemandTextRequestsOpen] = useState<boolean>(false);
  
  const toggleCollapse = () => {
    setIsCollapsed(!isCollapsed);
  };

  return (
    <div className="border border-gray-300 rounded-md md:rounded-lg p-4">
      <div
        className="flex justify-between items-center cursor-pointer"
        onClick={toggleCollapse}
      >
        <h3 className="text-sm flex gap-x-2 items-center md:text-base">{ label }</h3>
        <IconChevronDown
          size={20}
          className={classNames("transition-transform", {
            "rotate-180": !isCollapsed,
          })}
        />
      </div>
      {!isCollapsed && (
        <div className="border-t border-gray-300 mt-4 pt-4 flex flex-col gap-2">
          <TextAreaInput
            name="reasonContent"
            label="Motivos de demanda"
            placeholder="Ruega, etc."
            register={register}
            errors={errors}
          />
          <AdditionalRequestGroup 
            label="Otrosíes"
            requests={watch("requests")}
            setRequests={(r) => setValue("requests", r)}
            onAdd={() => setIsModalDemandTextRequestsOpen(true)}
          />
          {/* <DollarCertificate setValue={setValue} watch={watch}/> */}
          {/* <DataSearcher className="border-t border-gray-300 pt-6 mt-4" onIncorporate={onIncorporate}/> */}
        </div>
      )}
      <ModalDemandTextRequests
       isVisible={isModalDemandTextRequestsOpen}
       onClose={() => setIsModalDemandTextRequestsOpen(false)}
       onAddItem={(label, value, text, id) => {
         setValue("requests", [...watch("requests"), { label, value, text, id }]);
       }}
       exclude={watch("requests").map((request: Request) => request.value)}
      />
    </div>
  );
};

export default OptionalInfo;
