import { Calendar, Search, Sun } from "lucide-react-native";
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

export default function LibraryScreen() {
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedItem, setSelectedItem] = useState<any | null>(null);
  const [modalVisible, setModalVisible] = useState(false);

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

  const formatDayMonth = (value?: string) => {
    if (!value) {
      return "Non defini";
    }

    const dateValue = new Date(value);
    if (Number.isNaN(dateValue.getTime())) {
      return "Non defini";
    }

    return dateValue.toLocaleDateString("fr-FR", {
      day: "numeric",
      month: "long",
    });
  };

  const formatWeekRange = (start?: string, end?: string) => {
    const startLabel = formatDayMonth(start);
    const endLabel = formatDayMonth(end);

    if (startLabel === "Non defini" || endLabel === "Non defini") {
      return "Non defini";
    }

    return `${startLabel} au ${endLabel}`;
  };

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
            <Pressable
              key={item.id}
              style={styles.card}
              onPress={() => {
                setSelectedItem(item);
                setModalVisible(true);
              }}
            >
              <View style={styles.cardHeader}>
                <Text style={styles.cardTitle}>{item.name}</Text>
              </View>
              <View style={styles.cardBody}>
                <View style={styles.row}>
                  <Calendar color="#10B981" size={16} style={styles.rowIcon} />
                  <Text style={styles.rowText}>
                    Semaine :{" "}
                    <Text style={styles.bold}>
                      {formatWeekRange(item.plantingStart, item.plantingEnd)}
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

          {filteredLibrary.length === 0 && (
            <Text style={styles.emptyText}>
              Aucun légume trouvé pour "{searchTerm}"
            </Text>
          )}
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
            <Text style={styles.modalTitle}>
              {selectedItem?.name ?? "Legume"}
            </Text>
            <View style={styles.modalSection}>
              <Text style={styles.modalLabel}>Date de plantation</Text>
              <Text style={styles.modalValue}>
                {formatDayMonth(selectedItem?.plantingDate)}
              </Text>
            </View>
            <View style={styles.modalSection}>
              <Text style={styles.modalLabel}>Saison ideale</Text>
              <Text style={styles.modalValue}>
                {selectedItem?.season ?? "Non defini"}
              </Text>
            </View>
            <View style={styles.modalSection}>
              <Text style={styles.modalLabel}>Besoins en eau (par jour)</Text>
              <Text style={styles.modalValue}>
                {selectedItem?.waterNeeds ?? "Non defini"}
              </Text>
            </View>
            <View style={styles.modalSection}>
              <Text style={styles.modalLabel}>Conseils</Text>
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
  modalCard: { backgroundColor: "#fff", borderRadius: 16, padding: 20 },
  modalTitle: {
    fontSize: 18,
    fontWeight: "bold",
    color: "#065f46",
    marginBottom: 12,
  },
  modalSection: { marginBottom: 12 },
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
    paddingVertical: 10,
    borderRadius: 10,
    alignItems: "center",
  },
  modalCloseText: { color: "#fff", fontWeight: "bold" },
  emptyText: { textAlign: "center", color: "#6B7280", marginTop: 40 },
});
