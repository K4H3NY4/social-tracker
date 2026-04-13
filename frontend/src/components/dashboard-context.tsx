"use client";

import {
  createContext,
  useContext,
  useEffect,
  useState,
  useCallback,
  type ReactNode,
} from "react";
import type { Client, PlatformCompliance } from "@/types";
import {
  getClients,
  getClient,
  getFacebookCompliance,
  getInstagramCompliance,
  getTikTokCompliance,
  normaliseFacebook,
  normaliseInstagram,
  normaliseTikTok,
} from "@/lib/api";
import { mockClients, mockFacebookCompliance, mockInstagramCompliance, mockTikTokCompliance } from "@/lib/mock-data";

export interface DashboardData {
  facebook: PlatformCompliance | null;
  instagram: PlatformCompliance | null;
  tiktok: PlatformCompliance | null;
}

interface DashboardContextValue {
  /** List of clients from backend (falls back to mock) */
  clients: Client[];
  /** Currently selected client */
  selectedClient: Client | null;
  setSelectedClientId: (id: number) => void;
  /** Date range */
  startDate: string;
  endDate: string;
  setStartDate: (d: string) => void;
  setEndDate: (d: string) => void;
  /** Platform compliance data */
  data: DashboardData;
  /** Loading state */
  loading: boolean;
  /** Error message if API fails */
  error: string | null;
  /** Re-fetch data */
  refresh: () => void;
}

const DashboardContext = createContext<DashboardContextValue>({
  clients: [],
  selectedClient: null,
  setSelectedClientId: () => {},
  startDate: "",
  endDate: "",
  setStartDate: () => {},
  setEndDate: () => {},
  data: { facebook: null, instagram: null, tiktok: null },
  loading: false,
  error: null,
  refresh: () => {},
});

export function useDashboard() {
  return useContext(DashboardContext);
}

export function DashboardProvider({ children }: { children: ReactNode }) {
  const [clients, setClients] = useState<Client[]>([]);
  const [selectedClientId, setSelectedClientId] = useState<number | null>(null);
  const [startDate, setStartDate] = useState("2026-03-01");
  const [endDate, setEndDate] = useState("2026-03-31");
  const [data, setData] = useState<DashboardData>({
    facebook: null,
    instagram: null,
    tiktok: null,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [usingMock, setUsingMock] = useState(false);

  const selectedClient = clients.find((c) => c.id === selectedClientId) ?? null;

  // Load clients from API on mount
  useEffect(() => {
    let cancelled = false;
    (async () => {
      const res = await getClients();
      if (cancelled) return;
      if (!res.error && res.data?.clients?.length) {
        setClients(res.data.clients);
        setSelectedClientId(res.data.clients[0].id);
        setUsingMock(false);
      } else {
        // Fallback to mock clients
        setClients(mockClients);
        setSelectedClientId(mockClients[0].id);
        setUsingMock(true);
      }
    })();
    return () => { cancelled = true; };
  }, []);

  // Fetch compliance data when client or dates change
  const fetchData = useCallback(async () => {
    if (!selectedClient) return;

    // If using mock data, set mock compliance directly
    if (usingMock) {
      setData({
        facebook: mockFacebookCompliance,
        instagram: mockInstagramCompliance,
        tiktok: mockTikTokCompliance,
      });
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Fetch full client record (with complete contract) in parallel with compliance data
      const [clientRes, fbRes, igRes, ttRes] = await Promise.all([
        getClient(selectedClient.id),
        selectedClient.facebook
          ? getFacebookCompliance(selectedClient.facebook, startDate, endDate)
          : Promise.resolve({ data: null, error: undefined, status: 0 }),
        selectedClient.instagram
          ? getInstagramCompliance(selectedClient.instagram, startDate, endDate)
          : Promise.resolve({ data: null, error: undefined, status: 0 }),
        selectedClient.tiktok
          ? getTikTokCompliance(selectedClient.tiktok, startDate, endDate)
          : Promise.resolve({ data: null, error: undefined, status: 0 }),
      ]);

      // Enrich client with full contract if available
      if (clientRes.data && !clientRes.error) {
        setClients((prev) =>
          prev.map((c) => (c.id === selectedClient.id ? { ...c, contract: clientRes.data.contract } : c))
        );
      }

      setData({
        facebook: fbRes.data && !fbRes.error ? normaliseFacebook(fbRes.data) : null,
        instagram: igRes.data && !igRes.error ? normaliseInstagram(igRes.data) : null,
        tiktok: ttRes.data && !ttRes.error ? normaliseTikTok(ttRes.data) : null,
      });

      // Show warning if all failed
      if (fbRes.error && igRes.error && ttRes.error) {
        setError("Could not reach backend — showing cached data");
      }
    } catch {
      setError("Network error — check if the backend is running");
    } finally {
      setLoading(false);
    }
  }, [selectedClient, startDate, endDate, usingMock]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return (
    <DashboardContext.Provider
      value={{
        clients,
        selectedClient,
        setSelectedClientId,
        startDate,
        endDate,
        setStartDate,
        setEndDate,
        data,
        loading,
        error,
        refresh: fetchData,
      }}
    >
      {children}
    </DashboardContext.Provider>
  );
}
