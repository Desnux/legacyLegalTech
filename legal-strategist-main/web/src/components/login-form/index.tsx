"use client";

import React, { useContext, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { IconEye, IconEyeOff } from "@tabler/icons-react";
import { AuthContext } from "@/contexts/auth-context";
import { sendValidateTokenRequest } from "@/services/auth";
import { setAuthTokenClient, setUserGroupClient } from "@/utils/auth-token";

const LoginForm: React.FC = () => {
  const [username, setUsername] = useState("");
  const [token, setToken] = useState("");
  const [error, setError] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const router = useRouter();
  const params = useSearchParams();
  const { setAuth } = useContext(AuthContext);
  const callbackUrl = params.get("callbackUrl") || "/";

  const togglePasswordVisibility = () => {
    setShowPassword((prev) => !prev);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    const result = await sendValidateTokenRequest(token)
  
    if (result && typeof result !== "boolean") {
      const { group } = result;
      setAuthTokenClient(token);
      setUserGroupClient(group);
      setAuth({ token, group: result.group });
      router.push(callbackUrl)
    } else {
      setError("Token inválido. Por favor, verifique su información.")
    }
  };

  return (
    <div className="flex flex-1 w-full items-center justify-center bg-white md:bg-gray-100">
      <form
        onSubmit={handleSubmit}
        className="bg-white p-6 md:rounded-xl md:shadow-lg w-full max-w-sm"
      >
        <div className="text-xl md:text-2xl font-bold mb-6 text-center">¡Hola, empecemos!</div>
        <div className="text-xs md:text-sm mb-6 text-center">Por favor, inicie sesión para continuar.</div>

        <div className="mb-4">
          <label className="block text-gray-700 text-xs md:text-sm font-semibold mb-2">
            Nombre de usuario
          </label>
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="Ingrese su nombre de usuario"
            required
            className="text-xs md:text-sm w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        <div className="mb-4">
          <label className="block text-gray-700 text-xs md:text-sm font-semibold mb-2">
            Token de autenticación
          </label>
          <div className="flex rounded-md group focus-within:ring-2 focus-within:ring-blue-500">
            <input
              type={showPassword ? "text" : "password"}
              value={token}
              onChange={(e) => setToken(e.target.value)}
              placeholder="Ingrese su token"
              required
              className="text-xs md:text-sm w-full px-3 py-2 border rounded-l-md focus:outline-none focus:ring-0 focus:border-transparent"
            />
            <button
              type="button"
              onClick={togglePasswordVisibility}
              className="px-2 md:px-3 py-1.5 md:py-2 bg-blue-600 text-white rounded-r-md group-focus-within:rounded-r-sm hover:bg-blue-500 focus:outline-none focus:ring-0"
            >
              {showPassword ? (
                <>
                  <IconEyeOff className="hidden md:block" size={20}/>
                  <IconEyeOff className="md:hidden" size={18}/>
                </>
              ) : (
                <>
                  <IconEye className="hidden md:block" size={20}/>
                  <IconEye className="md:hidden" size={18}/>
                </>
              )}
            </button>
          </div>
        </div>

        {error && <p className="text-red-500 text-sm mb-4">{error}</p>}

        <button
          type="submit"
          className="w-full bg-blue-600 text-white text-sm md:text-base font-semibold mt-2 py-2 px-4 rounded-md hover:bg-blue-500 transition"
        >
          Iniciar Sesión
        </button>
      </form>
    </div>
  );
};

export default LoginForm;
