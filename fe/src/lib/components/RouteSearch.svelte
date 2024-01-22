<script lang="ts">
  import * as L from "leaflet";
  import { API_BASE_URL, type Route, type APIResponse } from "../../api";
  import RouteSearchInput from "./RouteSearchInput.svelte";

  export let map: L.Map;

  let from: number;
  let to: number;

  async function fetchRoute() {
    const res = await fetch(
      API_BASE_URL + `/api/v1/address/route?source=${from}&dest=${to}`
    );
    const response = (await res.json()) as APIResponse;

    if (response.data && response.data.route) {
      const route = response.data as Route;
      if (!route || !route.route || !route.route.length) return;

      const nodes = route.route.map((rr) => [
        rr.lat,
        rr.lon,
      ]) as L.LatLngExpression[];

      L.polyline(nodes).setStyle({ color: "red", weight: 8 }).addTo(map);
      const first = route.route[0];
      const last = route.route[route.route.length - 1];

      const c1 = L.latLng(first.lat, first.lon);
      const c2 = L.latLng(last.lat, last.lon);

      L.marker(c1).addTo(map);
      L.marker(c2).addTo(map);

      const bounds = L.latLngBounds(c1, c2);

      map.panInsideBounds(bounds);
    }
  }
</script>

<div class="flex gap-4 items-end justify-center">
  <RouteSearchInput bind:value={from} label="from" />
  <RouteSearchInput bind:value={to} label="to" />
  <button
    class="bg-blue-600 rounded p-2 px-4 text-white border border-blue-800 font-bold"
    on:click={fetchRoute}>Route</button
  >
</div>
