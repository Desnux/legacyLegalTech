import React, { useRef, useState } from "react";
import classNames from "classnames";
import { IconPlus, IconX, IconChevronDown } from "@tabler/icons-react";
import { ButtonPrimary } from "@/components/button";
import { GoodsGroup, GoodsTable } from "@/components/output";

const sampleGoods = [
  {
    source: "Conservadores Digitales",
    url: "https://conservadoresdigitales.cl/conservador/santiago/consultas-en-linea/indice-de-propiedad",
    headers: ["Foja", "Número", "Año", "Dirección"],
    values: [
      ["28278", "37594", "1981", "Calle A 1950"],
      ["2284", "1556", "1998", "Pablo Burchard 1940"],
    ],
  },
  {
    source: "deQuiénes",
    url: "https://dequienes.cl/",
    headers: ["Empresa", "RUT", "Socio"],
    values: [
      ["BERZINS Y PIZARRO LIMITADA", "77.437.070-6", "Sí"],
      ["COMERCIAL PIZARRO Y COMPANIA LIMITADA", "77.031.800-9", "Sí"],
      ["COMERCIAL TRANSAMERICA LIMITADA", "77.406.150-9", "Sí"],
      ["SOC COMERCIAL PROSPER STORES LIMITADA", "77.809.230-1", "Sí"],
      ["SOCIEDAD DE INVERSIONES PIZARRO E HIJOS S.A", "77.809.030-9", "Sí"],
    ],
  },
  {
    source: "CMF",
    url: "https://www.cmfchile.cl/",
    headers: ["Razón Social", "RUT", "Acciones (%)"],
    values: [
      ["LIGA INDEPENDIENTE DE FUTBOL S.A.", "94.514.000-3", "<1"],
    ]
  }
];

const societyGoods = [
  {
    source: "Volante o Maleta",
    sources: [
      { source: "Registro de vehículos motorizados", url: "https://www.registrosciviles.cl/tramites/registro-de-vehiculos-motorizados/" },
      { source: "Volante o Maleta", url: "https://www.volanteomaleta.com/" },
    ],
    url: "https://www.volanteomaleta.com/",
    headers: ["Patente", "Tipo", "Marca", "Modelo", "Nro. Motor", "Año", "Nombre a Rutificador"],
    values: [
      ["KRKG72", "Camion", "Chevrolet", "NQR 919", "4HK1681283", "2018", "Via Uno Chile Spa"],
    ],
  },
]

