export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:42068";

export type APIResponse = {
  success: true;
  error: false;
  message: string | null;
  errors: { message: string; type: string }[] | null;
  data: any;
  timestamp: string;
};

export type LatLon = {
  lat: number;
  lon: number;
};

export type POIOption = {
  value: string;
  score: number;
  label: string;
  id: number;
};

export type Route = {
  route: LatLon[];
};

export type PointOfInterest = {
  latitude: number;
  longitude: number;
  name: string;
  categories: string[];
  tags: Record<string, any>;
};
