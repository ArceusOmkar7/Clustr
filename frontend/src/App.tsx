import "./App.css";
import Navbar from "./components/Navbar";
import { ThemeProvider } from "./components/theme-provider";

function App() {
  return (
    <ThemeProvider defaultTheme="system" storageKey="clustr-theme">
      <div className="min-h-screen bg-background text-foreground">
        <Navbar />
      </div>
    </ThemeProvider>
  );
}

export default App;
