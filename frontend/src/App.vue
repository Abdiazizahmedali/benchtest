<script setup>
import {
  Badge,
  Button,
  FeatherIcon,
  TabButtons,
  TextInput,
  createListResource,
  createResource,
} from 'frappe-ui'
import { computed, onMounted, onUnmounted, reactive, ref, watch } from 'vue'

// Shown until the visitor signs in and the ERP has selling prices to read.
const DEMO_MENU = [
  { id: 'tilapia-whole', group: 'Fish', name: 'Whole fried tilapia', desc: 'Lake fish, fried crisp, with kachumbari', price: 1200 },
  { id: 'tilapia-wet', group: 'Fish', name: 'Wet-fry tilapia', desc: 'Simmered in tomato and onion sauce', price: 1350 },
  { id: 'fish-fillet', group: 'Fish', name: 'Fish fillet', desc: 'Pan-seared with lemon butter', price: 950 },
  { id: 'ugali', group: 'Sides', name: 'Ugali', desc: 'Firm white maize meal', price: 100 },
  { id: 'sukuma', group: 'Sides', name: 'Sukuma wiki', desc: 'Sautéed collard greens', price: 150 },
  { id: 'chips', group: 'Sides', name: 'Chips', desc: 'Hand-cut, lightly salted', price: 200 },
  { id: 'soda', group: 'Drinks', name: 'Soda', desc: '300 ml, chilled', price: 80 },
  { id: 'juice', group: 'Drinks', name: 'Fresh passion juice', desc: 'Pressed daily', price: 250 },
  { id: 'chai', group: 'Drinks', name: 'Chai', desc: 'Spiced milk tea', price: 100 },
]
const STAGES = ['New', 'Preparing', 'Ready', 'Served']
const STAGE_THEME = { New: 'orange', Preparing: 'blue', Ready: 'green', Served: 'gray' }

// --- live data from the ERP --------------------------------------------------------
const ping = createResource({ url: 'ping', auto: true })
// Frappe sets a `user_id` cookie on every response ("Guest" when signed out).
const cookie = (name) =>
  decodeURIComponent(document.cookie.split('; ').find((c) => c.startsWith(name + '='))?.split('=')[1] || '')
const session = { data: cookie('user_id') || 'Guest' }
const signedIn = computed(() => session.data !== 'Guest')
const prices = createListResource({
  doctype: 'Item Price',
  fields: ['item_code', 'item_name', 'price_list_rate'],
  filters: { selling: 1 },
  orderBy: 'item_name asc',
  pageLength: 100,
})
watch(signedIn, (yes) => yes && prices.fetch(), { immediate: true })

const items = createListResource({
  doctype: 'Item',
  fields: ['name', 'item_group', 'description'],
  filters: { is_sales_item: 1, disabled: 0 },
  pageLength: 200,
})
watch(signedIn, (yes) => yes && items.fetch(), { immediate: true })
const erpMenu = computed(() => {
  const info = Object.fromEntries((items.data || []).map((i) => [i.name, i]))
  return (prices.data || []).map((p) => ({
    id: p.item_code,
    group: info[p.item_code]?.item_group || 'Menu',
    name: p.item_name || p.item_code,
    desc: (info[p.item_code]?.description || '').replace(/<[^>]*>/g, ''),
    price: p.price_list_rate,
  }))
})
const live = computed(() => erpMenu.value.length > 0)

// Orders placed while signed in become real Sales Orders in the ERP.
const today = new Date().toISOString().slice(0, 10)
const orders = createListResource({
  doctype: 'Sales Order',
  fields: ['name', 'po_no', 'grand_total', 'total_qty', 'creation'],
  filters: { transaction_date: today, docstatus: 0 },
  orderBy: 'creation desc',
  pageLength: 50,
})
watch(signedIn, (yes) => yes && orders.fetch(), { immediate: true })
const placeOrder = createResource({ url: 'cb_cb_demo.api.place_order', method: 'POST' })
const stageOf = reactive({})
const menu = computed(() => (live.value ? erpMenu.value : DEMO_MENU))
const source = computed(() =>
  live.value ? 'Live menu and prices from your ERP' : 'Sample menu — sign in to use your ERP',
)

const release = ref('…')
onMounted(async () => {
  try {
    const html = await (await fetch('/cb_release')).text()
    release.value = html.match(/id="cb-release">([^<]+)</)?.[1] ?? 'unknown'
  } catch {
    release.value = 'local'
  }
})

// --- ordering ----------------------------------------------------------------------
const group = ref('All')
const groups = computed(() => ['All', ...new Set(menu.value.map((m) => m.group))])
const search = ref('')
const table = ref('T1')
const order = reactive(new Map())
const tickets = ref([])
let nextTicket = 101

