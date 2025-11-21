import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { sendValidateTokenRequest } from "@/services/auth";
import { setAuthToken, getPreviousRoute } from "@/utils/auth-token";

const LoginForm: React.FC = () => {
  const [username, setUsername] = useState("");
  const [token, setToken] = useState("");
  const [error, setError] = useState("");
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const isValid = await sendValidateTokenRequest(token);
    
    if (isValid) {
      setAuthToken(token, 60 * 24); // Guarda el token en sessionStorage con expiración
      router.push(getPreviousRoute()); // Redirige a la página predeterminada
    } else {
      setError("Token inválido. Por favor, verifique su información.");
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
            Nombre de Usuario
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
            Token de Autenticación
          </label>
          <input
            type="password"
            value={token}
            onChange={(e) => setToken(e.target.value)}
            placeholder="Ingrese su token"
            required
            className="text-xs md:text-sm w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
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
