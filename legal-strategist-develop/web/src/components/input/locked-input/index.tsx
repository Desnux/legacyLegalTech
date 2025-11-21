import { IconCircleCheckFilled } from "@tabler/icons-react";

interface LockedInputProps {
  label: string;
  placeholder: string;
  value?: string;
  classname?: string;
}

const LockedInput = ({ label, placeholder, value, classname }: LockedInputProps) => {
  return (
    <div className={classname}>
      <div className="mb-2 text-sm md:text-base">{label}</div>
        <div className="border border-gray-300 bg-gray-50 rounded-lg outline-none w-full flex flex-col gap-y-2 min-h-10 md:min-h-12 p-1">
          {value ? (
            <div className="flex justify-between rounded-lg items-center text-xs md:text-sm shadow-sm border select-none gap-x-2 bg-white p-2">
              <IconCircleCheckFilled className="text-green-600 translate-y-[1px] hidden md:block" size={20}/>
              <IconCircleCheckFilled className="text-green-600 md:hidden" size={18}/>
              <div className="flex-1">{value}</div>
            </div>
          ) : (
            <div className="text-gray-400 items-center text-sm md:text-base justify-center flex-1 flex">
              {placeholder}
            </div>
          )}
      </div>
    </div>
  );
};

export default LockedInput;