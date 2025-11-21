import { useState } from "react";
import classNames from "classnames";
import { ButtonPrimary } from "@/components/button";
import { GoodsGroup, GoodsTable } from "@/components/output";
import { exampleData } from "@/components/extractor/demand-text-input/exampleData";

interface DataSearcherProps {
  className?: string;
  label?: string;
  onIncorporate?: (content: string) => void;
}

const DataSearcher = ({ className, label = "Bienes extraídos", onIncorporate }: DataSearcherProps) => {
  const [goodsQuery, setGoodsQuery] = useState<string>("");
  const [goodsResult, setGoodsResult] = useState<GoodsGroup[]>([]);
  const [loading, setLoading] = useState<boolean | null>(null);

  const handleSearch = async () => {
    const normalize = (text: string) =>
      text
        .toLowerCase()
        .replace(/[.\-\s]/g, "")
        .normalize("NFD")
        .replace(/[\u0300-\u036f]/g, "");
  
    setLoading(true);
    await new Promise((resolve) => setTimeout(resolve, 500));
  
    const query = normalize(goodsQuery);
  
    const entity = exampleData.find((e) => {
      const normName = normalize(e.name);
      const normRut = normalize(e.rut);
      return query === normName || query === normRut;
    });
    setGoodsResult((entity?.bienes ?? []) as GoodsGroup[]);
    setLoading(false);
  };


  const handleIncorporate = () => {
    if (onIncorporate === undefined) {
      return;
    }
    let content: string[] = [];
    let participation: string[] = [];

    const normalize = (text: string) =>
      text
        .toLowerCase()
        .replace(/[.\-\s]/g, "")
        .normalize("NFD")
        .replace(/[\u0300-\u036f]/g, "");

    const query = normalize(goodsQuery);
    const entity = exampleData.find((e) => {
      const normName = normalize(e.name);
      const normRut = normalize(e.rut);
      return query === normName || query === normRut;
    });

    if (entity?.type === "PERSONA") {
      content.push(`Bienes de ${entity.name}:`);
    }

    goodsResult.forEach((group) => {
      if (group.source.startsWith("Conservador")) {
        group.values.forEach((row) => {
          content.push(`- El inmueble inscrito a fojas ${row[0]} Nº ${row[1]} del Registro de Propiedad del Conservador de Bienes Raíces de Santiago del año ${row[2]}.`)
        });
      } else if (group.source.startsWith("Volante")) {
        group.values.forEach((row) => {
          const marcaText = row[2] !== "Sin Datos" ? ` marca ${row[2]}` : "";
          const modeloText = row[3] !== "Sin Datos" ? ` modelo ${row[3]}` : "";
          const anioText = row[5] !== "Sin Datos" ? ` del año ${row[5]}` : "";
          const registradoText = row[6] !== "Sin Datos" ? ` registrado a nombre de ${row[6]}` : "";
          content.push(`- ${row[1] !== "Sin Datos" ? row[1] : "Vehículo"}${marcaText}${modeloText}, patente ${row[0]}${anioText}${registradoText}.`);
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
    <div className={classNames("flex flex-col gap-2", className)}>
      <div className="block text-sm md:text-base">{ label }</div>
      {loading !== null && <GoodsTable goods={goodsResult} loading={loading}/>}
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
        <ButtonPrimary
          disabled={loading || goodsQuery.trim().length === 0}
          label="Buscar"
          onClick={handleSearch}
        />
      </div>
      <p className="mt-1 text-xs md:text-sm text-gray-500">
        Presione para buscar posibles bienes de los demandados, extraídos desde sitios web públicos.
      </p>
    </div>
  );
};

export default DataSearcher;
