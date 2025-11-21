"use client";

import React, { useState, useEffect } from "react";
import classNames from "classnames";
import { useForm } from "react-hook-form";
import { toast, ToastContainer } from "react-toastify";
import { IconExternalLink } from "@tabler/icons-react";
import { PasswordInput, RutInput } from "@/components/input";
import { FullPageOverlay } from "@/components/loading";
import { Demand, DemandResponse, fetchDemandList, sendDemand, deleteDemand } from "@/services/sender/demand-text-sender";
import { formatRut } from "@/utils/rut";

interface FormInputs {
  rut: string;
  password: string;
}

const DemandTextSender: React.FC = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [toastMessage, setToastMessage] = useState<string>("");
  const [refresh, setRefresh] = useState(false);
  const [rut, setRut] = useState('');
  const [password, setPassword] = useState('');
  const [authenticated, setAuthenticated] = useState(false);
  const [demandList, setDemandList] = useState<Demand[]>([]);

  const {
    register,
    setValue,
    handleSubmit,
    formState: { errors },
  } = useForm<FormInputs>();

  const handleStatusCode = (code: number, message: string, text: string) => {
    switch (code) {
      case 200:
        if (text) {
          toast.success(text);
        } else {
          toast.success(message);
        }
        setRefresh(true);
        setAuthenticated(true);
        break;
      default:
        toast.error(message);
        setAuthenticated(false);
        break;
    }
  }

  const handleSend = async (index: number) => {
    try {
      setToastMessage("Enviando demanda...");
      setIsLoading(true);
      const response: DemandResponse = await sendDemand(formatRut(rut), password, index);
      handleStatusCode(response.status, response.message, "Demanda enviada correctamente.");
    } catch (error) {
      toast.error("Error al enviar la demanda.");
    } finally {
      setIsLoading(false);
      setToastMessage("");
    }
  };

  const handleDelete = async (index: number) => {
    try {
      setToastMessage("Eliminando demanda...");
      setIsLoading(true);
      const response: DemandResponse = await deleteDemand(formatRut(rut), password, index);
      handleStatusCode(response.status, response.message, "Demanda eliminada correctamente.");
    } catch (error) {
      toast.error("Error al eliminar la demanda.");
    } finally {
      setIsLoading(false);
      setToastMessage("");
    }
  };

  const onSubmit = async (data: FormInputs) => {
    setRut(data.rut);
    setPassword(data.password);
    await getDemandList(data.rut, data.password);
  };

  const getDemandList = async (rut: string, password: string) => {
    try {
      setToastMessage("Solicitando información...");
      setIsLoading(true);
      const response = await fetchDemandList(formatRut(rut), password);
      console.log(response);
      handleStatusCode(response.status, response.message, "Demandas obtenidas.");

      if (response.data) {
        setDemandList(response.data);
      } else {
        setDemandList([]);
      }
    } catch (error) {
      console.log(error);
      // toast.error('Error al obtener la lista de demandas');
    } finally {
      setIsLoading(false);
      setRefresh(false);
      setToastMessage("");
    }
  };

  useEffect(() => {
    if (rut && password) {
      getDemandList(rut, password);
    }
  }, [refresh]);

  return (
    <div className="bg-white md:rounded-xl flex flex-col flex-1 w-full p-8 md:shadow-lg">
      <h1 className="text-lg md:text-xl font-semibold mb-2 md:mb-4">Bandeja de demandas</h1>
      {/* Lista de demandas */}
      {demandList.length > 0 && (
        <>
          <ul className="space-y-4 flex-1">
            {demandList.map((demand) => (
              <li
                key={demand.index}
                className="border rounded-lg py-2 px-3 flex flex-col md:flex-row justify-between shadow-sm bg-white"
              >
                {/* Contenido principal */}
                <div className="w-full flex flex-col md:flex-grow gap-y-2">
                  {/* Título y fecha */}
                  <div className="flex flex-col md:flex-row justify-between items-start md:items-center">
                    <h2 className="font-semibold uppercase text-sm md:text-base text-gray-800 w-full md:w-auto md:line-clamp-1">
                      {demand.title}
                    </h2>
                    <span className="text-xs md:text-sm text-gray-500 w-full md:w-auto md:text-right">
                      {new Date(demand.creation_date).toLocaleDateString()}
                    </span>
                  </div>
                  {/* Información adicional */}
                  <div className="flex flex-col md:flex-row justify-between items-start md:items-center text-xs md:text-sm text-gray-700">
                    <span className="capitalize w-full md:w-1/3 md:line-clamp-1">{demand.court}</span>
                    <span className="capitalize text-gray-500 w-full md:w-1/3 md:line-clamp-1 md:text-center">
                      {demand.legal_subject}
                    </span>
                    <span className="capitalize w-full md:w-1/3 md:line-clamp-1 md:text-right">
                      {demand.author}
                    </span>
                  </div>
                  {/* Botones */}
                  <div className="flex justify-center md:justify-end md:items-end mt-2 md:mt-4 space-x-3 w-full md:w-auto">
                    <button
                      className="bg-blue-600 text-white hover:bg-blue-500 px-4 py-2 rounded-md shadow-sm w-full md:w-[80px] text-sm"
                      onClick={() => handleSend(demand.index)}
                    >
                      Enviar
                    </button>
                    <button
                      className="bg-red-600 text-white hover:bg-red-500 px-4 py-2 rounded-md shadow-sm w-full md:w-[80px] text-sm"
                      onClick={() => handleDelete(demand.index)}
                    >
                      Eliminar
                    </button>
                  </div>
                </div>
              </li>
            ))}
          </ul>
          <a
            href="https://ojv.pjud.cl/kpitec-ojv-web/views/login.html#segunda"
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-600 hover:text-blue-500 underline text-sm md:text-base mt-4 flex items-center flex-nowrap gap-x-1"
          >
            <IconExternalLink className="hidden md:block" size={20}/>
            <IconExternalLink className="md:hidden" size={18}/>
            Editar manualmente
          </a>
        </>
      )}
      {demandList.length === 0 && authenticated && (
        <div className="flex-1 text-gray-600 flex justify-center text-sm md:text-base items-center text-center p-8">
          No hay demandas por enviar
        </div>
      )}

      <form onSubmit={handleSubmit(onSubmit)} className={classNames("mt-2 flex flex-col gap-y-8", { "hidden": authenticated })} hidden={authenticated}>
        <RutInput
          name="rut"
          register={register}
          setValue={setValue}
          errors={errors}
          required="Debe ingresar su RUT"
          help="Necesario para automatizar el envío vía PJUD"
        />
        <PasswordInput
          name="password"
          label="Clave Poder Judicial"
          register={register}
          errors={errors}
          help="Necesaria para automatizar el envío vía PJUD"
        />
        <button
          type="submit"
          className="text-white self-end py-1.5 md:py-2 px-2.5 md:px-4 rounded-lg text-sm md:text-base bg-blue-600 hover:bg-blue-500"
        >
          Autenticarse
        </button>
      </form>
      <ToastContainer toastStyle={{ zIndex: 9999 }}/> {/* Aparece sobre FullPageOverlay y Spinner */}
      <FullPageOverlay isVisible={isLoading} toastMessage={toastMessage} />
    </div>
  );
};

export default DemandTextSender;
