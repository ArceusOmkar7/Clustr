import { Button } from "./ui/button";
import { ThemeToggle } from "./theme-toggle";

const Navbar = () => {
  return (
    <nav className="w-full flex items-center justify-between">
      <span className="font-bold text-xl">CLUSTR</span>
      <div className="flex items-center justify-between gap-4">
        <Button variant="ghost">Home</Button>
        <Button variant="ghost">Gallery</Button>
        <ThemeToggle />
      </div>
    </nav>
  );
};

export default Navbar;
