import AsyncStorage from "@react-native-async-storage/async-storage";
import { API_URL } from "../../constants/api";

const LOCATION_VALUE_KEY = "potagia.location.value";
const DEFAULT_LOCATION = { lat: 48.8566, lon: 2.3522 };
const VARIETE_COEUR = "C\u0153ur de B\u0153uf";
const VARIETE_NOIRE = "Noire de Crim\u00e9e";

type AiCacheItem = {
  displayName: string;
  prediction: any | null;
  bestDate: any | null;
};

export type AiCachePayload = {
  updatedAt: string;
  items: Record<string, AiCacheItem>;
};

export const normalizeVarieteName = (name: string) => {
  const normalized = name
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .trim();

  if (normalized.includes("Marmande")) return "Marmande";
  if (normalized.includes("Cerise")) return "Cerise";
  if (normalized.includes("Coeur de Boeuf")) return VARIETE_COEUR;
  if (normalized.includes("Noire") || normalized.includes("Crimee"))
    return VARIETE_NOIRE;
  return name.trim();
};

export const getStoredLocation = async () => {
  const value = await AsyncStorage.getItem(LOCATION_VALUE_KEY);
  if (!value) return DEFAULT_LOCATION;
  const [latRaw, lonRaw] = value.split(",").map((part) => part.trim());
  const lat = Number(latRaw);
  const lon = Number(lonRaw);
  if (!Number.isFinite(lat) || !Number.isFinite(lon)) return DEFAULT_LOCATION;
  return { lat, lon };
};

// Cache en mémoire vive (volatile)
// Ce cache disparaît dès que l'application est fermée/relancée
let MEMORY_AI_CACHE: AiCachePayload | null = null;

const AI_CACHE_TTL_MS = 60 * 60 * 1000; // 1 heure par sécurité durant la session

export const getAiCache = async () => {
  return MEMORY_AI_CACHE;
};

export const saveAiCache = async (payload: AiCachePayload) => {
  MEMORY_AI_CACHE = payload;
};

export const isAiCacheStale = (payload: AiCachePayload | null) => {
  if (!payload?.updatedAt) return true;
  const updatedAt = new Date(payload.updatedAt).getTime();
  if (Number.isNaN(updatedAt)) return true;
  return Date.now() - updatedAt > AI_CACHE_TTL_MS;
};

/**
 * Récupère les données IA en temps réel et les stocke dans le cache.
 */
export const fetchFreshAiData = async (options?: {
  lat?: number;
  lon?: number;
}) => {
  const coords = {
    lat: options?.lat ?? DEFAULT_LOCATION.lat,
    lon: options?.lon ?? DEFAULT_LOCATION.lon,
  };

  try {
    const libraryRes = await fetch(`${API_URL}/api/library`);
    if (!libraryRes.ok) return null;
    const libraryItems: Array<{ name: string }> = await libraryRes.json();

    const varietyMap: Record<string, string> = {};
    for (const item of libraryItems) {
      const variete = normalizeVarieteName(item.name);
      if (!varietyMap[variete]) {
        varietyMap[variete] = item.name;
      }
    }

    const entries = await Promise.all(
      Object.entries(varietyMap).map(async ([variete, displayName]) => {
        const body = JSON.stringify({
          variete,
          lat: coords.lat,
          lon: coords.lon,
        });

        const [predictRes, bestRes] = await Promise.all([
          fetch(`${API_URL}/ai/predict`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body,
          }),
          fetch(`${API_URL}/ai/best-planting-date`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body,
          }),
        ]);

        const prediction = predictRes.ok ? await predictRes.json() : null;
        const bestDate = bestRes.ok ? await bestRes.json() : null;

        return [variete, { displayName, prediction, bestDate } as AiCacheItem];
      }),
    );

    const payload: AiCachePayload = {
      updatedAt: new Date().toISOString(),
      items: Object.fromEntries(entries),
    };

    await saveAiCache(payload);
    return payload;
  } catch (error) {
    console.error("Erreur fetch IA:", error);
    return null;
  }
};

/**
 * Récupère le cache ou lance une analyse si périmé.
 */
export const prefetchAiCache = async (options?: {
  lat?: number;
  lon?: number;
  force?: boolean;
}) => {
  const existing = await getAiCache();
  if (!options?.force && existing && !isAiCacheStale(existing)) {
    return existing;
  }
  return fetchFreshAiData(options);
};

