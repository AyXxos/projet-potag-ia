import { Combine, Droplets, Sprout, Thermometer } from "lucide-react-native";
import { useEffect, useState } from "react";
import {
    ActivityIndicator,
    ScrollView,
    StyleSheet,
    Text,
    View,
} from "react-native";

export default function GardenScreen() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      fetch("http://172.23.119.189:8000/api/garden-stats").then((res) =>
        res.json(),
      ),
      fetch("http://172.23.119.189:8000/api/current-vegetables").then((res) =>
        res.json(),
      ),
    ])
      .then(([stats, veg]) => {
        setData({ gardenStats: stats, currentVegetables: veg });
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color="#047857" />
      </View>
    );
  }

  const stats = data?.gardenStats;
  const vegs = data?.currentVegetables || [];

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={{ paddingBottom: 30 }}
    >
      {/* Header Info */}
      <View style={styles.headerInfo}>
        <Text style={styles.headerTitle}>Mon Espace</Text>
        <Text style={styles.headerSub}>Superficie : {stats?.totalSize}</Text>
      </View>

      {/* KPIs Grid */}
      <View style={styles.grid}>
        <View style={styles.gridItem}>
          <View style={[styles.iconBox, { backgroundColor: "#D1FAE5" }]}>
            <Sprout color="#059669" size={20} />
          </View>
          <View>
            <Text style={styles.kpiLabel}>Santé du sol</Text>
            <Text style={styles.kpiValue}>{stats?.solHealth}%</Text>
          </View>
        </View>

        <View style={styles.gridItem}>
          <View style={[styles.iconBox, { backgroundColor: "#DBEAFE" }]}>
            <Droplets color="#2563EB" size={20} />
          </View>
          <View>
            <Text style={styles.kpiLabel}>Humidité</Text>
            <Text style={styles.kpiValue}>{stats?.humidity}%</Text>
          </View>
        </View>

        <View style={styles.gridItem}>
          <View style={[styles.iconBox, { backgroundColor: "#FFEDD5" }]}>
            <Thermometer color="#EA580C" size={20} />
          </View>
          <View>
            <Text style={styles.kpiLabel}>Terre</Text>
            <Text style={styles.kpiValue}>{stats?.temperature}°C</Text>
          </View>
        </View>

        <View style={styles.gridItem}>
          <View style={[styles.iconBox, { backgroundColor: "#FEF3C7" }]}>
            <Combine color="#B45309" size={20} />
          </View>
          <View>
            <Text style={styles.kpiLabel}>Type Sol</Text>
            <Text style={styles.kpiValue} numberOfLines={1}>
              {stats?.soilType}
            </Text>
          </View>
        </View>
      </View>

      {/* En terre actuellement */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Actuellement en terre</Text>
        <View style={styles.vegGrid}>
          {vegs.map((veg: any) => (
            <View key={veg.id} style={styles.vegCard}>
              <View style={styles.vegIconBox}>
                <Sprout color="#059669" size={24} />
              </View>
              <Text style={styles.vegName} numberOfLines={1}>
                {veg.name}
              </Text>
              <View style={styles.vegStatusBox}>
                <Text style={styles.vegStatusText}>{veg.status}</Text>
              </View>
            </View>
          ))}
        </View>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#F5F5F0", padding: 16 },
  center: { flex: 1, justifyContent: "center", alignItems: "center" },
  headerInfo: {
    backgroundColor: "#059669",
    padding: 20,
    borderRadius: 16,
    marginBottom: 24,
  },
  headerTitle: { color: "#fff", fontSize: 20, fontWeight: "bold" },
  headerSub: { color: "#D1FAE5", fontSize: 14, marginTop: 4 },
  grid: {
    flexDirection: "row",
    flexWrap: "wrap",
    justifyContent: "space-between",
    marginBottom: 24,
  },
  gridItem: {
    width: "48%",
    backgroundColor: "#fff",
    padding: 16,
    borderRadius: 16,
    flexDirection: "row",
    alignItems: "center",
    marginBottom: 16,
    borderWidth: 1,
    borderColor: "#ECFDF5",
  },
  iconBox: { padding: 8, borderRadius: 999, marginRight: 12 },
  kpiLabel: { fontSize: 12, color: "#6B7280" },
  kpiValue: { fontSize: 16, fontWeight: "bold", color: "#065f46" },
  section: { marginBottom: 24 },
  sectionTitle: {
    fontSize: 18,
    fontWeight: "bold",
    color: "#065f46",
    marginBottom: 16,
  },
  vegGrid: {
    flexDirection: "row",
    flexWrap: "wrap",
    justifyContent: "space-between",
  },
  vegCard: {
    width: "48%",
    backgroundColor: "#fff",
    padding: 16,
    borderRadius: 16,
    alignItems: "center",
    marginBottom: 16,
    borderWidth: 1,
    borderColor: "#ECFDF5",
  },
  vegIconBox: {
    width: 48,
    height: 48,
    backgroundColor: "#ECFDF5",
    borderRadius: 24,
    justifyContent: "center",
    alignItems: "center",
    marginBottom: 12,
  },
  vegName: { fontWeight: "bold", fontSize: 14, textAlign: "center" },
  vegStatusBox: {
    backgroundColor: "#ECFDF5",
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 999,
    marginTop: 8,
  },
  vegStatusText: { color: "#059669", fontSize: 10, fontWeight: "bold" },
});
