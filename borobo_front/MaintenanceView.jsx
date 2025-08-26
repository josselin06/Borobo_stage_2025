// src/MaintenanceView.jsx
import { useEffect, useState } from "react";
import { fetchMaintenanceReports, fetchRobotsStatus } from "./api";
import axios from "axios";

function MaintenanceView({ token, onLogout, onChangePassword }) {
  const [reportsData, setReportsData] = useState([]);
  const [statuses, setStatuses] = useState({});
  const [error, setError] = useState("");

  const parseJwt = (token) => {
    try {
      return JSON.parse(atob(token.split(".")[1]));
    } catch {
      return {};
    }
  };
  const username = parseJwt(token).sub || "Utilisateur";

  useEffect(() => {
    async function load() {
      try {
        const [maint, statusList] = await Promise.all([
          fetchMaintenanceReports(token),
          fetchRobotsStatus(token),
        ]);
        setReportsData(maint);
        setStatuses(
          Object.fromEntries(statusList.map((s) => [s.robot_folder, s]))
        );
        setError("");
      } catch (err) {
        if (err.message.startsWith("Session expirée")) {
          setError(err.message);
          onLogout();
        } else {
          setError("Erreur lors du chargement des fichiers de maintenance.");
        }
      }
    }
    load();
  }, [token, onLogout]);

  const formatLastSeen = (last_seen) =>
    last_seen
      ? new Date(last_seen).toLocaleString("fr-FR", {
          year: "numeric",
          month: "2-digit",
          day: "2-digit",
          hour: "2-digit",
          minute: "2-digit",
          hour12: false,
        })
      : "—";

  const download = async (url, filename) => {
    try {
      const res = await axios.get(url, {
        headers: { Authorization: `Bearer ${token}` },
        responseType: "blob",
      });
      const blob = new Blob([res.data]);
      const link = document.createElement("a");
      link.href = URL.createObjectURL(blob);
      link.download = filename;
      link.click();
      URL.revokeObjectURL(link.href);
    } catch {
      alert("Échec du téléchargement.");
    }
  };

  return (
    <div className="p-6">
      <header className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-semibold">Fichiers de maintenance</h2>
        <div className="flex items-center gap-2">
          <span className="text-gray-700">Connecté en tant que : {username}</span>
          <button
            onClick={onChangePassword}
            className="bg-yellow-500 hover:bg-yellow-600 text-white font-bold py-1 px-3 rounded"
          >
            Changer mot de passe
          </button>
          <button
            onClick={onLogout}
            className="bg-red-500 hover:bg-red-600 text-white font-bold py-1 px-3 rounded"
          >
            Se déconnecter
          </button>
        </div>
      </header>

      {error && <p className="text-red-500 mb-4">{error}</p>}

      {reportsData.map(({ robot_folder, reports }) => {
        const { is_active, last_seen } = statuses[robot_folder] || {};
        return (
          <details
            key={robot_folder}
            className="mb-4 border rounded shadow bg-white"
          >
            <summary className="cursor-pointer p-4 flex justify-between items-center">
              <div className="flex items-center gap-4">
                <h3 className="font-bold">{robot_folder}</h3>
                <div
                  className={`w-3 h-3 rounded-full ${
                    is_active ? "bg-green-500" : "bg-red-500"
                  }`}
                />
                <span className="text-sm text-gray-500">
                  Dernière activité : {formatLastSeen(last_seen)}
                </span>
              </div>
            </summary>
            <div className="p-4">
              <div className="flex justify-end mb-4">
                <button
                  onClick={() =>
                    download(
                      `/maintenance/${robot_folder}/reports/all`,
                      `${robot_folder}_maintenance_reports.zip`
                    )
                  }
                  className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-1 px-3 rounded"
                >
                  Télécharger tout
                </button>
              </div>
              <ul className="space-y-2">
                {reports.map((file) => (
                  <li
                    key={file}
                    className="flex justify-between items-center bg-gray-100 rounded p-2"
                  >
                    <span>{file}</span>
                    <button
                      onClick={() =>
                        download(
                          `/maintenance/download?robot_folder=${robot_folder}&filename=${file}`,
                          file
                        )
                      }
                      className="bg-green-600 hover:bg-green-700 text-white font-bold py-1 px-3 rounded text-sm"
                    >
                      Télécharger
                    </button>
                  </li>
                ))}
              </ul>
            </div>
          </details>
        );
      })}
    </div>
  );
}

export default MaintenanceView;
