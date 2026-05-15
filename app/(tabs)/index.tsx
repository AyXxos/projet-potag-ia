import { AlertCircle, Calendar as CalendarIcon } from "lucide-react-native";
import { useEffect, useState } from "react";
import {
  ActivityIndicator,
  Modal,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from "react-native";
import { API_URL } from "../../constants/api";
import {
  AiCachePayload,
  fetchFreshAiData,
  getAiCache,
  getStoredLocation,
  isAiCacheStale,
  prefetchAiCache,
} from "../lib/ai-cache";

export default function DashboardScreen() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [viewMonthIndex, setViewMonthIndex] = useState(4); // Mai 2026
  const [selectedDate, setSelectedDate] = useState<{
    year: number;
    monthIndex: number;
    day: number;
  } | null>(null);
  const [modalVisible, setModalVisible] = useState(false);
  const [aiCache, setAiCache] = useState<AiCachePayload | null>(null);

  useEffect(() => {
    // Utilisation de l'IP de la machine locale pour les requêtes réseau depuis l'app
    fetch(`${API_URL}/api/to-plant`)
      .then((res) => res.json())
      .then((res) => {
        setData({ toPlantThisWeek: res });
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

  const now = new Date();
  const currentYear = now.getFullYear();
  const currentMonthIndex = now.getMonth();
  const todayDate = now.getDate();
  const viewYear = 2026;
  const minMonthIndex = 4; // Mai
  const maxMonthIndex = 8; // Septembre
  const monthNames = [
    "Janvier",
    "Fevrier",
    "Mars",
    "Avril",
    "Mai",
    "Juin",
    "Juillet",
    "Aout",
    "Septembre",
    "Octobre",
    "Novembre",
    "Decembre",
  ];
  const weekdayLabels = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"];
  const tomatoVarietiesByDay: Record<number, string[]> = {};
  if (aiCache?.items) {
    Object.values(aiCache.items).forEach((entry) => {
      const bestDate = entry.bestDate?.best_date;
      if (!bestDate) return;
      const parsed = new Date(bestDate);
      if (Number.isNaN(parsed.getTime())) return;
      if (
        parsed.getFullYear() !== viewYear ||
        parsed.getMonth() !== viewMonthIndex
      ) {
        return;
      }
      const day = parsed.getDate();
      if (!tomatoVarietiesByDay[day]) {
        tomatoVarietiesByDay[day] = [];
      }
      tomatoVarietiesByDay[day].push(entry.displayName || "Tomate");
    });
  }
  const tomatoDays = Object.keys(tomatoVarietiesByDay).map((day) =>
    Number(day),
  );

  const canGoPrev = viewMonthIndex > minMonthIndex;
  const canGoNext = viewMonthIndex < maxMonthIndex;

  const buildCalendarCells = (year: number, monthIndex: number) => {
    const daysInMonth = new Date(year, monthIndex + 1, 0).getDate();
    const firstDayIndex = (new Date(year, monthIndex, 1).getDay() + 6) % 7;
    return Array.from({ length: firstDayIndex + daysInMonth }, (_, i) =>
      i < firstDayIndex ? null : i - firstDayIndex + 1,
    );
  };

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color="#047857" />
        <Text style={styles.loadingText}>Chargement...</Text>
      </View>
    );
  }

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={{ paddingBottom: 30 }}
    >
      {/* Calendar Section */}
      <View style={styles.section}>
        <View style={styles.titleRow}>
          <CalendarIcon color="#065f46" size={20} />
          <Text style={styles.sectionTitle}>Calendrier</Text>
        </View>
        <View style={styles.calendarCard}>
          <View style={styles.monthHeaderRow}>
            <Pressable
              style={[styles.navButton, !canGoPrev && styles.navButtonDisabled]}
              onPress={() => canGoPrev && setViewMonthIndex(viewMonthIndex - 1)}
            >
              <Text style={styles.navButtonText}>‹</Text>
            </Pressable>
            <Text style={styles.monthTitle}>
              {monthNames[viewMonthIndex]} {viewYear}
            </Text>
            <Pressable
              style={[styles.navButton, !canGoNext && styles.navButtonDisabled]}
              onPress={() => canGoNext && setViewMonthIndex(viewMonthIndex + 1)}
            >
              <Text style={styles.navButtonText}>›</Text>
            </Pressable>
          </View>
          <View style={styles.weekdayRow}>
            {weekdayLabels.map((label) => (
              <Text key={label} style={styles.weekdayText}>
                {label}
              </Text>
            ))}
          </View>
          <View style={styles.calendarGrid}>
            {buildCalendarCells(viewYear, viewMonthIndex).map((date, index) => {
              if (!date) {
                return <View key={`empty-${index}`} style={styles.emptyCell} />;
              }

              const isToday =
                date === todayDate &&
                viewYear === currentYear &&
                viewMonthIndex === currentMonthIndex;
              const isTomatoDay = tomatoDays.includes(date);
              return (
                <Pressable
                  key={date}
                  onPress={() => {
                    setSelectedDate({
                      year: viewYear,
                      monthIndex: viewMonthIndex,
                      day: date,
                    });
                    setModalVisible(true);
                  }}
                  style={[styles.dayCell, isToday && styles.todayItem]}
                >
                  <Text
                    style={[
                      styles.dateTextMonthly,
                      isToday && styles.todayText,
                    ]}
                  >
                    {date}
                  </Text>
                  {isTomatoDay && <Text style={styles.tomatoIcon}>🍅</Text>}
                </Pressable>
              );
            })}
          </View>
        </View>
      </View>

      <Modal
        visible={modalVisible}
        transparent
        animationType="slide"
        onRequestClose={() => setModalVisible(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalCard}>
            <Text style={styles.modalTitle}>
              {selectedDate
                ? `${selectedDate.day} ${monthNames[selectedDate.monthIndex]} ${selectedDate.year}`
                : "Jour"}
            </Text>
            <Text style={styles.modalSubtitle}>Infos du jour</Text>
            <View style={styles.modalSection}>
              <Text style={styles.modalLabel}>Plantation recommandee</Text>
              <Text style={styles.modalValue}>
                {selectedDate && tomatoVarietiesByDay[selectedDate.day]?.length
                  ? `Tomates: ${tomatoVarietiesByDay[selectedDate.day].join(", ")}`
                  : aiCache
                    ? "Aucune recommandation"
                    : "Analyse IA en cours"}
              </Text>
            </View>
            <View style={styles.modalSection}>
              <Text style={styles.modalLabel}>Taches</Text>
              <Text style={styles.modalValue}>
                Arrosage, controle des feuilles
              </Text>
            </View>
            <Pressable
              style={styles.modalCloseButton}
              onPress={() => setModalVisible(false)}
            >
              <Text style={styles.modalCloseText}>Fermer</Text>
            </Pressable>
          </View>
        </View>
      </Modal>

    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#F5F5F0", padding: 16 },
  center: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: "#F5F5F0",
  },
  loadingText: { color: "#047857", marginTop: 10, fontWeight: "bold" },
  section: { marginBottom: 24 },
  titleRow: { flexDirection: "row", alignItems: "center", marginBottom: 12 },
  sectionTitle: {
    fontSize: 18,
    fontWeight: "bold",
    color: "#065f46",
    marginLeft: 8,
  },
  calendarCard: {
    backgroundColor: "#fff",
    padding: 16,
    borderRadius: 16,
    borderWidth: 1,
    borderColor: "#D1FAE5",
  },
  monthHeaderRow: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    marginBottom: 12,
  },
  monthTitle: {
    fontSize: 16,
    fontWeight: "bold",
    color: "#065f46",
  },
  navButton: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: "#ECFDF5",
    alignItems: "center",
    justifyContent: "center",
  },
  navButtonDisabled: { opacity: 0.4 },
  navButtonText: { fontSize: 20, color: "#065f46", fontWeight: "bold" },
  weekdayRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    marginBottom: 8,
  },
  weekdayText: {
    width: "14.2857%",
    textAlign: "center",
    color: "#6B7280",
    fontSize: 12,
    fontWeight: "600",
  },
  calendarGrid: { flexDirection: "row", flexWrap: "wrap" },
  emptyCell: { width: "14.2857%", height: 48, marginBottom: 8 },
  dayCell: {
    alignItems: "center",
    justifyContent: "center",
    width: "14.2857%",
    height: 48,
    marginBottom: 8,
    borderRadius: 8,
    backgroundColor: "#f8fafc",
  },
  todayItem: { backgroundColor: "#059669" },
  dateTextMonthly: { fontSize: 16, fontWeight: "bold", color: "#374151" },
  todayText: { color: "#fff" },
  tomatoIcon: { fontSize: 12, marginTop: 2 },
  modalOverlay: {
    flex: 1,
    backgroundColor: "rgba(15, 23, 42, 0.5)",
    justifyContent: "center",
    padding: 20,
  },
  modalCard: { backgroundColor: "#fff", borderRadius: 16, padding: 20 },
  modalTitle: {
    fontSize: 18,
    fontWeight: "bold",
    color: "#065f46",
    marginBottom: 4,
  },
  modalSubtitle: { color: "#6B7280", marginBottom: 16 },
  modalSection: { marginBottom: 12 },
  modalLabel: {
    fontSize: 12,
    textTransform: "uppercase",
    color: "#9CA3AF",
    marginBottom: 4,
  },
  modalValue: { fontSize: 14, color: "#111827" },
  modalCloseButton: {
    marginTop: 8,
    backgroundColor: "#047857",
    paddingVertical: 10,
    borderRadius: 10,
    alignItems: "center",
  },
  modalCloseText: { color: "#fff", fontWeight: "bold" },
  reminderCard: {
    backgroundColor: "#FFFBEB",
    padding: 20,
    borderRadius: 16,
    borderColor: "#FDE68A",
    borderWidth: 1,
    marginBottom: 24,
  },
  reminderRow: { flexDirection: "row" },
  reminderTitle: { fontWeight: "bold", color: "#78350F", fontSize: 16 },
  reminderDesc: {
    color: "#92400E",
    fontSize: 14,
    marginTop: 4,
    lineHeight: 20,
  },
  plantCard: {
    backgroundColor: "#fff",
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    padding: 16,
    borderRadius: 16,
    marginBottom: 12,
    borderColor: "#ECFDF5",
    borderWidth: 1,
  },
  plantName: { fontWeight: "500", fontSize: 16 },
  badge: { paddingHorizontal: 12, paddingVertical: 4, borderRadius: 999 },
  badgeHigh: { backgroundColor: "#FEE2E2" },
  badgeMedium: { backgroundColor: "#FFEDD5" },
  badgeText: { fontSize: 12, fontWeight: "bold" },
  badgeHighText: { color: "#B91C1C" },
  badgeMediumText: { color: "#C2410C" },
});