const DollarCertificate = ({
  label,
  register,
  setValue,
  watch,
  errors,
  onIncorporate,
}: {
  label: string;
  register: any;
  setValue: any;
  watch: any;
  errors: any;
  onIncorporate?: (content: string) => void;
}) => {
  const [isCollapsed, setIsCollapsed] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [goodsQuery, setGoodsQuery] = useState<string>("");
  const [goodsResult, setGoodsResult] = useState<GoodsGroup[]>([]);
  const [loading, setLoading] = useState<boolean | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const currentFile = watch("dollarCertificate");

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];

    if (file) {
      if (file.type !== "application/pdf") {
        setError("Solo se permiten archivos en formato PDF.");
        return;
      }
      setValue("dollarCertificate", file);
      setError(null);
    } else {
      setValue("dollarCertificate", null);
    }

    event.target.value = ""; // Restablece el valor del input para evitar problemas al volver a agregar el mismo archivo
  };

  const handleRemoveFile = () => {
    setValue("dollarCertificate", null);
  };

  const handleFileUploadClick = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  const toggleCollapse = () => {
    setIsCollapsed(!isCollapsed);
  };

  const handleSearch = async () => {
    setLoading(true);
    await new Promise((resolve) => setTimeout(resolve, 2000));
    if (goodsQuery.trim().toLowerCase().includes("pizarro corral")) {
      setGoodsResult(sampleGoods);
    } else if (goodsQuery.trim().replaceAll(".", "").replaceAll("-", "") == "66470563") {
      setGoodsResult(sampleGoods);
    } else if (goodsQuery.trim().toLowerCase().includes("via uno")) {
      setGoodsResult(societyGoods);
    } else if (goodsQuery.trim().replaceAll(".", "").replaceAll("-", "") == "760557498") {
      setGoodsResult(societyGoods);
    } else {
      setGoodsResult([]);
    }
    setLoading(false);
  }

  const handleIncorporate = () => {
    if (onIncorporate === undefined) {
      return;
    }
    let content: string[] = [];
    let participation: string[] = [];
    if (goodsQuery.trim().toLowerCase().includes("pizarro corral") || goodsQuery.trim().replaceAll(".", "").replaceAll("-", "") == "66470563") {
      content.push("Además los siguientes bienes de propiedad del representante legal FELIPE FERNANDO PIZARRO CORRAL:");
    }
    goodsResult.forEach((group) => {
      if (group.source.startsWith("Conservadores")) {
        group.values.forEach((row) => {
          content.push(`- El inmueble inscrito a fojas ${row[0]} Nº ${row[1]} del Registro de Propiedad del Conservador de Bienes Raíces de Santiago del año ${row[2]}.`)
        });
      } else if (group.source.startsWith("Volante")) {
        group.values.forEach((row) => {
          content.push(`- ${row[1]} marca ${row[2]} modelo ${row[3]}, patente ${row[0]}, del año ${row[5]} registrado a nombre de ${row[6]}.`)
        });
      } else if (group.source.startsWith("deQuiénes")) {
        group.values.forEach((row) => {
          participation.push(`${row[0]}, RUT Nº ${row[1]}`)
        });
      } else if (group.source.startsWith("CMF")) {
        group.values.forEach((row) => {
          participation.push(`${row[0]}, RUT Nº ${row[1]}`)
        });
      }
    })
    if (participation.length > 0) {
      content.push("- La participación accionaria o derechos en las siguientes sociedades: " + participation.join("; ") + ".");
    }
    onIncorporate(content.join("\n"));
    setGoodsQuery("");
    setGoodsResult([]);
    setLoading(null);
  };

  return (
    <div className="border border-gray-300 rounded-md md:rounded-lg p-4">
      {/* Header */}
      <div
        className="flex justify-between items-center cursor-pointer"
        onClick={toggleCollapse}
      >
        <h3 className="text-sm flex gap-x-2 items-center md:text-base">Información opcional</h3>
        <IconChevronDown
          size={20}
          className={classNames("transition-transform", {
            "rotate-180": !isCollapsed,
          })}
        />
      </div>

      {/* Collapsible content */}
      {!isCollapsed && (
        <div className="border-t border-gray-300 mt-4 pt-4 flex flex-col gap-2">
          <div className="flex flex-col gap-2">
            {/* Header with upload button */}
            <div className="flex justify-between items-center">
              <label htmlFor="file-upload" className="block cursor-pointer text-sm md:text-base">
                {label}
              </label>
              <div
                onClick={handleFileUploadClick}
                className="group flex items-center px-2 py-1 text-white cursor-pointer bg-blue-600 rounded-l-full rounded-r-full hover:bg-blue-500"
              >
                <div className="text-xs opacity-0 group-hover:opacity-100 w-0 h-0 overflow-hidden group-hover:mr-2 group-hover:w-auto group-hover:h-auto transition-all duration-300">
                  Agregar
                </div>
                <IconPlus size={18} />
              </div>
              <input
                id="dollarCertificate"
                type="file"
                ref={fileInputRef}
                className="hidden"
                accept="application/pdf"
                onChange={handleFileUpload}
              />
            </div>

            {/* File preview or empty state */}
            <div
              className={classNames(
                "flex items-center gap-2 p-2 border rounded-lg bg-gray-50",
                { "border-red-500": error },
                { "border-gray-300": !error }
              )}
            >
              {currentFile ? (
                <>
                  <span className="flex-grow text-xs md:text-sm">{currentFile.name}</span>
                  <button
                    onClick={handleRemoveFile}
                    className="text-gray-500 hover:text-gray-700"
                  >
                    <IconX size={16} />
                  </button>
                </>
              ) : (
                <span className="text-gray-400 text-xs md:text-sm">
                  No se ha seleccionado ningún archivo
                </span>
              )}
            </div>

            {/* Error message */}
            {error && <p className="text-xs md:text-sm text-red-600">{error}</p>}
            <p className="mt-1 text-xs md:text-sm text-gray-500">
              Adjunte un archivo PDF que respalde los cálculos si hay montos en
              USD.
            </p>
          </div>

          {/* TODO: Remove */}
          <div className="flex flex-col gap-2 border-t border-gray-300 pt-6 mt-4">
            <div className="block text-sm md:text-base">
              Bienes extraídos
            </div>

            {loading !== null && (
              <GoodsTable goods={goodsResult} loading={loading}/>
            )}

            <div className="flex gap-x-2 text-xs md:text-sm">
              <input
                value={goodsQuery}
                maxLength={64}
                autoComplete="off"
                type="text"
                disabled={loading === true}
                placeholder="Nombre o RUT"
                className={classNames("p-2 border rounded-lg outline-none bg-gray-50 flex-1 border-gray-300")}
                onChange={(e) => setGoodsQuery(e.target.value)}
              />
              <ButtonPrimary
                disabled={loading || goodsResult.length === 0}
                className={classNames("text-left w-min", (loading || goodsResult.length === 0) && "hidden")}
                label="Incorporar"
                onClick={handleIncorporate}
              />
              <ButtonPrimary disabled={loading || goodsQuery.trim().length === 0} className="text-left w-min" label="Buscar" onClick={handleSearch}/>
            </div>
            <p className="mt-1 text-xs md:text-sm text-gray-500">
              Presione para buscar posibles bienes de los demandados, extraídos desde sitios web públicos.
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default DollarCertificate;
