import React from "react";
import classNames from "classnames";

export interface ButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  type?: "button" | "submit" | "reset";
  variant?: "primary" | "secondary" | "success" | "danger" | "warning" | "ghost";
  size?: "sm" | "md" | "lg";
  disabled?: boolean;
  loading?: boolean;
  fullWidth?: boolean;
  className?: string;
  icon?: React.ReactNode;
  iconPosition?: "left" | "right";
}

const Button: React.FC<ButtonProps> = ({
  children,
  onClick,
  type = "button",
  variant = "primary",
  size = "md",
  disabled = false,
  loading = false,
  fullWidth = false,
  className = "",
  icon,
  iconPosition = "left"
}) => {
  const baseClasses = "inline-flex items-center justify-center font-medium rounded-full transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed";
  
  const variantClasses = {
    primary: "bg-gradient-to-r from-teal-green to-teal-green/90 hover:from-teal-green/90 hover:to-teal-green/80 text-pure-white focus:ring-teal-green/20 shadow-lg hover:shadow-xl",
    secondary: "bg-gradient-to-r from-petroleum-blue to-petroleum-blue/90 hover:from-petroleum-blue/90 hover:to-petroleum-blue/80 text-pure-white focus:ring-petroleum-blue/20 shadow-lg hover:shadow-xl",
    success: "bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 text-pure-white focus:ring-green-500/20 shadow-lg hover:shadow-xl",
    danger: "bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700 text-pure-white focus:ring-red-500/20 shadow-lg hover:shadow-xl",
    warning: "bg-gradient-to-r from-yellow-500 to-yellow-600 hover:from-yellow-600 hover:to-yellow-700 text-pure-white focus:ring-yellow-500/20 shadow-lg hover:shadow-xl",
    ghost: "bg-transparent hover:bg-light-gray text-charcoal-gray hover:text-petroleum-blue border border-medium-gray hover:border-petroleum-blue focus:ring-petroleum-blue/20 shadow-sm hover:shadow-md"
  };

  const sizeClasses = {
    sm: "px-4 py-2 text-small",
    md: "px-6 py-3 text-body-sm",
    lg: "px-8 py-4 text-body"
  };

  const widthClasses = fullWidth ? "w-full" : "";

  const classes = classNames(
    baseClasses,
    variantClasses[variant],
    sizeClasses[size],
    widthClasses,
    className
  );

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled || loading}
      className={classes}
    >
      {loading && (
        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-current mr-2"></div>
      )}
      {!loading && icon && iconPosition === "left" && (
        <span className="mr-2">{icon}</span>
      )}
      {children}
      {!loading && icon && iconPosition === "right" && (
        <span className="ml-2">{icon}</span>
      )}
    </button>
  );
};

// Exportar componentes existentes
export { default as ButtonClose } from "./button-close";
export { default as ButtonCopy } from "./button-copy";
export { default as ButtonGenerate } from "./button-generate";
export { default as ButtonPrimary } from "./button-primary";
export { default as ButtonSecondary } from "./button-secondary";
export { default as ButtonSend } from "./button-send";

export default Button;
