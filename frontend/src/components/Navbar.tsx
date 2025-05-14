import { Button } from "./ui/button";
import { ThemeToggle } from "./theme-toggle";
import { Link, useLocation } from "react-router-dom";
import { cn } from "../lib/utils";

const Navbar = () => {
  const location = useLocation();

  const navLinks = [
    { to: "/", label: "Home" },
    { to: "/gallery", label: "Gallery" },
  ];

  return (
    <nav className="w-full flex items-center justify-between p-4 bg-card">
      <span className="font-bold text-xl">CLUSTR</span>
      <div className="flex items-center justify-between gap-4">
        {navLinks.map((link) => (
          <Link key={link.to} to={link.to}>
            <Button
              variant="ghost"
              className={cn(
                location.pathname === link.to &&
                  "bg-accent text-accent-foreground"
              )}
            >
              {link.label}
            </Button>
          </Link>
        ))}
        <ThemeToggle />
      </div>
    </nav>
  );
};

export default Navbar;
