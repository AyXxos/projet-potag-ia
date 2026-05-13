import AsyncStorage from "@react-native-async-storage/async-storage";
import { useFocusEffect } from "@react-navigation/native";
import * as Location from "expo-location";
import { Bell, MapPin, Shield, User } from "lucide-react-native";
import { useCallback, useState } from "react";
import {
    Pressable,
    ScrollView,
    StyleSheet,
    Switch,
    Text,
    View,
} from "react-native";

export default function SettingsScreen() {
  const [notifications, setNotifications] = useState(true);
  const [locationConsent, setLocationConsent] = useState(false);
  const [locationStatus, setLocationStatus] = useState("Non demande");
  const [locationValue, setLocationValue] = useState("Non definie");
  const [locationUpdatedAt, setLocationUpdatedAt] = useState("Non defini");
  const [analyticsConsent, setAnalyticsConsent] = useState(false);
  const [personalizationConsent, setPersonalizationConsent] = useState(true);
  const locationEnabledKey = "potagia.location.enabled";
  const locationStatusKey = "potagia.location.status";
  const locationValueKey = "potagia.location.value";
  const locationUpdatedKey = "potagia.location.updatedAt";

  const loadLocationSettings = useCallback(async () => {
    const enabledValue = await AsyncStorage.getItem(locationEnabledKey);
    const statusValue = await AsyncStorage.getItem(locationStatusKey);
    const storedValue = await AsyncStorage.getItem(locationValueKey);
    const storedUpdated = await AsyncStorage.getItem(locationUpdatedKey);

    setLocationConsent(enabledValue !== "false");
    setLocationStatus(
      statusValue === "granted"
        ? "Autorisee"
        : statusValue === "denied"
          ? "Refusee"
          : statusValue === "disabled"
            ? "Desactivee"
            : "Non demande",
    );
    setLocationValue(storedValue ?? "Non definie");
    setLocationUpdatedAt(
      storedUpdated
        ? new Date(storedUpdated).toLocaleString("fr-FR")
        : "Non defini",
    );
  }, []);

  useFocusEffect(
    useCallback(() => {
      loadLocationSettings();
    }, [loadLocationSettings]),
  );

  const requestLocation = async () => {
    try {
      const { status } = await Location.requestForegroundPermissionsAsync();
      if (status !== "granted") {
        await AsyncStorage.setItem(locationStatusKey, status);
        await AsyncStorage.removeItem(locationValueKey);
        await AsyncStorage.removeItem(locationUpdatedKey);
        setLocationStatus("Refusee");
        setLocationConsent(false);
        setLocationValue("Non definie");
        setLocationUpdatedAt("Non defini");
        return;
      }

      const position = await Location.getCurrentPositionAsync({
        accuracy: Location.Accuracy.Balanced,
      });
      setLocationStatus("Autorisee");
      const value = `${position.coords.latitude.toFixed(4)}, ${position.coords.longitude.toFixed(4)}`;
      const timestamp = new Date().toISOString();
      await AsyncStorage.setItem(locationStatusKey, status);
      await AsyncStorage.setItem(locationValueKey, value);
      await AsyncStorage.setItem(locationUpdatedKey, timestamp);
      setLocationValue(value);
      setLocationUpdatedAt(new Date(timestamp).toLocaleString("fr-FR"));
      setLocationConsent(true);
    } catch (error) {
      console.error(error);
      setLocationStatus("Erreur");
      setLocationConsent(false);
    }
  };

  const handleLocationToggle = async (value: boolean) => {
    if (value) {
      await AsyncStorage.setItem(locationEnabledKey, "true");
      await requestLocation();
      return;
    }

    await AsyncStorage.setItem(locationEnabledKey, "false");
    await AsyncStorage.setItem(locationStatusKey, "disabled");
    await AsyncStorage.removeItem(locationValueKey);
    await AsyncStorage.removeItem(locationUpdatedKey);
    setLocationConsent(false);
    setLocationStatus("Desactivee");
    setLocationValue("Non definie");
    setLocationUpdatedAt("Non defini");
  };

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={styles.contentContainer}
    >
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

        <View style={styles.settingItem}>
          <View style={styles.settingRow}>
            <MapPin color="#10B981" size={20} style={styles.settingIcon} />
            <View>
              <Text style={styles.settingText}>Localisation du potager</Text>
              <Text style={styles.settingSubText}>
                Statut : {locationStatus} | {locationValue}
              </Text>
              <Text style={styles.settingSubText}>
                Derniere maj : {locationUpdatedAt}
              </Text>
            </View>
          </View>
          <Switch
            value={locationConsent}
            onValueChange={handleLocationToggle}
            trackColor={{ false: "#D1D5DB", true: "#10B981" }}
            thumbColor="#fff"
          />
        </View>

        <View style={[styles.settingItem, { borderBottomWidth: 0 }]}>
          <View style={styles.settingRow}>
            <Shield color="#10B981" size={20} style={styles.settingIcon} />
            <Text style={styles.settingText}>Confidentialite (RGPD)</Text>
          </View>
        </View>
      </View>

      <View style={styles.sectionCard}>
        <Text style={styles.sectionTitle}>Consentements</Text>
        <Text style={styles.sectionDesc}>
          Nous ne collectons la localisation que pour les recommandations meteo
          et le calendrier. Vous pouvez retirer l'autorisation a tout moment
          depuis les reglages du systeme.
        </Text>
        <View style={styles.settingItemInline}>
          <Text style={styles.settingText}>Localisation (necessaire)</Text>
          <Switch
            value={locationConsent}
            onValueChange={handleLocationToggle}
            trackColor={{ false: "#D1D5DB", true: "#10B981" }}
            thumbColor="#fff"
          />
        </View>
        <View style={styles.settingItemInline}>
          <Text style={styles.settingText}>Personnalisation</Text>
          <Switch
            value={personalizationConsent}
            onValueChange={setPersonalizationConsent}
            trackColor={{ false: "#D1D5DB", true: "#10B981" }}
            thumbColor="#fff"
          />
        </View>
        <View style={styles.settingItemInline}>
          <Text style={styles.settingText}>Analytique anonyme</Text>
          <Switch
            value={analyticsConsent}
            onValueChange={setAnalyticsConsent}
            trackColor={{ false: "#D1D5DB", true: "#10B981" }}
            thumbColor="#fff"
          />
        </View>
      </View>

      <View style={styles.sectionCard}>
        <Text style={styles.sectionTitle}>Vos droits (RGPD)</Text>
        <Text style={styles.sectionDesc}>
          Vous pouvez demander l'acces, la rectification, l'effacement ou la
          portabilite de vos donnees.
        </Text>
        <Pressable style={styles.actionButton}>
          <Text style={styles.actionButtonText}>Exporter mes donnees</Text>
        </Pressable>
        <Pressable style={[styles.actionButton, styles.deleteButton]}>
          <Text style={[styles.actionButtonText, styles.deleteButtonText]}>
            Supprimer mes donnees
          </Text>
        </Pressable>
      </View>

      <Pressable style={styles.logoutButton}>
        <Text style={styles.logoutText}>Déconnexion</Text>
      </Pressable>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#F5F5F0" },
  contentContainer: { padding: 16, paddingBottom: 40 },
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
  settingSubText: { fontSize: 12, color: "#6B7280", marginTop: 4 },
  sectionCard: {
    backgroundColor: "#fff",
    borderRadius: 16,
    borderWidth: 1,
    borderColor: "#ECFDF5",
    padding: 16,
    marginTop: 20,
  },
  sectionTitle: { fontSize: 16, fontWeight: "bold", color: "#065f46" },
  sectionDesc: { fontSize: 13, color: "#6B7280", marginTop: 8 },
  settingItemInline: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    marginTop: 12,
  },
  actionButton: {
    marginTop: 12,
    backgroundColor: "#ECFDF5",
    borderRadius: 12,
    paddingVertical: 10,
    alignItems: "center",
  },
  actionButtonText: { color: "#047857", fontWeight: "bold" },
  deleteButton: { backgroundColor: "#FEF2F2" },
  deleteButtonText: { color: "#EF4444" },
  logoutButton: {
    backgroundColor: "#FEF2F2",
    padding: 16,
    borderRadius: 16,
    alignItems: "center",
    marginTop: 32,
  },
  logoutText: { color: "#EF4444", fontSize: 16, fontWeight: "bold" },
});
