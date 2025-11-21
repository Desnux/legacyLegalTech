import React, { useState, useRef } from "react";
import classNames from "classnames";
import { v4 as uuidv4 } from "uuid";
import {
  DndContext,
  DragOverlay,
  closestCenter,
  useSensor,
  useSensors,
  PointerSensor,
  KeyboardSensor,
  DragStartEvent,
  DragEndEvent,
} from "@dnd-kit/core";
import {
  SortableContext,
  arrayMove,
  sortableKeyboardCoordinates,
  useSortable,
  verticalListSortingStrategy,
} from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import { IconPlus, IconX, IconGripVertical, IconUpload } from "@tabler/icons-react";

export interface FileItem {
  id: string;
  file: File;
  name: string;
}

interface FileExtraProps {
  name: string;
  label?: string;
  filesWithContext: FileItem[];
  setFilesWithContext: (filesWithContext: FileItem[]) => void;
  accept?: string;
}

const maxFiles = 10;

const SortableFileItem = ({ fileItem, index, onRemove, onNameChange, grabbed, active }: any) => {
  const { attributes, listeners, setNodeRef, transform, transition } = useSortable({
    id: fileItem.id,
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
        "flex gap-2 items-center rounded-lg p-2 border bg-white shadow-sm",
        { "cursor-grabbing": grabbed, "opacity-0": active },
      )}
    >
      <div className="cursor-grab" {...listeners} {...attributes}>
        <IconGripVertical size={16} />
      </div>
      <div className="flex flex-col flex-grow">
        <input
          type="text"
          value={fileItem.name}
          onChange={(e) => onNameChange(fileItem.id, e.target.value)}
          className="outline-none text-sm border-b"
          placeholder="Nombre del archivo"
        />
      </div>
      <button
        onClick={() => onRemove(fileItem.id)}
        className="text-gray-500 hover:text-gray-700"
      >
        <IconX size={16} />
      </button>
    </div>
  );
};

const FileExtra: React.FC<FileExtraProps> = ({
  label = "Archivos",
  filesWithContext,
  setFilesWithContext,
  accept = "application/pdf",
}) => {
  const [activeItem, setActiveItem] = useState<FileItem | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates })
  );

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (!event.target.files) return;

    const selectedFiles = Array.from(event.target.files).filter(
      (file) => file.type === accept
    );

    // Verifica si excede el límite de 10 archivos
    if (filesWithContext.length + selectedFiles.length > maxFiles) {
      setError(`No puedes adjuntar más de ${maxFiles} archivos.`);
      return;
    }

    const newFiles: FileItem[] = selectedFiles.map((file) => ({
      id: uuidv4(),
      file,
      name: file.name.replace(/\.[^/.]+$/, ""),
    }));

    setFilesWithContext([...filesWithContext, ...newFiles]);
    event.target.value = ""; // Restablece el valor del input para evitar problemas al volver a agregar el mismo archivo
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

  const handleRemoveFile = (id: string) => {
    setFilesWithContext(filesWithContext.filter((file) => file.id !== id));
    setError(null);
  };

  const handleNameChange = (id: string, newName: string) => {
    const nameExists = filesWithContext.some(
      (file) => file.name === newName && file.id !== id
    );
  
    if (nameExists) {
      setError(`El nombre "${newName}" ya existe, por favor elige otro.`);
      return;
    }
  
    setError(null); // Limpia el error si no hay problema
    setFilesWithContext(
      filesWithContext.map((file) =>
        file.id === id ? { ...file, name: newName } : file
      )
    );
  };
  
  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      e.preventDefault(); // Evita el comportamiento predeterminado de ENTER
    }
  };

  const handleFileDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
    
    const selectedFiles = Array.from(e.dataTransfer.files).filter((file) => file.type === accept);
    if (filesWithContext.length + selectedFiles.length > maxFiles) {
      setError(`No puedes adjuntar más de ${maxFiles} archivos.`);
      return;
    }

    const newFiles: FileItem[] = selectedFiles.map((file) => ({
      id: uuidv4(),
      file,
      name: file.name.replace(/\.[^/.]+$/, ""),
    }));

    setFilesWithContext([...filesWithContext, ...newFiles]);
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
  
  const handleFileUploadClick = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  return (
    <div className="file-group" onKeyDown={handleKeyDown}>
      <div className="flex justify-between items-center mb-2">
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
          type="file"
          ref={fileInputRef}
          className="hidden"
          multiple
          accept={accept}
          onChange={handleFileUpload}
        />
      </div>
      <div 
        className={classNames(
          "flex flex-col p-1 rounded-lg border gap-y-2 min-h-10 md:min-h-12",
          { "border-blue-600 bg-blue-100": isDragging },
          { "border-gray-300 bg-gray-50": !isDragging },
          { "cursor-pointer": filesWithContext.length === 0 },
        )}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleFileDrop}
        onClick={(filesWithContext.length === 0) ? handleFileUploadClick : undefined}
      >
        <DndContext
          sensors={sensors}
          collisionDetection={closestCenter}
          onDragStart={handleDragStart}
          onDragEnd={handleDragEnd}
        >
          <SortableContext
            items={filesWithContext}
            strategy={verticalListSortingStrategy}
          >
            {error && <p className="text-red-500 text-sm">{error}</p>}
            {filesWithContext.length === 0 ? (
                <div className={classNames(
                    "items-center justify-center flex-1 flex",
                    { "text-blue-400": isDragging },
                    { "text-gray-400": !isDragging },
                )}>
                <IconUpload className="hidden md:block" size={24}/>
                <IconUpload className="md:hidden" size={20}/>
              </div>
            ) : (
                filesWithContext.map((fileItem, index) => (
                    <SortableFileItem
                    key={fileItem.id}
                    fileItem={fileItem}
                    index={index}
                    onRemove={handleRemoveFile}
                    onNameChange={handleNameChange}
                    grabbed={false}
                    active={activeItem?.id === fileItem.id}
                    />
                ))
            )}
          </SortableContext>
          <DragOverlay>
            {activeItem ? (
              <SortableFileItem
                fileItem={activeItem}
                index={-1}
                onRemove={() => {}}
                onNameChange={() => {}}
                grabbed
              />
            ) : null}
          </DragOverlay>
        </DndContext>
      </div>
    </div>
  );
};

export default FileExtra;