const kes = (n) => 'KES ' + Number(n || 0).toLocaleString('en-KE')
const visible = computed(() =>
  menu.value.filter(
    (m) => (group.value === 'All' || m.group === group.value) &&
      m.name.toLowerCase().includes(search.value.trim().toLowerCase()),
  ),
)
const lines = computed(() =>
  [...order.entries()].map(([id, qty]) => ({ ...menu.value.find((m) => m.id === id), qty })),
)
const itemCount = computed(() => lines.value.reduce((n, l) => n + l.qty, 0))
const total = computed(() => lines.value.reduce((n, l) => n + l.qty * l.price, 0))
const allTickets = computed(() =>
  live.value
    ? (orders.data || []).map((o) => ({
        no: o.name,
        table: o.po_no || '—',
        total: o.grand_total,
        items: [`${o.total_qty} item${o.total_qty === 1 ? '' : 's'}`],
        at: new Date(o.creation.replace(' ', 'T')).toLocaleTimeString('en-KE', { hour: '2-digit', minute: '2-digit' }),
        get stage() { return stageOf[o.name] || 'New' },
        set stage(v) { stageOf[o.name] = v },
      }))
    : tickets.value,
)
const byStage = computed(() =>
  Object.fromEntries(STAGES.map((s) => [s, allTickets.value.filter((t) => t.stage === s)])),
)
const takings = computed(() =>
  allTickets.value.filter((t) => t.stage === 'Served').reduce((n, t) => n + t.total, 0),
)

function add(item) { order.set(item.id, (order.get(item.id) || 0) + 1) }
function dec(id) {
  const q = (order.get(id) || 0) - 1
  q > 0 ? order.set(id, q) : order.delete(id)
}
async function place() {
  if (!itemCount.value) return
  if (live.value) {
    await placeOrder.submit({
      table: table.value,
      lines: lines.value.map((l) => ({ item_code: l.id, qty: l.qty })),
    })
    order.clear()
    await orders.reload()
    return
  }
  tickets.value.unshift({
    no: nextTicket++, table: table.value, stage: 'New', total: total.value,
    items: lines.value.map((l) => `${l.qty}× ${l.name}`),
    at: new Date().toLocaleTimeString('en-KE', { hour: '2-digit', minute: '2-digit' }),
  })
  order.clear()
}
function advance(t) {
  const i = STAGES.indexOf(t.stage)
  if (i < STAGES.length - 1) t.stage = STAGES[i + 1]
}

const now = ref(new Date())
const clock = setInterval(() => (now.value = new Date()), 1000)
onUnmounted(() => clearInterval(clock))
</script>

