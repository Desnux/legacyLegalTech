"use client";

import { Suspense } from "react";
import LoginForm from "@/components/login-form";
import { Spinner } from "@/components/state";

const LoginPage: React.FC = () => {
  return (
    <div className="login-page flex flex-col md:my-4 flex-1 w-full">
      <Suspense fallback={
        <div className="p-6 flex flex-col flex-1">
          <Spinner className="flex-1"/>
        </div>
      }>
        <LoginForm />
      </Suspense>
    </div>
  );
};

export default LoginPage;
