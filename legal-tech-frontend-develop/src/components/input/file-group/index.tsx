import { useRef, useState } from "react";
import classNames from "classnames";
import { v4 as uuidv4 } from "uuid";
import {
  closestCenter,
  DndContext, 
  DragOverlay,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  DragStartEvent,
  DragEndEvent,
} from "@dnd-kit/core";
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  verticalListSortingStrategy,
  useSortable,
} from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import { IconGripVertical, IconPlus, IconUpload, IconX } from "@tabler/icons-react";
import { FileWithContext, FileType } from "@/types/file";
import Button from "@/components/button";

const FILE_TYPE_NAME: Record<FileType, string> = {
  "promissory_note": "Pagaré",
  "bill": "Factura",
  "bond": "Fianza",
  "response": "Respuesta",
};

interface SortableFileItemProps {
  fileWithContext: FileWithContext,
  index: number,
  onClose?: () => void;
  handleContextChange?: (index: number, context: string) => void;
  onTypeChange?: (index: number, newType: FileType) => void;
  className?: string;
  grabbed?: boolean;
  active?: boolean;
  type?: "response" | "demand";
}

const SortableFileItem = (
  { fileWithContext, index, handleContextChange, onTypeChange, className, onClose, grabbed = false, active = false, type = "demand" }: SortableFileItemProps
) => {
  const { attributes, listeners, setNodeRef, transform, transition } = useSortable({
    id: fileWithContext.id,
  });
  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
  };

  return (
    <div
      ref={setNodeRef}
      style={style}
      className={classNames(
        "flex gap-x-2 rounded-lg text-xs md:text-sm shadow-sm border bg-white p-2",
        className,
        { "cursor-grabbing": grabbed, "opacity-0": active },
      )}
    >
      {grabbed ? (
        <div className="self-center cursor-grabbing">
          <IconGripVertical size={16} />
        </div>
      ) : (
        <div className="self-center cursor-grab" {...listeners} {...attributes}>
          <IconGripVertical size={16} />
        </div>
      )}
              <div className="flex gap-y-2 flex-col flex-1">
          <div className="flex flex-1 justify-between flex-nowrap items-start">
            <div className="flex-1 flex gap-x-1 flex-wrap">
              <div className="font-semibold">{index + 1}{"."}</div>
              {fileWithContext.file.name}
            </div>
            {onClose && (
  <Button
    variant="ghost"
    size="sm"
    onClick={onClose}
    className="ml-1 p-1"
  >
    <IconX size={16} />
  </Button>
)}
          </div>
          {type === "demand" && (
            <div className="flex flex-wrap items-end gap-2 p-1 rounded-lg">
              <div className="flex gap-2">
                {(["promissory_note", "bill"] as FileType[]).map((fileType) => (
                  <div
                    key={fileType}
                    className={classNames(
                      "text-xs text-pure-white rounded-md py-1 px-2 flex font-semibold items-center cursor-pointer transition-colors duration-200",
                      {
                        "bg-teal-green hover:bg-teal-green/90": fileWithContext.fileType === fileType,
                        "bg-medium-gray hover:bg-medium-gray/80": fileWithContext.fileType !== fileType,
                      }
                    )}
                    onClick={onTypeChange ? () => onTypeChange(index, fileType) : undefined}
                  >
                    {FILE_TYPE_NAME[fileType]}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
    </div>
  );
};

interface FileGroupProps {
  filesWithContext: FileWithContext[],
  label?: string;
  className?: string;
  setFilesWithContext: (filesWithContext: FileWithContext[]) => void;
  accept?: string;
  type?: "response" | "demand";
}

const FileGroup = ({ label = "Archivos", className, filesWithContext, setFilesWithContext, accept = "*/*", type = "demand" }: FileGroupProps) => {
  const [activeItem, setActiveItem] = useState<FileWithContext | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates }),
  );

  const handleFileDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
    
    if (type === "response" && filesWithContext.length >= 1) {
      return;
    }
    
    const droppedData = e.dataTransfer.getData('application/json');
    if (droppedData) {
      try {
        const droppedFiles: FileWithContext[] = JSON.parse(droppedData);
        const newFiles: FileWithContext[] = droppedFiles.map((fileWithContext) => ({
          ...fileWithContext,
          id: uuidv4(),
        }));
        
        const filesToAdd = type === "response" ? newFiles.slice(0, 1) : newFiles;
        setFilesWithContext([...filesWithContext, ...filesToAdd]);
        return;
      } catch (error) {
      }
    }
    
    const selectedFiles = Array.from(e.dataTransfer.files).filter((file) => file.type === accept);

    if (selectedFiles) {
      const newFiles: FileWithContext[] = selectedFiles.map((file) => {
        let fileType: FileType = type === "demand" ? "promissory_note" : "response";
        let context = type === "demand" ? "PAGARÉ" : "RESPUESTA";
        
        return {
          id: uuidv4(),
          file,
          context,
          promissory_number: 0,
          fileType,
        };
      });

      const filesToAdd = type === "response" ? newFiles.slice(0, 1) : newFiles;
      setFilesWithContext([...filesWithContext, ...filesToAdd]);
    }
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();

    if (!isDragging) {
      setIsDragging(true);
    }
  };

  const handleDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();

    if (e.relatedTarget && e.currentTarget.contains(e.relatedTarget as Node)) {
      return;
    }

    setIsDragging(false);
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = event.target.files;
    
    if (type === "response" && filesWithContext.length >= 1) {
      return;
    }
    
    if (selectedFiles) {
      const newFiles: FileWithContext[] = Array.from(selectedFiles).map((file) => {
        let fileType: FileType = type === "demand" ? "promissory_note" : "response";
        let context = type === "demand" ? "PAGARÉ" : "RESPUESTA";
        
        return {
          id: uuidv4(),
          file,
          context,
          promissory_number: 0,
          fileType,
        };
      });

      const filesToAdd = type === "response" ? newFiles.slice(0, 1) : newFiles;
      setFilesWithContext([...filesWithContext, ...filesToAdd]);
    }
  };

  const handleContextChange = (index: number, newContext: string) => {
    setFilesWithContext(filesWithContext.map((fileWithContext, i) =>
      i === index ? { ...fileWithContext, context: newContext } : fileWithContext
    ));
  };

  const handleTypeChange = (index: number, newType: FileType) => {
    setFilesWithContext(filesWithContext.map((fileWithContext, i) =>
      i === index ? { 
        ...fileWithContext, 
        fileType: newType,
        context: FILE_TYPE_NAME[newType].toUpperCase()
      } : fileWithContext
    ));
  };  

  const handleDragStart = (event: DragStartEvent) => {
    const { active } = event;
    setActiveItem(filesWithContext.find(({ id }) => id === active.id) || null);
  };

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;
    if (active.id !== over?.id) {
      const oldIndex = filesWithContext.findIndex(({ id }) => id === active.id);
      const newIndex = filesWithContext.findIndex(({ id }) => id === over?.id);
      setFilesWithContext(arrayMove(filesWithContext, oldIndex, newIndex));
    }
    setActiveItem(null);
  };

  const handleRemoveFile = (index: number) => {
    setFilesWithContext([...filesWithContext.slice(0, index), ...filesWithContext.slice(index + 1)]);
  };

  const handleFileUploadClick = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  return (
    <div className={classNames(className)}>
      <div className="flex gap-x-1 justify-between items-end mb-2">
        <label htmlFor="file-upload" className="block cursor-pointer text-sm md:text-base">
          {label}
        </label>
        {/* Ocultar el botón de agregar si es tipo response y ya hay un archivo */}
        {!(type === "response" && filesWithContext.length >= 1) && (
          <div 
            onClick={handleFileUploadClick}
            className="group flex items-center px-3 py-2 text-pure-white cursor-pointer bg-teal-green rounded-lg hover:bg-teal-green/90 transition-all duration-200 shadow-sm hover:shadow-md"
          >
            <div className="text-xs opacity-0 group-hover:opacity-100 w-0 h-0 overflow-hidden group-hover:mr-2 group-hover:w-auto group-hover:h-auto transition-all duration-300">Agregar</div>
            <IconPlus className="hidden md:block" size={18}/>
            <IconPlus className="md:hidden" size={16}/>
          </div>
        )}
        <input
          id="file-upload"
          type="file"
          ref={fileInputRef}
          className="hidden"
          multiple={type !== "response"}
          onChange={handleFileChange}
          accept={accept}
        />
      </div>
      <div 
        className={classNames(
          `flex flex-col p-1 rounded-lg border gap-y-2 min-h-20 ${filesWithContext.length === 0 ? 'cursor-pointer' : ''}`,
          { "border-teal-green bg-light-gray": isDragging },
          { "border-medium-gray bg-pure-white": !isDragging },
        )}
        onDragOver={type === "response" && filesWithContext.length >= 1 ? undefined : handleDragOver}
        onDragLeave={type === "response" && filesWithContext.length >= 1 ? undefined : handleDragLeave}
        onDrop={type === "response" && filesWithContext.length >= 1 ? undefined : handleFileDrop}
        onClick={filesWithContext.length === 0 ? handleFileUploadClick : undefined}
      >
        <DndContext
          id="file-group"
          sensors={sensors}
          collisionDetection={closestCenter}
          onDragStart={handleDragStart}
          onDragEnd={handleDragEnd}
        >
          <SortableContext
            items={filesWithContext}
            strategy={verticalListSortingStrategy}
          >
            {filesWithContext.map((fileWithContext, index) => (
              <SortableFileItem
                key={fileWithContext.id}
                fileWithContext={fileWithContext}
                index={index}
                handleContextChange={handleContextChange}
                onTypeChange={handleTypeChange}
                onClose={() => handleRemoveFile(index)}
                active={activeItem?.id === fileWithContext.id}
                type={type}
              />
            ))}
            {filesWithContext.length === 0 && (
              <div className={classNames(
                "items-center justify-center flex-1 flex",
                { "text-teal-green": isDragging },
                { "text-medium-gray": !isDragging },
              )}>
                <IconUpload className="hidden md:block" size={24}/>
                <IconUpload className="md:hidden" size={20}/>
              </div>
            )}
          </SortableContext>
          <DragOverlay>
            {activeItem 
              ? <SortableFileItem
                  fileWithContext={activeItem}
                  index={filesWithContext.findIndex(({ id }) => id === activeItem.id)}
                  className="bg-white"
                  grabbed
                  type={type}
                />
              : null
            }
          </DragOverlay>
        </DndContext>
      </div>
    </div>
  );
};

export default FileGroup;
