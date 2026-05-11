import { Calendar, Droplets, Info, Search, Sun } from "lucide-react-native";
import { useEffect, useState } from "react";
import {
    ActivityIndicator,
    ScrollView,
    StyleSheet,
    Text,
    TextInput,
    View,
} from "react-native";

export default function LibraryScreen() {
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");

  useEffect(() => {
    fetch("http://172.23.119.189:8000/api/library")
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

  const filteredLibrary = data.filter((item) =>
    item.name.toLowerCase().includes(searchTerm.toLowerCase()),
  );

  return (
    <View style={styles.container}>
      {/* Search Bar */}
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
            <View key={item.id} style={styles.card}>
              <View style={styles.cardHeader}>
                <Text style={styles.cardTitle}>{item.name}</Text>
              </View>
              <View style={styles.cardBody}>
                <View style={styles.row}>
                  <Calendar color="#10B981" size={16} style={styles.rowIcon} />
                  <Text style={styles.rowText}>
                    Période : <Text style={styles.bold}>{item.period}</Text>
                  </Text>
                </View>
                <View style={styles.row}>
                  <Sun color="#F59E0B" size={16} style={styles.rowIcon} />
                  <Text style={styles.rowText}>
                    Saison : <Text style={styles.bold}>{item.season}</Text>
                  </Text>
                </View>
                <View style={styles.row}>
                  <Droplets color="#3B82F6" size={16} style={styles.rowIcon} />
                  <Text style={styles.rowText}>
                    Eau : <Text style={styles.bold}>{item.waterNeeds}</Text>
                  </Text>
                </View>

                <View style={styles.tipsBox}>
                  <Info
                    color="#059669"
                    size={16}
                    style={{ marginTop: 2, marginRight: 8 }}
                  />
                  <Text style={styles.tipsText}>
                    <Text style={{ fontWeight: "bold" }}>Conseil : </Text>
                    {item.tips}
                  </Text>
                </View>
              </View>
            </View>
          ))}

          {filteredLibrary.length === 0 && (
            <Text style={styles.emptyText}>
              Aucun légume trouvé pour "{searchTerm}"
            </Text>
          )}
        </ScrollView>
      )}
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
  tipsBox: {
    flexDirection: "row",
    backgroundColor: "rgba(209, 250, 229, 0.5)",
    padding: 12,
    borderRadius: 12,
    marginTop: 12,
    borderColor: "#D1FAE5",
    borderWidth: 1,
  },
  tipsText: { color: "#065f46", fontSize: 12, flex: 1, lineHeight: 18 },
  emptyText: { textAlign: "center", color: "#6B7280", marginTop: 40 },
});
