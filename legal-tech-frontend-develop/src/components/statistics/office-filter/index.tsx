import { IconFilter } from "@tabler/icons-react";

type LawyerOfficeFilter = 'all' | 'IFBL Abogados' | 'Braun y Asociados';

interface OfficeFilterProps {
  activeFilter: LawyerOfficeFilter;
  onFilterChange: (filter: LawyerOfficeFilter) => void;
}

export default function OfficeFilter({ activeFilter, onFilterChange }: OfficeFilterProps) {
  const filters: { value: LawyerOfficeFilter; label: string }[] = [
    { value: 'all', label: 'Todas las oficinas' },
    { value: 'IFBL Abogados', label: 'IFBL Abogados' },
    { value: 'Braun y Asociados', label: 'Braun y Asociados' }
  ];

  return (
    <div className="mb-6 bg-white p-2 rounded-xl shadow-md flex justify-center">
      <div className="bg-light-gray rounded-xl p-1 inline-flex">
        {filters.map((filter) => (
          <button
            key={filter.value}
            onClick={() => onFilterChange(filter.value)}
            className={`
              px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200
              ${activeFilter === filter.value
                ? 'bg-pure-white text-teal-green shadow-sm'
                : 'text-medium-gray hover:text-charcoal-gray'
              }
            `}
          >
            {filter.label}
          </button>
        ))}
      </div>
    </div>
  );
} 