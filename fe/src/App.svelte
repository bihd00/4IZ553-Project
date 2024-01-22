<script lang="ts">
  import * as turf from "@turf/turf";
  import * as L from "leaflet";
  import "leaflet/dist/leaflet.css";
  import "@geoman-io/leaflet-geoman-free";
  import "@geoman-io/leaflet-geoman-free/dist/leaflet-geoman.css";
  import type { SvelteComponent } from "svelte";
  import { API_BASE_URL, type PointOfInterest } from "./api";
  import FisLogoEN from "./lib/assets/FIS_logo_en.png";
  import RouteSearch from "./lib/components/RouteSearch.svelte";

  interface Map extends L.Map {}

  const initialView = [50.0737633, 14.4349126] as L.LatLngExpression;
  const initialZoom = 13;
  const popup = L.popup();

  let map: Map | null;

  function createMap(container: HTMLElement) {
    let m = L.map(container, { preferCanvas: true }).setView(
      initialView,
      initialZoom
    );
    L.tileLayer(
      "https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png",
      {
        attribution: `&copy;<a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap</a>,
	        &copy;<a href="https://carto.com/attributions" target="_blank">CARTO</a>`,
        subdomains: "abcd",
        maxZoom: 35,
        minZoom: 2,
      }
    ).addTo(m);
    return m;
  }

  let toolbar = new L.Control({ position: "topright" });
  let toolbarComponent: SvelteComponent | null;
  toolbar.onAdd = (map: L.Map) => {
    let div = L.DomUtil.create("div");
    return div;
  };
  toolbar.onRemove = () => {
    if (toolbarComponent) {
      toolbarComponent.$destroy();
      toolbarComponent = null;
    }
  };

  function mapAction(container: HTMLElement) {
    map = createMap(container);
    toolbar.addTo(map);

    map.on("pm:create", handleShape as any);

    map.pm.addControls({
      position: "topleft",
      drawCircleMarker: false,
      drawPolyline: true,
      drawText: false,
      editMode: false,
      cutPolygon: false,
      rotateMode: false,
    });

    return {
      destroy: () => {
        toolbar.remove();
        if (map) {
          map.remove();
        }
        map = null;
      },
    };
  }

  function resizeMap() {
    if (map) {
      map.invalidateSize();
    }
  }

  async function handleShape({ shape, layer }: { shape: string; layer: any }) {
    if (shape === "Circle") await handleCircle(layer);
    if (shape === "Rectangle") handleRectangle(layer);
    if (shape === "Polygon") handlePolygon(layer);
  }

  async function handleCircle(layer: L.Circle) {
    const radius = layer.getRadius();
    const circleCenterPoint = layer.toGeoJSON();
    const qs = new URLSearchParams({
      radius: `${radius}`,
      lat: `${circleCenterPoint.geometry.coordinates[1]}`,
      lon: `${circleCenterPoint.geometry.coordinates[0]}`,
    });
    const resp = await fetch(
      API_BASE_URL + "/api/v1/poi/circle?" + qs.toString()
    );
    const response = await resp.json();
    if (response.data) {
      const data = response.data as PointOfInterest[];
      for (const poi of data) {
        L.marker([poi.latitude, poi.longitude]).addTo(map!).bindPopup(poi.name);
      }
    }
  }

  async function handleRectangle(layer: L.Rectangle) {
    const bbox = layer.toGeoJSON();
    const turfbbox = turf.polygon(bbox as any);
    const coords = (turfbbox.geometry.coordinates as any).geometry.coordinates;
    const qs = new URLSearchParams({
      lat_min: `${coords[0][0][1]}`,
      lon_min: `${coords[0][0][0]}`,
      lat_max: `${coords[0][2][1]}`,
      lon_max: `${coords[0][2][0]}`,
    });
    const resp = await fetch(
      API_BASE_URL + "/api/v1/poi/polygon?" + qs.toString()
    );
    const response = await resp.json();
    if (response.data) {
      const data = response.data as PointOfInterest[];
      for (const poi of data) {
        L.marker([poi.latitude, poi.longitude]).addTo(map!).bindPopup(poi.name);
      }
    }
  }

  async function handlePolygon(layer: L.Polygon) {
    const poly = layer.toGeoJSON();
    const bbox = turf.bbox(poly as any) as any as number[];
    const qs = new URLSearchParams({
      lat_min: `${bbox[1]}`,
      lon_min: `${bbox[0]}`,
      lat_max: `${bbox[3]}`,
      lon_max: `${bbox[1]}`,
    });
    const resp = await fetch(
      API_BASE_URL + "/api/v1/poi/polygon?" + qs.toString()
    );
    const response = await resp.json();
    if (response.data) {
      const data = response.data as PointOfInterest[];
      const points = data.map((p) => [p.longitude, p.latitude, p.name]);
      // @ts-ignore
      const poisWithin = turf.pointsWithinPolygon(turf.points(points), poly);
      for (const poi of poisWithin.features) {
        L.marker([poi.geometry.coordinates[1], poi.geometry.coordinates[0]])
          .addTo(map!)
          .bindPopup(poi.geometry.coordinates[2]);
      }
    }
  }
</script>

<svelte:window on:resize={resizeMap} />

<main class="relative w-screen h-screen overflow-hidden">
  <div
    class="map w-full h-full text-center bg-slate-600 text-slate-400"
    use:mapAction
  />
  <div class="absolute bottom-0 left-0 z-[99999999] w-full bg-white p-4">
    {#if map}
      <RouteSearch {map} />
    {/if}
  </div>
  <div class="fixed top-2 right-2 z-[99999999]">
    <img
      src={FisLogoEN}
      alt="FIS logo"
      width="64"
      height="64"
      class="ms-auto"
    />
  </div>
</main>
