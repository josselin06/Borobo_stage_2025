import { useState } from "react";

function ChangePassword({ token, onLogout, onBack }) {
  const [oldPassword, setOldPassword]         = useState("");
  const [newPassword, setNewPassword]         = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [message, setMessage]                 = useState("");
  const [error, setError]                     = useState("");

  //Mot de passe fort : ≥ 8 caractères, ≥ 1 majuscule, ≥ 1 chiffre, ≥ 1 caractère spécial
  const passwordPattern = /^(?=.*[A-Z])(?=.*\d)(?=.*[!@#\$%\^&\*]).{8,}$/;

  const handleChangePassword = async (e) => {
    e.preventDefault();
    setMessage("");
    setError("");


    if (!passwordPattern.test(newPassword)) {
      setError(
        "Le mot de passe doit faire au moins 8 caractères, " +
        "contenir une majuscule, un chiffre et un caractère spécial."
      );
      return;
    }

    // Vérification client : les deux nouveaux mots de passe doivent être identiques
    if (newPassword !== confirmPassword) {
      setError("Les deux nouveaux mots de passe ne correspondent pas.");
      return;
    }

    try {
      const response = await fetch("/auth/users/change-password", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          old_password:     oldPassword,
          new_password:     newPassword,
          confirm_password: confirmPassword,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        let detail = data.detail;
        let msg;
        if (Array.isArray(detail)) {
          msg = detail.map((err) => err.msg || JSON.stringify(err)).join(" ; ");
        } else if (typeof detail === "string") {
          msg = detail;
        } else {
          msg = JSON.stringify(detail);
        }
        throw new Error(msg);
      }

      // Succès
      setMessage(data.detail || "Mot de passe changé avec succès.");
      setOldPassword("");
      setNewPassword("");
      setConfirmPassword("");
    } catch (err) {
      setError(err.message || "Erreur inconnue");
    }
  };

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-semibold">Changer le mot de passe</h2>
        <div className="flex items-center gap-2">
          <button
            onClick={onBack}
            className="bg-gray-500 hover:bg-gray-600 text-white font-bold py-1 px-3 rounded"
          >
            Retour
          </button>
          <button
            onClick={onLogout}
            className="bg-red-500 hover:bg-red-600 text-white font-bold py-1 px-3 rounded"
          >
            Se déconnecter
          </button>
        </div>
      </div>

      <form onSubmit={handleChangePassword} className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1">
            Ancien mot de passe
          </label>
          <input
            type="password"
            value={oldPassword}
            onChange={(e) => setOldPassword(e.target.value)}
            className="w-full border rounded p-2"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">
            Nouveau mot de passe
          </label>
          <input
            type="password"
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
            className="w-full border rounded p-2"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">
            Confirmer le nouveau mot de passe
          </label>
          <input
            type="password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            className="w-full border rounded p-2"
            required
          />
        </div>

        <button
          type="submit"
          className="bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded w-full"
        >
          Valider
        </button>

        {message && <p className="text-green-500 mt-2">{message}</p>}
        {error   && <p className="text-red-500 mt-2">{error}</p>}
      </form>
    </div>
  );
}

export default ChangePassword;
