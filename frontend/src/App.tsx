import "./App.css";
import Navbar from "./components/Navbar";
import { ThemeProvider } from "./components/theme-provider";
import { Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import Gallery from "./pages/Gallery";
import Health from "./pages/Health";

function App() {
  return (
    <ThemeProvider defaultTheme="system" storageKey="clustr-theme">
      <div className="flex flex-col h-screen bg-background text-foreground">
        <Navbar />
        <main className="flex-1 overflow-hidden">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/gallery" element={<Gallery />} />
            <Route path="/health" element={<Health />} />
          </Routes>
        </main>
      </div>
    </ThemeProvider>
  );
}

export default App;
