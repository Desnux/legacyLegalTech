import classNames from "classnames";
import { IconExternalLink } from "@tabler/icons-react";
import { Spinner } from "@/components/state";

export interface GoodsGroup {
  sources?: { source: string, url: string}[];
  source: string;
  url: string;
  headers: string[];
  values: string[][];
}

interface GoodsTableProps {
  className?: string;
  goods: GoodsGroup[];
  loading?: boolean;
}

const GoodsTable = ({ className, goods, loading = false }: GoodsTableProps) => {
  if (loading) {
    return (
      <div className={classNames("flex flex-col min-h-32 text-xs md:text-sm p-2 border rounded-lg border-gray-300", className)}>
        <Spinner className="flex-1 w-full h-full"/>
      </div>
    );
  }

  if (goods.length === 0) {
    return (
      <div className={classNames("flex flex-col min-h-32 text-xs md:text-sm p-2 border rounded-lg border-gray-300", className)}>
        <div className="flex-1 text-gray-600 flex justify-center text-sm md:text-base items-center text-center p-8">
          No se encontraron bienes asociados a la entidad solicitada.
        </div>
      </div>
    );
  }

  return (
    <div className={classNames("text-xs md:text-sm px-2 md:px-4 pb-2 md:pb-4 pt-1 md:pt-2 border rounded-lg border-gray-300", className)}>
      <div className="space-y-6">
        {goods.map((group, index) => (
          <div
            key={index}
            className=""
          >
            <div className="overflow-x-auto">
              <table className="min-w-full border-collapse">
                <thead>
                  <tr className="text-gray-900">
                    {group.headers.map((header, i) => (
                      <th
                        key={i}
                        className="px-2 py-2.5 border-b border-gray-400 text-left font-semibold"
                      >
                        {header}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {group.values.map((row, i) => (
                    <tr
                      key={i}
                      className={classNames(
                        "text-gray-700",
                        i % 2 === 0 ? "bg-gray-50" : "bg-white"
                      )}
                    >
                      {row.map((value, j) => (
                        <td
                          key={j}
                          className="px-2 py-2.5 border-b border-gray-200"
                        >
                          {value}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            { (group.sources || []).length === 0 && (
              <div className="ml-2 mt-2 text-xs md:text-sm flex gap-x-1">
                <div className="font-semibold text-gray-600">Fuente: <span className="italic">{group.source}</span></div>
                <a
                  href={group.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:text-blue-500"
                >
                  <IconExternalLink className="hidden md:block" size={20}/>
                  <IconExternalLink className="md:hidden" size={16}/>
                </a>
              </div>
            )}
            { group.sources && (
              <div className="ml-2 mt-2 text-xs md:text-sm flex gap-x-1">
                <div className="font-semibold text-gray-600">Fuentes:</div>
                {group.sources.map((row, i) => (
                  <div className="flex gap-x-1" key={i}>
                    {i !== 0 && <span>|</span>}
                    <span className="italic">{row.source}</span>
                    <a
                      href={row.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:text-blue-500"
                    >
                      <IconExternalLink className="hidden md:block" size={20}/>
                      <IconExternalLink className="md:hidden" size={16}/>
                    </a>
                  </div>
                ))}

              </div>
            )}
            
          </div>
        ))}
      </div>
    </div>
  );
};

export default GoodsTable;
