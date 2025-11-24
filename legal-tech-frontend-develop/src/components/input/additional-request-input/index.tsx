import React, { forwardRef } from "react";
import classNames from "classnames";
import { IconGripVertical } from "@tabler/icons-react";
import { DraggableAttributes } from "@dnd-kit/core";
import { ButtonClose } from "@/components/button";

const INDEX_PREFIX = [
  "PRIMER",
  "SEGUNDO",
  "TERCER",
  "CUARTO",
  "QUINTO",
  "SEXTO",
  "SÉPTIMO",
  "OCTAVO",
  "NOVENO",
  "DÉCIMO",
]

interface AdditionalRequestInputProps {
  className?: string;
  label: string;
  text: string;
  index?: number;
  onClose?: () => void;
  style?: React.CSSProperties;
  draggableAttributes?: DraggableAttributes;
  listenerAttributes?: any;
  grabbed?: boolean;
}

const AdditionalRequestInput = forwardRef<HTMLDivElement, AdditionalRequestInputProps>(({ 
  label,
  text,
  index,
  onClose,
  className,
  style,
  draggableAttributes,
  listenerAttributes,
  grabbed = false,
}, ref) => {
  const indexClamped = index !== undefined ? Math.min(Math.max(0, index), 9) : -1;
  const formattedText = text.split("\n\n").map((paragraph, subIndex) => (
    <p key={subIndex} className="mb-1 last-of-type:mb-0">
      {paragraph.split("\n").map((line, i) => (
        <React.Fragment key={i}>
          {line}
          <br />
        </React.Fragment>
      ))}
    </p>
  ));

  return (
    <div className={classNames("flex gap-x-2 rounded-lg text-xs md:text-sm shadow-sm border bg-white p-2", className, { "cursor-grabbing": grabbed })} ref={ref} style={style}>
      { draggableAttributes && listenerAttributes ? (
        <div className="self-center cursor-grab" {...listenerAttributes} {...draggableAttributes}>
          <IconGripVertical size={16}/>
        </div>
      ) : (
        <div className="self-center cursor-grabbing">
          <IconGripVertical size={16}/>
        </div>
      )}
      <div className="flex gap-y-1 flex-col flex-1">
        <div className="flex flex-1 justify-between flex-nowrap items-start">
          <div className="flex flex-1 gap-x-1 flex-wrap">
            {index !== undefined && <div className="font-semibold">{INDEX_PREFIX[indexClamped]} OTROSÍ:</div>}
            {label.toUpperCase()}
          </div>
          { onClose && <ButtonClose onClick={onClose} className="ml-1" size={16}/>}
        </div>
        {text && <div className="flex-1 text-xs ml-0.5 text-gray-500">{formattedText}</div>}
      </div>
    </div>
  );
});

export default AdditionalRequestInput;
