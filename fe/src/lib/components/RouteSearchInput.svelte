<script lang="ts">
  import { API_BASE_URL } from "../../api";
  import type { APIResponse, POIOption } from "../../api";

  export let value: number;
  export let label: string;

  let search = "";
  let timer: number;
  let options: POIOption[] = [];
  let listElem: HTMLElement;
  let hidden: boolean = true;

  // debounce
  function setSearch(t: Event) {
    let v = (t.target! as any).value as string;
    clearTimeout(timer);
    timer = setTimeout(async () => {
      search = v;
      if (!search || search == "") {
        options = [];
        return;
      }
      await fetchOptions();
    }, 750);
  }

  function selectOption(opt: POIOption) {
    search = opt.value;
    value = opt.id;
  }

  async function fetchOptions() {
    const res = await fetch(API_BASE_URL + "/api/v1/address?search=" + search);
    const response = (await res.json()) as APIResponse;
    options = response.data as POIOption[];
  }
</script>

<div class="relative">
  <ul
    bind:this={listElem}
    class="
      absolute flex flex-col p-2 gap-2 bg-white shadow
      left-0 top-[-22rem] min-h-[20rem] max-h-[20rem] w-[18rem]
      overflow-y-auto text-left
      {hidden ? 'hidden' : ''}"
  >
    {#each options as opt}
      <li class="text-start">
        <button class="text-start" on:click={() => selectOption(opt)}>
          {opt.value}
        </button>
      </li>
    {/each}
  </ul>
  <label for="route-search-input={label}" class="text-left">
    <span>{label}</span>
    <input
      id="route-search-input={label}"
      class="block border border-slate-400 p-2 rounded w-[18rem]"
      type="text"
      placeholder="search..."
      on:focus={() => (hidden = false)}
      on:blur={() =>
        setTimeout(() => {
          hidden = true;
        }, 200)}
      bind:value={search}
      on:input={setSearch}
    />
  </label>
</div>
