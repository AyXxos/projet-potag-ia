import { Tabs } from "expo-router";
import { Home, Leaf, Search, Settings } from "lucide-react-native";

export default function TabLayout() {
  return (
    <Tabs
      screenOptions={{
        tabBarActiveTintColor: "#047857", // emerald-700
        tabBarInactiveTintColor: "#9CA3AF",
        tabBarStyle: {
          backgroundColor: "#ffffff",
          borderTopColor: "#E5E7EB",
        },
        headerStyle: { backgroundColor: "#047857" },
        headerTintColor: "#fff",
        title: "Potag'IA",
      }}
    >
      <Tabs.Screen
        name="index"
        options={{
          tabBarLabel: "Accueil",
          tabBarIcon: ({ color, size }) => <Home color={color} size={size} />,
        }}
      />
      <Tabs.Screen
        name="garden"
        options={{
          tabBarLabel: "Potager",
          tabBarIcon: ({ color, size }) => <Leaf color={color} size={size} />,
        }}
      />
      <Tabs.Screen
        name="library"
        options={{
          tabBarLabel: "Plantes",
          tabBarIcon: ({ color, size }) => <Search color={color} size={size} />,
        }}
      />
      <Tabs.Screen
        name="settings"
        options={{
          tabBarLabel: "Réglages",
          tabBarIcon: ({ color, size }) => (
            <Settings color={color} size={size} />
          ),
        }}
      />
    </Tabs>
  );
}