<template>
  <div class="min-h-screen bg-surface-gray-1 text-ink-gray-9">
    <header class="sticky top-0 z-10 border-b bg-surface-white">
      <div class="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-3 px-4 py-3">
        <div class="flex items-center gap-3">
          <div class="grid h-9 w-9 place-items-center rounded-lg bg-surface-gray-7 text-sm font-semibold text-ink-white">MO</div>
          <div>
            <h1 class="text-lg font-semibold leading-tight">Mama Oliech</h1>
            <p class="text-sm text-ink-gray-5">
              Front of house ·
              {{ now.toLocaleDateString('en-KE', { weekday: 'long', day: 'numeric', month: 'long' }) }}
            </p>
          </div>
        </div>
        <div class="flex flex-wrap items-center gap-2">
          <Badge :theme="ping.data === 'pong' ? 'green' : 'gray'" variant="subtle" size="lg">
            {{ ping.data === 'pong' ? 'ERP connected' : ping.loading ? 'Connecting…' : 'Offline preview' }}
          </Badge>
          <Badge theme="gray" variant="outline" size="lg">Release {{ release }}</Badge>
          <Button v-if="!signedIn" variant="subtle" :link="'/login?redirect-to=/cb'">
            <template #prefix><FeatherIcon name="log-in" class="h-4 w-4" /></template>
            Sign in
          </Button>
          <Badge v-else theme="blue" variant="subtle" size="lg">{{ session.data }}</Badge>
          <span class="ml-1 font-semibold tabular-nums">
            {{ now.toLocaleTimeString('en-KE', { hour: '2-digit', minute: '2-digit' }) }}
          </span>
        </div>
      </div>
    </header>

    <main class="mx-auto grid max-w-7xl gap-4 p-4 lg:grid-cols-[1.5fr_1fr]">
      <section class="rounded-xl border bg-surface-white p-4">
        <div class="mb-3 flex flex-wrap items-center justify-between gap-3">
          <div>
            <h2 class="text-base font-semibold">Menu</h2>
            <p class="text-sm text-ink-gray-5">{{ source }}</p>
          </div>
          <TextInput v-model="search" type="search" placeholder="Search dishes" class="w-56">
            <template #prefix><FeatherIcon name="search" class="h-4 w-4 text-ink-gray-5" /></template>
          </TextInput>
        </div>
        <TabButtons v-model="group" :buttons="groups.map((g) => ({ label: g, value: g }))" class="mb-3" />
        <div class="grid gap-2 sm:grid-cols-2 xl:grid-cols-3">
          <button
            v-for="m in visible"
            :key="m.id"
            class="relative flex flex-col items-start gap-1 rounded-lg border bg-surface-gray-1 p-3 text-left transition hover:border-outline-gray-4 active:scale-[.98]"
            @click="add(m)"
          >
            <span class="font-medium">{{ m.name }}</span>
            <span class="text-sm text-ink-gray-5">{{ m.desc }}</span>
            <span class="text-sm font-semibold text-ink-gray-8">{{ kes(m.price) }}</span>
            <Badge v-if="order.get(m.id)" theme="orange" variant="subtle" size="lg" class="absolute right-2 top-2">{{ order.get(m.id) }}</Badge>
          </button>
        </div>
        <p v-if="!visible.length" class="py-6 text-center text-sm text-ink-gray-5">No dishes match “{{ search }}”.</p>
      </section>

      <section class="flex flex-col rounded-xl border bg-surface-white p-4">
        <div class="mb-3 flex items-center justify-between">
          <h2 class="text-base font-semibold">Current order</h2>
          <select v-model="table" class="form-select rounded border-outline-gray-2 bg-surface-gray-2 py-1 text-sm">
            <option v-for="n in 12" :key="n" :value="'T' + n">Table {{ n }}</option>
            <option value="Takeaway">Takeaway</option>
          </select>
        </div>
        <ul v-if="lines.length" class="divide-y">
          <li v-for="l in lines" :key="l.id" class="grid grid-cols-[1fr_auto_90px] items-center gap-2 py-2 text-sm">
            <span>{{ l.name }}</span>
            <span class="flex items-center gap-1 tabular-nums">
              <Button size="sm" variant="ghost" icon="minus" aria-label="Remove one" @click="dec(l.id)" />
              {{ l.qty }}
              <Button size="sm" variant="ghost" icon="plus" aria-label="Add one" @click="add(l)" />
            </span>
            <span class="text-right tabular-nums">{{ kes(l.qty * l.price) }}</span>
          </li>
        </ul>
        <p v-else class="py-6 text-center text-sm text-ink-gray-5">Tap a dish to start an order.</p>
        <div class="mt-auto flex items-baseline justify-between pt-4 text-ink-gray-5">
          <span>{{ itemCount }} item{{ itemCount === 1 ? '' : 's' }}</span>
          <span class="text-2xl font-semibold text-ink-gray-9">{{ kes(total) }}</span>
        </div>
        <Button
          variant="solid"
          size="lg"
          class="mt-3 w-full"
          :disabled="!itemCount"
          :loading="placeOrder.loading"
          @click="place"
        >
          Send to kitchen
        </Button>
        <p v-if="placeOrder.error" class="mt-2 text-sm text-ink-red-4">
          {{ placeOrder.error.messages?.[0] || 'The order could not be placed.' }}
        </p>
        <p v-else-if="placeOrder.data" class="mt-2 text-sm text-ink-green-3">
          Sales order {{ placeOrder.data.name }} created · {{ kes(placeOrder.data.grand_total) }}
        </p>
      </section>

      <section class="rounded-xl border bg-surface-white p-4 lg:col-span-2">
        <div class="mb-3 flex items-center justify-between">
          <h2 class="text-base font-semibold">Kitchen</h2>
          <span class="text-sm text-ink-gray-5">Served today <strong class="text-ink-gray-9">{{ kes(takings) }}</strong></span>
        </div>
        <div class="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <div v-for="s in STAGES" :key="s" class="min-h-[140px] rounded-lg bg-surface-gray-1 p-2">
            <div class="mb-2 flex items-center justify-between px-1 text-sm font-medium text-ink-gray-6">
              {{ s }} <Badge :theme="STAGE_THEME[s]" variant="subtle">{{ byStage[s].length }}</Badge>
            </div>
            <div class="flex flex-col gap-2">
              <article v-for="t in byStage[s]" :key="t.no" class="rounded-lg border bg-surface-white p-3 text-sm">
                <div class="flex justify-between"><strong>#{{ t.no }}</strong><span class="text-ink-gray-5">{{ t.table }} · {{ t.at }}</span></div>
                <ul class="my-2 list-disc pl-4"><li v-for="i in t.items" :key="i">{{ i }}</li></ul>
                <div class="flex items-center justify-between">
                  <span class="tabular-nums">{{ kes(t.total) }}</span>
                  <Button v-if="s !== 'Served'" size="sm" variant="subtle" @click="advance(t)">
                    {{ s === 'Ready' ? 'Serve' : 'Next' }}
                    <template #suffix><FeatherIcon name="arrow-right" class="h-3.5 w-3.5" /></template>
                  </Button>
                </div>
              </article>
            </div>
          </div>
        </div>
      </section>
    </main>
    <footer class="pb-6 text-center text-xs text-ink-gray-4">Demo system generated and deployed by CentralBench · Powered by ERPNext</footer>
  </div>
</template>
