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
import { IconGripVertical, IconPlus, IconUpload } from "@tabler/icons-react";
import { FileWithContext, FileType } from "@/types/file";
import { ButtonClose } from "@/components/button";

const FILE_TYPE_NAME: Record<FileType, string> = {
  "promissory_note": "Pagaré",
  "bill": "Factura",
  "bond": "Fianza",
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
}

const SortableFileItem = (
  { fileWithContext, index, handleContextChange, onTypeChange, className, onClose, grabbed = false, active = false }: SortableFileItemProps
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
          {onClose && <ButtonClose onClick={onClose} className="ml-1" size={16} />}
        </div>
        <div className="flex flex-wrap justify-between border border-gray-300 p-1 rounded-lg">
          <input
            type="text"
            value={fileWithContext.context}
            onChange={handleContextChange ? (e) => handleContextChange(index, e.target.value) : undefined}
            readOnly={handleContextChange === undefined}
            placeholder="Razón asociada a los demandados"
            className={classNames("outline-none text-xs flex-1 ml-0.5", { "cursor-grabbing": grabbed })}
          />
          {(["promissory_note", "bill"] as FileType[]).map((type) => (
            <div
              key={type}
              className={classNames(
                "ml-2 text-xs text-white rounded-l-md py-1 px-2 flex font-semibold items-center rounded-r-md cursor-pointer",
                {
                  "bg-blue-600 hover:bg-blue-500": fileWithContext.fileType === type,
                  "bg-gray-600 hover:bg-gray-500": fileWithContext.fileType !== type,
                }
              )}
              onClick={onTypeChange ? () => onTypeChange(index, type) : undefined}
            >
              {FILE_TYPE_NAME[type]}
            </div>
          ))}
        </div>
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
}

const FileGroup = ({ label = "Archivos", className, filesWithContext, setFilesWithContext, accept = "*/*", }: FileGroupProps) => {
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
    
    const selectedFiles = Array.from(e.dataTransfer.files).filter((file) => file.type === accept);

    if (selectedFiles) {
      const newFiles: FileWithContext[] = selectedFiles.map((file) => ({
        id: uuidv4(),
        file,
        context: "",
        fileType: "promissory_note",
      }));

      setFilesWithContext([...filesWithContext, ...newFiles]);
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

    if (selectedFiles) {
      const newFiles: FileWithContext[] = Array.from(selectedFiles).map((file) => ({
        id: uuidv4(),
        file,
        context: "",
        fileType: "promissory_note",
      }));

      setFilesWithContext([...filesWithContext, ...newFiles]);
    }
  };

  const handleContextChange = (index: number, newContext: string) => {
    setFilesWithContext(filesWithContext.map((fileWithContext, i) =>
      i === index ? { ...fileWithContext, context: newContext } : fileWithContext
    ));
  };

  const handleTypeChange = (index: number, newType: FileType) => {
    setFilesWithContext(filesWithContext.map((fileWithContext, i) =>
      i === index ? { ...fileWithContext, fileType: newType } : fileWithContext
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
        <div 
          onClick={handleFileUploadClick}
          className="group flex items-center px-2 py-1 text-white cursor-pointer bg-blue-600 rounded-l-full rounded-r-full hover:bg-blue-500"
        >
          <div className="text-xs opacity-0 group-hover:opacity-100 w-0 h-0 overflow-hidden group-hover:mr-2 group-hover:w-auto group-hover:h-auto transition-all duration-300">Agregar</div>
          <IconPlus className="hidden md:block" size={18}/>
          <IconPlus className="md:hidden" size={16}/>
        </div>
        <input
          id="file-upload"
          type="file"
          ref={fileInputRef}
          className="hidden"
          multiple
          onChange={handleFileChange}
          accept={accept}
        />
      </div>
      <div 
        className={classNames(
          "flex flex-col p-1 rounded-lg border gap-y-2 min-h-20",
          { "border-blue-600 bg-blue-100": isDragging },
          { "border-gray-300 bg-gray-50": !isDragging },
        )}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleFileDrop}
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
              />
            ))}
            {filesWithContext.length === 0 && (
              <div className={classNames(
                "items-center justify-center flex-1 flex",
                { "text-blue-400": isDragging },
                { "text-gray-400": !isDragging },
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
