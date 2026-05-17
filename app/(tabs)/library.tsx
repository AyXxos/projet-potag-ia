import { Calendar, Info, Search, Sun } from "lucide-react-native";
import { useEffect, useState } from "react";
import {
  ActivityIndicator,
  Modal,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from "react-native";
import { API_URL } from "../../constants/api";
import {
  AiCachePayload,
  fetchFreshAiData,
  getAiCache,
  getStoredLocation,
  isAiCacheStale,
  normalizeVarieteName,
  prefetchAiCache,
  saveAiCache
} from "../lib/ai-cache";

export default function LibraryScreen() {
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedItem, setSelectedItem] = useState<any | null>(null);
  const [modalVisible, setModalVisible] = useState(false);

  // États pour l'IA
  const [prediction, setPrediction] = useState<any>(null);
  const [loadingIA, setLoadingIA] = useState(false);
  const [bestDate, setBestDate] = useState<any>(null);
  const [aiCache, setAiCache] = useState<AiCachePayload | null>(null);

  useEffect(() => {
    fetch(`${API_URL}/api/library`)
      .then((res) => res.json())
      .then((res) => {
        setData(res);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setLoading(false);
      });
  }, []);

  useEffect(() => {
    let isMounted = true;
    const loadAiData = async () => {
      const cached = await getAiCache();
      if (isMounted && cached) {
        setAiCache(cached);
      }
      
      const coords = await getStoredLocation();
      const data = await prefetchAiCache({
        lat: coords.lat,
        lon: coords.lon,
      });
      
      if (isMounted) {
        setAiCache(data);
      }
    };

    loadAiData();
    return () => {
      isMounted = false;
    };
  }, []);

  const getIAPrediction = async (varieteName: string) => {
    const variete = normalizeVarieteName(varieteName);
    const cachedEntry = aiCache?.items?.[variete];

    setPrediction(cachedEntry?.prediction ?? null);
    setBestDate(cachedEntry?.bestDate ?? null);

    if (cachedEntry && !isAiCacheStale(aiCache)) {
      setLoadingIA(false);
      return;
    }

    setLoadingIA(true);

    try {
      const coords = await getStoredLocation();
      const body = JSON.stringify({
        variete,
        lat: coords.lat,
        lon: coords.lon,
      });

      const [resPredict, resBest] = await Promise.all([
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

      const dataPredict = resPredict.ok ? await resPredict.json() : null;
      const dataBest = resBest.ok ? await resBest.json() : null;

      if (dataPredict) {
        setPrediction(dataPredict);
      }
      if (dataBest) {
        setBestDate(dataBest);
      }

      if (dataPredict || dataBest) {
        const updatedCache: AiCachePayload = {
          updatedAt: new Date().toISOString(),
          items: {
            ...(aiCache?.items ?? {}),
            [variete]: {
              displayName: varieteName,
              prediction: dataPredict ?? cachedEntry?.prediction ?? null,
              bestDate: dataBest ?? cachedEntry?.bestDate ?? null,
            },
          },
        };
        setAiCache(updatedCache);
        await saveAiCache(updatedCache);
      }
    } catch (error) {
      console.error("Erreur IA:", error);
    } finally {
      setLoadingIA(false);
    }
  };

  const filteredLibrary = data.filter((item) =>
    item.name.toLowerCase().includes(searchTerm.toLowerCase()),
  );

  const formatDayMonth = (value?: string) => {
    if (!value) return "Non defini";
    const dateValue = new Date(value);
    if (Number.isNaN(dateValue.getTime())) return "Non defini";
    return dateValue.toLocaleDateString("fr-FR", {
      day: "numeric",
      month: "long",
    });
  };

  return (
    <View style={styles.container}>
      <View style={styles.searchContainer}>
        <Search color="#9CA3AF" size={20} style={styles.searchIcon} />
        <TextInput
          style={styles.searchInput}
          placeholder="Rechercher un légume..."
          value={searchTerm}
          onChangeText={setSearchTerm}
          placeholderTextColor="#9CA3AF"
        />
      </View>

      {loading ? (
        <View style={styles.center}>
          <ActivityIndicator size="large" color="#047857" />
        </View>
      ) : (
        <ScrollView contentContainerStyle={{ paddingBottom: 30 }}>
          {filteredLibrary.map((item) => (
            <Pressable
              key={item.id}
              style={styles.card}
              onPress={() => {
                setSelectedItem(item);
                setModalVisible(true);
                getIAPrediction(item.name);
              }}
            >
              <View style={styles.cardHeader}>
                <Text style={styles.cardTitle}>{item.name}</Text>
              </View>
              <View style={styles.cardBody}>
                <View style={styles.row}>
                  <Calendar color="#059669" size={16} style={styles.rowIcon} />
                  <Text style={styles.rowText}>
                    Date IA :{" "}
                    <Text style={styles.bold}>
                      {(() => {
                        const entry =
                          aiCache?.items?.[normalizeVarieteName(item.name)];
                        return entry?.bestDate?.best_date
                          ? formatDayMonth(entry.bestDate.best_date)
                          : "Analyse IA en cours";
                      })()}
                    </Text>
                  </Text>
                </View>
                <View style={styles.row}>
                  <Sun color="#F59E0B" size={16} style={styles.rowIcon} />
                  <Text style={styles.rowText}>
                    Saison : <Text style={styles.bold}>{item.season}</Text>
                  </Text>
                </View>
              </View>
            </Pressable>
          ))}
        </ScrollView>
      )}

      <Modal
        visible={modalVisible}
        transparent
        animationType="slide"
        onRequestClose={() => setModalVisible(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalCard}>
            <ScrollView showsVerticalScrollIndicator={false}>
              <Text style={styles.modalTitle}>
                {selectedItem?.name ?? "Legume"}
              </Text>

              {/* SECTION DATE IA MISE EN AVANT */}
              <View style={styles.highlightDateBox}>
                <Calendar color="#059669" size={24} />
                <View style={{ marginLeft: 12 }}>
                  <Text style={styles.highlightDateLabel}>DATE DE PLANTATION IA</Text>
                  <Text style={styles.highlightDateValue}>
                    {(() => {
                      const entry = aiCache?.items?.[normalizeVarieteName(selectedItem?.name || "")];
                      return entry?.bestDate?.best_date
                        ? formatDayMonth(entry.bestDate.best_date)
                        : "Analyse en cours...";
                    })()}
                  </Text>
                </View>
              </View>

              {/* SECTION IA PREDICTION */}
              <View style={styles.iaSection}>
                <Text style={styles.iaTitle}>🧪 Analyse Potag'IA d'aujourd'hui</Text>
                {loadingIA ? (
                  <ActivityIndicator
                    size="small"
                    color="#059669"
                    style={{ marginVertical: 10 }}
                  />
                ) : prediction ? (
                  <View>
                    <View style={styles.scoreRow}>
                      <View style={styles.scoreBadge}>
                        <Text style={styles.scoreValue}>
                          {prediction.score}%
                        </Text>
                        <Text style={styles.scoreLabel}>Succès</Text>
                      </View>
                      <View style={styles.fiabiliteBadge}>
                        <Text style={styles.fiabiliteValue}>
                          {prediction.fiabilite}%
                        </Text>
                        <Text style={styles.fiabiliteLabel}>Confiance</Text>
                      </View>
                    </View>

                    <Text style={styles.statutLabel}>{prediction.statut}</Text>
                    <Text style={styles.conseilText}>{prediction.conseil}</Text>

                    {bestDate &&
                      bestDate.best_date !== prediction.meteo.date && (
                        <View style={styles.bestDateAlert}>
                          <Info size={14} color="#065F46" />
                          <Text style={styles.bestDateText}>
                            Pensez aussi au {formatDayMonth(bestDate.best_date)}{" "}
                            ({bestDate.best_score}%)
                          </Text>
                        </View>
                      )}

                    <View style={styles.dataUsedBox}>
                      <Text style={styles.dataUsedTitle}>
                        Données utilisées :
                      </Text>
                      <Text style={styles.dataUsedText}>
                        N: {prediction.data_used.N} | P:{" "}
                        {prediction.data_used.P} | K: {prediction.data_used.K} |
                        pH: {prediction.data_used.PH_Level}
                      </Text>
                    </View>
                  </View>
                ) : (
                  <Text style={styles.errorText}>
                    Impossible de charger l'analyse.
                  </Text>
                )}
              </View>

              <View style={styles.modalSection}>
                <Text style={styles.modalLabel}>Conseils de culture</Text>
                <Text style={styles.modalValue}>
                  {selectedItem?.tips ?? "Aucun conseil"}
                </Text>
              </View>

              <Pressable
                style={styles.modalCloseButton}
                onPress={() => setModalVisible(false)}
              >
                <Text style={styles.modalCloseText}>Fermer</Text>
              </Pressable>
            </ScrollView>
          </View>
        </View>
      </Modal>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#F5F5F0", padding: 16 },
  center: { flex: 1, justifyContent: "center", alignItems: "center" },
  searchContainer: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: "#fff",
    borderRadius: 16,
    paddingHorizontal: 12,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: "#D1FAE5",
  },
  searchIcon: { marginRight: 8 },
  searchInput: { flex: 1, height: 48, fontSize: 16, color: "#374151" },
  card: {
    backgroundColor: "#fff",
    borderRadius: 16,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: "#D1FAE5",
    overflow: "hidden",
  },
  cardHeader: {
    backgroundColor: "#ECFDF5",
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: "#D1FAE5",
  },
  cardTitle: { fontWeight: "bold", color: "#064E3B", fontSize: 16 },
  cardBody: { padding: 16 },
  row: { flexDirection: "row", alignItems: "center", marginBottom: 8 },
  rowIcon: { marginRight: 12 },
  rowText: { color: "#4B5563", fontSize: 14 },
  bold: { fontWeight: "bold", color: "#1F2937" },
  modalOverlay: {
    flex: 1,
    backgroundColor: "rgba(15, 23, 42, 0.5)",
    justifyContent: "center",
    padding: 20,
  },
  modalCard: {
    backgroundColor: "#fff",
    borderRadius: 16,
    padding: 20,
    maxHeight: "80%",
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: "bold",
    color: "#064E3B",
    marginBottom: 16,
  },
  highlightDateBox: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: "#ECFDF5",
    padding: 16,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: "#10B981",
    marginBottom: 20,
  },
  highlightDateLabel: {
    fontSize: 10,
    fontWeight: "bold",
    color: "#059669",
    letterSpacing: 1,
  },
  highlightDateValue: {
    fontSize: 18,
    fontWeight: "bold",
    color: "#064E3B",
  },
  iaSection: {
    backgroundColor: "#F0FDF4",
    padding: 16,
    borderRadius: 16,
    marginBottom: 20,
    borderWidth: 1,
    borderColor: "#DCFCE7",
  },
  iaTitle: {
    fontSize: 14,
    fontWeight: "bold",
    color: "#166534",
    marginBottom: 12,
  },
  scoreRow: {
    flexDirection: "row",
    justifyContent: "space-around",
    marginBottom: 12,
  },
  scoreBadge: { alignItems: "center" },
  scoreValue: { fontSize: 24, fontWeight: "bold", color: "#059669" },
  scoreLabel: { fontSize: 10, color: "#065F46", textTransform: "uppercase" },
  fiabiliteBadge: { alignItems: "center" },
  fiabiliteValue: { fontSize: 24, fontWeight: "bold", color: "#2563EB" },
  fiabiliteLabel: {
    fontSize: 10,
    color: "#1E40AF",
    textTransform: "uppercase",
  },
  statutLabel: {
    fontSize: 14,
    fontWeight: "bold",
    color: "#065F46",
    textAlign: "center",
    marginBottom: 4,
  },
  conseilText: {
    fontSize: 13,
    color: "#166534",
    textAlign: "center",
    lineHeight: 18,
    marginBottom: 12,
  },
  bestDateAlert: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: "#DCFCE7",
    padding: 8,
    borderRadius: 8,
    marginBottom: 12,
  },
  bestDateText: {
    fontSize: 11,
    color: "#166534",
    marginLeft: 6,
    fontWeight: "500",
  },
  dataUsedBox: { borderTopWidth: 1, borderTopColor: "#DCFCE7", paddingTop: 8 },
  dataUsedTitle: {
    fontSize: 10,
    color: "#166534",
    fontWeight: "bold",
    marginBottom: 2,
  },
  dataUsedText: { fontSize: 10, color: "#15803D" },
  modalSection: { marginBottom: 16 },
  modalLabel: {
    fontSize: 12,
    textTransform: "uppercase",
    color: "#9CA3AF",
    marginBottom: 4,
  },
  modalValue: { fontSize: 14, color: "#111827", lineHeight: 20 },
  modalCloseButton: {
    marginTop: 8,
    backgroundColor: "#047857",
    paddingVertical: 12,
    borderRadius: 12,
    alignItems: "center",
  },
  modalCloseText: { color: "#fff", fontWeight: "bold" },
  errorText: { color: "#DC2626", fontSize: 12, textAlign: "center" },
});
