import { Bell, ChevronRight, MapPin, Shield, User } from "lucide-react-native";
import { useState } from "react";
import { StyleSheet, Switch, Text, TouchableOpacity, View } from "react-native";

export default function SettingsScreen() {
  const [notifications, setNotifications] = useState(true);

  return (
    <View style={styles.container}>
      <Text style={styles.pageTitle}>Paramètres</Text>

      {/* Profil section */}
      <View style={styles.profileCard}>
        <View style={styles.avatar}>
          <User color="#059669" size={32} />
        </View>
        <View>
          <Text style={styles.profileName}>Jardinier Amateur</Text>
          <Text style={styles.profileDate}>Membre depuis Mai 2026</Text>
        </View>
      </View>

      <View style={styles.settingsGroup}>
        <View style={styles.settingItem}>
          <View style={styles.settingRow}>
            <Bell color="#10B981" size={20} style={styles.settingIcon} />
            <Text style={styles.settingText}>Notifications de rappel</Text>
          </View>
          <Switch
            value={notifications}
            onValueChange={setNotifications}
            trackColor={{ false: "#D1D5DB", true: "#10B981" }}
            thumbColor="#fff"
          />
        </View>

        <TouchableOpacity style={styles.settingItem}>
          <View style={styles.settingRow}>
            <MapPin color="#10B981" size={20} style={styles.settingIcon} />
            <Text style={styles.settingText}>Localisation du potager</Text>
          </View>
          <ChevronRight color="#9CA3AF" size={20} />
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.settingItem, { borderBottomWidth: 0 }]}
        >
          <View style={styles.settingRow}>
            <Shield color="#10B981" size={20} style={styles.settingIcon} />
            <Text style={styles.settingText}>Confidentialité</Text>
          </View>
          <ChevronRight color="#9CA3AF" size={20} />
        </TouchableOpacity>
      </View>

      <TouchableOpacity style={styles.logoutButton}>
        <Text style={styles.logoutText}>Déconnexion</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#F5F5F0", padding: 16 },
  pageTitle: {
    fontSize: 24,
    fontWeight: "bold",
    color: "#065f46",
    marginBottom: 24,
  },
  profileCard: {
    backgroundColor: "#fff",
    padding: 16,
    borderRadius: 16,
    flexDirection: "row",
    alignItems: "center",
    marginBottom: 24,
    borderWidth: 1,
    borderColor: "#ECFDF5",
  },
  avatar: {
    width: 64,
    height: 64,
    borderRadius: 32,
    backgroundColor: "#D1FAE5",
    justifyContent: "center",
    alignItems: "center",
    marginRight: 16,
  },
  profileName: { fontSize: 18, fontWeight: "bold", color: "#1F2937" },
  profileDate: { fontSize: 14, color: "#6B7280", marginTop: 4 },
  settingsGroup: {
    backgroundColor: "#fff",
    borderRadius: 16,
    borderWidth: 1,
    borderColor: "#ECFDF5",
    overflow: "hidden",
  },
  settingItem: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: "#F3F4F6",
  },
  settingRow: { flexDirection: "row", alignItems: "center" },
  settingIcon: { marginRight: 12 },
  settingText: { fontSize: 16, color: "#374151", fontWeight: "500" },
  logoutButton: {
    backgroundColor: "#FEF2F2",
    padding: 16,
    borderRadius: 16,
    alignItems: "center",
    marginTop: 32,
  },
  logoutText: { color: "#EF4444", fontSize: 16, fontWeight: "bold" },
});
