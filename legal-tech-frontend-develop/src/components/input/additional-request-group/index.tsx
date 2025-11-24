import { useState } from "react";
import classNames from "classnames";
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
import { IconPlus } from "@tabler/icons-react";
import { AdditionalRequestInput } from "@/components/input";
import { Request } from "@/types/request";

const SortableItem = ({ id, label, text, onClose, index, active = false }: Request & { onClose: () => void, index: number, active?: boolean }) => {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
  } = useSortable({ id });
  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
  };

  return (
    <AdditionalRequestInput 
      className={active ? "opacity-0" : undefined}
      label={label}
      text={text}
      ref={setNodeRef}
      style={style}
      draggableAttributes={attributes}
      listenerAttributes={listeners}
      onClose={onClose}
      index={index}
    />
  );
};

interface AdditionalRequestGroupProps {
  requests: Request[];
  setRequests: (requests: Request[]) => void;
  className?: string;
  label?: string;
  onAdd?: () => void;
}

const AdditionalRequestGroup = ({ label, requests, setRequests, className, onAdd }: AdditionalRequestGroupProps) => {
  const [activeItem, setActiveItem] = useState<Request | null>(null);
  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates }),
  );

  const handleDragStart = (event: DragStartEvent) => {
    const { active } = event;
    setActiveItem(requests.find(({ id }) => id === active.id) || null);
  };
  
  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;
    if (active.id !== over?.id) {
      const oldIndex = requests.findIndex(({ id }) => id === active.id);
      const newIndex = requests.findIndex(({ id }) => id === over?.id);
      setRequests(arrayMove(requests, oldIndex, newIndex));
    }
    setActiveItem(null);
  };

  const handleRemoveRequest = (index: number) => {
    setRequests([...requests.slice(0, index), ...requests.slice(index + 1)]);
  };

  return (
    <div className={classNames("flex flex-col", className)}>
      { label && onAdd === undefined && <label className="block text-sm md:text-base mb-2">{label}</label>}
      { label && onAdd !== undefined && (
        <div className="flex gap-x-1 justify-between items-end mb-2">
          <label className="block text-sm md:text-base">{label}</label>
          <div 
            onClick={onAdd}
            className="group flex items-center px-3 py-2 text-pure-white cursor-pointer bg-teal-green rounded-lg hover:bg-teal-green/90 transition-all duration-200 shadow-sm hover:shadow-md"
          >
            <div className="text-xs opacity-0 group-hover:opacity-100 w-0 h-0 overflow-hidden group-hover:mr-2 group-hover:w-auto group-hover:h-auto transition-all duration-300">Agregar</div>
            <IconPlus className="hidden md:block" size={18}/>
            <IconPlus className="md:hidden" size={16}/>
          </div>
        </div>
      )}
      <div className="flex flex-col bg-gray-50 p-1 rounded-lg border border-gray-300 gap-y-2 min-h-12">
        <DndContext
          id="additional-request-group"
          sensors={sensors}
          collisionDetection={closestCenter}
          onDragStart={handleDragStart}
          onDragEnd={handleDragEnd}
        >
          <SortableContext 
            items={requests}
            strategy={verticalListSortingStrategy}
          >
            {requests.map((request, index) => (
              <SortableItem
                {...request}
                onClose={() => handleRemoveRequest(index)}
                key={request.id}
                index={index}
                active={activeItem?.id === request.id}
              />
            ))}
          </SortableContext>
          <DragOverlay>
            {activeItem 
              ? <AdditionalRequestInput 
                  {...activeItem}
                  index={requests.findIndex(({ id }) => id === activeItem.id)}
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

export default AdditionalRequestGroup;
