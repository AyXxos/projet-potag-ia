import {
    DarkTheme,
    DefaultTheme,
    ThemeProvider,
} from "@react-navigation/native";
import AsyncStorage from "@react-native-async-storage/async-storage";
import * as Location from "expo-location";
import { Stack } from "expo-router";
import { StatusBar } from "expo-status-bar";
import { useEffect } from "react";
import { Alert, Linking } from "react-native";
import "react-native-reanimated";

import { useColorScheme } from "@/hooks/use-color-scheme";

export const unstable_settings = {
  anchor: "(tabs)",
};

export default function RootLayout() {
  const colorScheme = useColorScheme();
  const locationEnabledKey = "potagia.location.enabled";
  const locationStatusKey = "potagia.location.status";
  const locationValueKey = "potagia.location.value";
  const locationUpdatedKey = "potagia.location.updatedAt";

  useEffect(() => {
    const requestLocationOnStart = async () => {
      try {
        const enabledValue = await AsyncStorage.getItem(locationEnabledKey);
        const enabled = enabledValue !== "false";
        if (!enabled) {
          return;
        }

        const response = await Location.requestForegroundPermissionsAsync();
        await AsyncStorage.setItem(locationStatusKey, response.status);

        if (response.status !== "granted") {
          await AsyncStorage.removeItem(locationValueKey);
          await AsyncStorage.removeItem(locationUpdatedKey);
        }

        if (response.status === "granted") {
          const position = await Location.getCurrentPositionAsync({
            accuracy: Location.Accuracy.Balanced,
          });
          const value = `${position.coords.latitude.toFixed(4)}, ${position.coords.longitude.toFixed(4)}`;
          await AsyncStorage.setItem(locationValueKey, value);
          await AsyncStorage.setItem(locationUpdatedKey, new Date().toISOString());
        }

        if (response.status !== "granted" && response.canAskAgain === false) {
          Alert.alert(
            "Autorisation localisation",
            "Veuillez autoriser la localisation dans les reglages pour activer les recommandations.",
            [
              { text: "Annuler", style: "cancel" },
              { text: "Ouvrir les reglages", onPress: () => Linking.openSettings() },
            ],
          );
        }
      } catch (error) {
        console.error(error);
      }
    };

    requestLocationOnStart();
  }, []);

  return (
    <ThemeProvider value={colorScheme === "dark" ? DarkTheme : DefaultTheme}>
      <Stack>
        <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
        <Stack.Screen
          name="modal"
          options={{ presentation: "modal", title: "Modal" }}
        />
      </Stack>
      <StatusBar style="auto" />
    </ThemeProvider>
  );
}
