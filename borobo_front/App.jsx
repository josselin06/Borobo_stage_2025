import { useState } from "react";
import Login from "./Login";
import RobotsTree from "./RobotsTree";
import MaintenanceView from "./MaintenanceView";
import ChangePassword from "./ChangePassword";
import DateTimeDisplay from "./DateTimeDisplay";
import CombinedView from "./CombinedView";
import logo from "/logo_borobo.jpg";

function App() {
  const [token, setToken] = useState(null);   // JWT
  const [role, setRole]   = useState(null);   // "user" | "maintenance" | "superuser"
  const [view, setView]   = useState("main"); // "main" ou "changePassword"

  const handleLogin = (token) => {
    const payload = JSON.parse(atob(token.split(".")[1]));
    setToken(token);
    setRole(payload.role);
  };

  const handleLogout = () => {
    setToken(null);
    setRole(null);
    setView("main");
  };

  return (
    <div className="min-h-screen flex flex-col">
      {/* HEADER */}
      <header className="flex items-center justify-between bg-white shadow px-6 py-4">
        <img src={logo} alt="Logo Borobo" className="h-8 w-auto mr-4" />
        {token && <DateTimeDisplay />}
      </header>

      {/* BODY */}
      <main className="flex-1">
        {token ? (
          view === "changePassword" ? (
            <ChangePassword
              token={token}
              onLogout={handleLogout}
              onBack={() => setView("main")}
            />
          ) : 
          role === "superuser" ? (
            <CombinedView
              token={token}
              onLogout={handleLogout}
              onChangePassword={() => setView("changePassword")}
            />
          ) : 
          role === "maintenance" ? (
            <MaintenanceView
              token={token}
              onLogout={handleLogout}
              onChangePassword={() => setView("changePassword")}
            />
          ) : (
            <RobotsTree
              token={token}
              onLogout={handleLogout}
              onChangePassword={() => setView("changePassword")}
            />
          )
        ) : (
          <Login onLogin={handleLogin} />
        )}
      </main>
    </div>
  );
}

export default App;
