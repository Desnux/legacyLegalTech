import { useState } from "react";
import classNames from "classnames";
import { IconChevronDown } from "@tabler/icons-react";
import { DataSearcher, DollarCertificate } from "@/components/input";

interface OptionalInfoProps {
  label?: string;
  setValue: any;
  watch: any;
  onIncorporate?: (content: string) => void;
}

const OptionalInfo = ({ label = "Información opcional", setValue, watch, onIncorporate }: OptionalInfoProps) => {
  const [isCollapsed, setIsCollapsed] = useState<boolean>(true);

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
          <DollarCertificate setValue={setValue} watch={watch}/>
          <DataSearcher className="border-t border-gray-300 pt-6 mt-4" onIncorporate={onIncorporate}/>
        </div>
      )}
    </div>
  );
};

export default OptionalInfo;
