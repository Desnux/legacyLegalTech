"use client";

import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { useRouter } from "next/navigation";
import { toast, ToastContainer } from "react-toastify";
import { IconEye, IconEyeOff } from "@tabler/icons-react";
import Button from "@/components/button";
import { TextInput, PasswordInput, Dropdown } from "@/components/input";
import { CreateUserRequest, sendCreateUserRequest } from "@/services/auth/create-user";
import { fetchLawFirmsRequest } from "@/services/law-firm";
import { Spinner } from "@/components/state";
import { LawFirm } from "@/types/law-firm";
import { ROLE_OPTIONS, UserFormData } from "@/types/user";

export default function CreateUserPage() {
  const router = useRouter();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [lawFirms, setLawFirms] = useState<LawFirm[]>([]);
  const [isLoadingLawFirms, setIsLoadingLawFirms] = useState(true);
  const {
    register,
    handleSubmit,
    setValue,
    watch,
    formState: { errors },
  } = useForm<UserFormData>({
    defaultValues: {
      name: "",
      password: "",
      confirmPassword: "",
      role: "guest",
      law_firm_id: "",
    },
  });

  const password = watch("password");

  const validatePasswordConfirmation = (value: string) => {
    if (value !== password) {
      return "Las contraseñas no coinciden";
    }
    return true;
  };

  const onSubmit = async (data: UserFormData) => {
    if(data.password.length < 8) {
      toast.error("La contraseña debe tener al menos 8 caracteres");
      return;
    }
    if(data.password !== data.confirmPassword) {
      toast.error("Las contraseñas no coinciden");
      return;
    }
    setIsSubmitting(true);
    try {
      const request: CreateUserRequest = {
        name: data.name,
        password: data.password,
        role: data.role,
        law_firm_id: data.law_firm_id === "" ? null : data.law_firm_id,
      };
      const result = await sendCreateUserRequest(request);
      
      if (result) {
        router.push("/users");
      } else {
        toast.error("Error al crear usuario");
      }
    } catch (error) {
      console.error("Error al crear usuario:", error);
    } finally {
      setIsSubmitting(false);
    }
  };

  useEffect(() => {
    fetchLawFirms();
  }, []);

  const fetchLawFirms = async () => {
    try {
      setIsLoadingLawFirms(true);
      const lawFirmsData = await fetchLawFirmsRequest();
      setLawFirms(lawFirmsData);
    } catch (error) {
      console.error("Error al obtener las firmas de abogados:", error);
      toast.error("Error al cargar las firmas de abogados");
    } finally {
      setIsLoadingLawFirms(false);
    }
  };

  const handleCancel = () => {
    router.back();
  };

  const toggleConfirmPasswordVisibility = () => {
    setShowConfirmPassword((prev) => !prev);
  };

  if (isLoadingLawFirms) {
    return (
      <div className="min-h-screen bg-light-gray py-8 flex items-center justify-center">
        <div className="bg-pure-white rounded-xl shadow-sm border border-medium-gray p-12 text-center">
          <Spinner className="mb-4" />
          <p className="text-body text-charcoal-gray">Cargando Datos...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-light-gray py-8">
      <div className="max-w-2xl mx-auto px-4">
        <div className="bg-pure-white rounded-xl shadow-sm border border-medium-gray p-6 md:p-8">
          <div className="mb-8">
            <h1 className="text-h2 font-serif text-petroleum-blue mb-3">
              Crear Nuevo Usuario
            </h1>
            <p className="text-body text-charcoal-gray">
              Complete los campos para crear un nuevo usuario en el sistema.
            </p>
          </div>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            {/* Campo Nombre */}
            <TextInput
              name="name"
              label="Nombre de Usuario"
              placeholder="Ingrese el nombre de usuario"
              register={register}
              setValue={setValue}
              errors={errors}
              required="El nombre es requerido"
              className="w-full"
            />

            {/* Campo Contraseña */}
            <PasswordInput
              name="password"
              label="Contraseña"
              placeholder="Ingrese la contraseña"
              register={register}
              errors={errors}
              className="w-full"
            />

            {/* Campo Confirmar Contraseña */}
            <div className="w-full">
              <label htmlFor="confirmPassword" className="block text-body-sm font-medium text-petroleum-blue mb-2">
                Confirmar contraseña
              </label>
              <div className="flex rounded-lg">
                <input
                  type={showConfirmPassword ? "text" : "password"}
                  id="confirmPassword"
                  placeholder="Confirme la contraseña"
                  className={`p-3 border rounded-l-lg outline-none bg-pure-white w-full border-medium-gray focus:border-teal-green focus:ring-1 focus:ring-teal-green/20 transition-colors duration-200 text-body-sm ${errors.confirmPassword ? "border-red-500 focus:border-red-500 focus:ring-red-500/20" : ""}`}
                  {...register("confirmPassword", {
                    required: "Debe confirmar la contraseña",
                    validate: validatePasswordConfirmation
                  })}
                />
                <button
                  type="button"
                  onClick={toggleConfirmPasswordVisibility}
                  className="px-3 py-3 bg-teal-green text-pure-white rounded-r-lg hover:bg-teal-green/90 focus:outline-none focus:ring-2 focus:ring-teal-green/20 transition-all duration-200 flex items-center justify-center"
                >
                  {showConfirmPassword ? (
                    <IconEyeOff size={20} className="transition-transform duration-200" />
                  ) : (
                    <IconEye size={20} className="transition-transform duration-200" />
                  )}
                </button>
              </div>
              {errors.confirmPassword && (
                <p className="text-red-600 text-small mt-2">{errors.confirmPassword.message}</p>
              )}
            </div>

            {/* Campo Rol */}
            <Dropdown
              name="role"
              label="Rol del usuario"
              options={ROLE_OPTIONS}
              register={register}
              setValue={setValue}
              watch={watch}
              required
              error={errors.role?.message}
              className="w-full"
            />

            {/* Campo Firma de Abogados */}
            <Dropdown
              name="law_firm_id"
              label="Firma de Abogados"
              options={[
                { value: "", label: "Sin firma" },
                ...lawFirms.map((firm) => ({
                  value: firm.id,
                  label: firm.name,
                }))
              ]}
              register={register}
              setValue={setValue}
              watch={watch}
              error={errors.law_firm_id?.message}
              className="w-full"
            />

            {/* Botones */}
                          <div className="flex flex-col sm:flex-row gap-4 pt-6 border-t border-medium-gray">
                <Button
                  variant="secondary"
                  onClick={handleCancel}
                  className="flex-1"
                >
                  Cancelar
                </Button>
                <Button
                  variant="primary"
                  onClick={handleSubmit(onSubmit)}
                  disabled={isSubmitting}
                  loading={isSubmitting}
                  className="flex-1"
                >
                  {isSubmitting ? "Creando..." : "Crear Usuario"}
                </Button>
              </div>
          </form>
        </div>  
      </div>
       <ToastContainer toastStyle={{ zIndex: 9999 }}/>
    </div>
  );
}
