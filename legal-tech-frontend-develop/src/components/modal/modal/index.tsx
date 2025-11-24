import { ReactNode, useEffect, useState } from "react";
import classNames from "classnames";
import { createPortal } from "react-dom";
import { ButtonClose } from "@/components/button";

interface ModalProps {
  isVisible: boolean;
  onClose: () => void;
  title?: string;
  children: ReactNode;
  footer?: ReactNode;
  className?: string;
  customWidthClassName?: string;
}

const Modal = ({ isVisible, onClose, title, children, footer, className, customWidthClassName }: ModalProps) => {
  const [isAnimating, setIsAnimating] = useState(false);
  const [isDisplayed, setIsDisplayed] = useState(isVisible);
  
  useEffect(() => {
    if (isVisible) {
      setIsDisplayed(true);
      setTimeout(() => setIsAnimating(true), 10);
    } else {
      setIsAnimating(false);
      setTimeout(() => setIsDisplayed(false), 300);
    }
  }, [isVisible]);

  if (!isDisplayed) return null;

  return createPortal(
    <div className={classNames(
      "fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 transition-opacity duration-300",
      {
        "opacity-100": isAnimating,
        "opacity-0": !isAnimating,
      },
    )}>
      <div
        className={classNames(
          "bg-white rounded-lg shadow-lg mx-4 p-6 relative transform transition-transform duration-300",
          !customWidthClassName && "max-w-lg w-full",
          {
            "scale-100": isAnimating,
            "scale-95": !isAnimating,
          },
          customWidthClassName,
          className,
        )}
      >
        <div className="flex justify-between items-center mb-4">
          {title && <h2 className="text-lg md:text-xl font-semibold">{title}</h2>}
          <ButtonClose onClick={onClose}/>
        </div>
        <div>
          {children}
        </div>
        {footer && <div className="mt-4">{footer}</div>}
      </div>
    </div>,
    document.body
  );
};

export default Modal;
