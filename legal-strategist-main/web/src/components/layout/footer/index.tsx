const Footer = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="flex flex-col items-center min-h-14 border-t border-gray-200 bg-gray-100 z-10">
      <div className="flex flex-1 items-center justify-center md:justify-start px-4 w-full text-gray-500 text-sm">
        <p>© {currentYear} Titan Group.</p>
      </div>
    </footer>
  );
};
  
export default Footer;