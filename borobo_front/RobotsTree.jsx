// src/RobotsTree.jsx
import { useEffect, useState } from "react";
import { fetchRobotsTree, fetchRobotsStatus } from "./api";

function RobotsTree({ token, onLogout, onChangePassword }) {
  const [robotsData, setRobotsData] = useState([]);
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
    async function fetchData() {
      try {
        const [tree, statuses] = await Promise.all([
          fetchRobotsTree(token),
          fetchRobotsStatus(token),
        ]);
        const statusMap = Object.fromEntries(
          statuses.map((s) => [s.robot_folder, s])
        );
        const merged = tree.map((robot) => ({
          ...robot,
          is_active: statusMap[robot.robot_folder]?.is_active ?? false,
          last_seen: statusMap[robot.robot_folder]?.last_seen ?? null,
        }));
        setRobotsData(merged);
      } catch (err) {
        if (err.message.startsWith("Session expirée")) {
          setError(err.message);
          onLogout();
        } else {
          setError("Erreur lors du chargement des données des robots.");
        }
      }
    }
    fetchData();
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, [token, onLogout]);

  const formatLastSeen = (lastSeen) => {
    if (!lastSeen) return "—";
    return new Date(lastSeen).toLocaleString("fr-FR", {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
      hour12: false,
    });
  };

  const downloadFile = async (robotFolder, filename) => {
    try {
      const res = await fetch(
        `/robots/${robotFolder}/reports/${filename}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      if (!res.ok) throw new Error();
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = filename;
      a.click();
      URL.revokeObjectURL(url);
    } catch {
      alert("Échec du téléchargement.");
    }
  };

  const downloadAll = async (robotFolder) => {
    try {
      const res = await fetch(
        `/robots/${robotFolder}/reports/all`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      if (!res.ok) throw new Error();
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${robotFolder}_reports.zip`;
      a.click();
      URL.revokeObjectURL(url);
    } catch {
      alert("Échec du téléchargement du ZIP.");
    }
  };

  return (
    <div className="p-6">
      <header className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-semibold">Fichiers des robots</h2>
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

      {robotsData.map(({ robot_folder, reports, is_active, last_seen }, i) => (
        <details
          key={robot_folder}
          className="mb-4 border rounded shadow bg-white"
        >
          <summary className="cursor-pointer p-4 flex justify-between items-center">
            <div className="flex items-center gap-4">
              <h3 className="font-bold">
                Robot {i + 1} — {robot_folder}
              </h3>
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
                onClick={() => downloadAll(robot_folder)}
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
                    onClick={() => downloadFile(robot_folder, file)}
                    className="bg-green-600 hover:bg-green-700 text-white font-bold py-1 px-3 rounded text-sm"
                  >
                    Télécharger
                  </button>
                </li>
              ))}
            </ul>
          </div>
        </details>
      ))}
    </div>
  );
}

export default RobotsTree;
