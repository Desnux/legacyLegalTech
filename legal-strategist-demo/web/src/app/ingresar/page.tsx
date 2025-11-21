"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import LoginForm from "@/components/login-form";
import { getAuthToken, getPreviousRoute } from "@/utils/auth-token";

const LoginPage: React.FC = () => {
  const router = useRouter();

  useEffect(() => {
    const token = getAuthToken();
    if (token !== null) {
      router.push(getPreviousRoute()); // Redirige si el usuario ya está autenticado
    }
  }, [router]);

  return (
    <div className="login-page flex flex-col md:my-4 flex-1 w-full">
      <LoginForm />
    </div>
  );
};

export default LoginPage;
