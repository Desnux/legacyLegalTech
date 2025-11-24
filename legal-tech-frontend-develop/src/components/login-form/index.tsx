"use client";

import React, { useContext, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { IconEye, IconEyeOff, IconUser, IconLock, IconShield } from "@tabler/icons-react";
import { AuthContext } from "@/contexts/auth-context";
import { setAuthTokenClient, setRecepthorAuthTokenClient, setUserGroupClient } from "@/utils/auth-token";
import { LoginRequest, sendLoginRequest } from "@/services/auth/login";
import { loginToRecepthor } from "@/services/recepthor";

const LoginForm: React.FC = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();
  const params = useSearchParams();
  const { setAuth } = useContext(AuthContext);
  const callbackUrl = params.get("callbackUrl") || "/";

  const togglePasswordVisibility = () => {
    setShowPassword((prev) => !prev);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError("");
    
    const request: LoginRequest = {
      username,
      password,
    };
    
    try {
      const result = await sendLoginRequest(request);
      // const resultRecepthor = await loginToRecepthor();
      
      if (result === null) {
        setError("Usuario o contraseña incorrectos.");
        return;
      }

      // if (resultRecepthor === null) {
      //   setError("Error al iniciar sesión en Recepthor.");
      //   return;
      // }

      if (result) {
        const { access_token, token_type, user_id, username, role, expires_at } = result;
        
        setAuthTokenClient(access_token);
        // if (resultRecepthor.token) {
        //   setRecepthorAuthTokenClient(resultRecepthor.token);
        // }
        setUserGroupClient(role);
        setAuth({ token: access_token, group: role });
        
        router.push(callbackUrl);
      } else {
        setError("Usuario o contraseña incorrectos.");
      }
    } catch (error) {
      console.error("Error al iniciar sesión:", error);
      setError("Error de conexión. Intente nuevamente.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-pure-white rounded-2xl shadow-xl border border-medium-gray overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-teal-green to-petroleum-blue px-8 py-6 text-center">
        <div className="flex items-center justify-center mb-4">
          <div className="bg-pure-white/20 rounded-full p-3">
            <IconShield size={32} className="text-pure-white" />
          </div>
        </div>
        <h1 className="text-h2 font-serif text-pure-white mb-2">
          Bienvenido
        </h1>
        <p className="text-body text-pure-white/90">
          Inicia sesión para acceder al sistema
        </p>
      </div>

      {/* Form */}
      <div className="px-8 py-8">
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Username Field */}
          <div className="space-y-2">
            <label className="block text-small font-semibold text-charcoal-gray">
              Nombre de usuario
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <IconUser size={20} className="text-medium-gray" />
              </div>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Ingrese su nombre de usuario"
                required
                disabled={isLoading}
                className="w-full pl-10 pr-4 py-3 border border-medium-gray rounded-lg text-body focus:outline-none focus:ring-2 focus:ring-teal-green/20 focus:border-teal-green transition-all duration-200 disabled:bg-light-gray disabled:cursor-not-allowed"
              />
            </div>
          </div>

          {/* Password Field */}
          <div className="space-y-2">
            <label className="block text-small font-semibold text-charcoal-gray">
              Contraseña
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <IconLock size={20} className="text-medium-gray" />
              </div>
              <input
                type={showPassword ? "text" : "password"}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Ingrese su contraseña"
                required
                disabled={isLoading}
                className="w-full pl-10 pr-12 py-3 border border-medium-gray rounded-lg text-body focus:outline-none focus:ring-2 focus:ring-teal-green/20 focus:border-teal-green transition-all duration-200 disabled:bg-light-gray disabled:cursor-not-allowed"
              />
              <button
                type="button"
                onClick={togglePasswordVisibility}
                disabled={isLoading}
                className="absolute inset-y-0 right-0 pr-3 flex items-center text-medium-gray hover:text-charcoal-gray transition-colors duration-200 disabled:cursor-not-allowed"
              >
                {showPassword ? (
                  <IconEyeOff size={20} />
                ) : (
                  <IconEye size={20} />
                )}
              </button>
            </div>
          </div>

          {/* Error Message */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-3">
              <p className="text-small text-red-600">{error}</p>
            </div>
          )}

          {/* Submit Button */}
          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-gradient-to-r from-teal-green to-teal-green/90 text-pure-white text-button font-semibold py-3 px-6 rounded-lg hover:from-teal-green/90 hover:to-teal-green/80 focus:outline-none focus:ring-2 focus:ring-teal-green/20 focus:ring-offset-2 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed transform hover:scale-[1.02] active:scale-[0.98]"
          >
            {isLoading ? (
              <div className="flex items-center justify-center">
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-pure-white mr-2"></div>
                Iniciando sesión...
              </div>
            ) : (
              "Iniciar Sesión"
            )}
          </button>
        </form>

        {/* Footer */}
        <div className="mt-8 pt-6 border-t border-medium-gray">
          <p className="text-small text-center text-medium-gray">
            ¿Necesitas ayuda? Contacta al administrador del sistema
          </p>
        </div>
      </div>
    </div>
  );
};

export default LoginForm;