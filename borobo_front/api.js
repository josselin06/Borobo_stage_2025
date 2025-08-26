// src/api.js

//  Authentification
export async function login(username, password) {
  const response = await fetch(`/auth/token`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({ username, password }),
  });

  if (response.status === 400 || response.status === 401) {
    throw new Error("Nom d'utilisateur ou mot de passe incorrect.");
  }
  if (!response.ok) {
    throw new Error("Erreur de connexion au serveur.");
  }

  const data = await response.json();
  return data.access_token;
}

//  Récupérer l’arborescence des fichiers des robots
export async function fetchRobotsTree(token) {
  const response = await fetch(`/robots/tree`, {
    headers: { Authorization: `Bearer ${token}` },
  });

  if (response.status === 401) {
    throw new Error("Session expirée. Veuillez vous reconnecter.");
  }
  if (!response.ok) {
    throw new Error("Erreur lors du chargement des fichiers des robots");
  }

  return await response.json();
}

//  Récupérer les fichiers de maintenance
export async function fetchMaintenanceReports(token) {
  const response = await fetch(`/maintenance/reports`, {
    headers: { Authorization: `Bearer ${token}` },
  });

  if (response.status === 401) {
    throw new Error("Session expirée. Veuillez vous reconnecter.");
  }
  if (!response.ok) {
    throw new Error("Erreur lors de la récupération des fichiers de maintenance");
  }

  return await response.json();
}

//  Récupérer l'état actif/inactif des robots
export async function fetchRobotsStatus(token) {
  const response = await fetch(`/robots/status`, {
    headers: { Authorization: `Bearer ${token}` },
  });

  if (response.status === 401) {
    throw new Error("Session expirée. Veuillez vous reconnecter.");
  }
  if (!response.ok) {
    throw new Error("Erreur lors du chargement des statuts des robots.");
  }

  return await response.json();
}
