<script setup>
import { computed, onMounted, onUnmounted, reactive, ref } from 'vue'

const MENU = [
  { id: 'tilapia-whole', cat: 'Fish', name: 'Whole fried tilapia', desc: 'Lake fish, fried crisp, served with kachumbari', price: 1200, emoji: '🐟' },
  { id: 'tilapia-wet', cat: 'Fish', name: 'Wet-fry tilapia', desc: 'Simmered in tomato and onion sauce', price: 1350, emoji: '🍲' },
  { id: 'fish-fillet', cat: 'Fish', name: 'Fish fillet', desc: 'Pan-seared fillet with lemon butter', price: 950, emoji: '🍋' },
  { id: 'ugali', cat: 'Sides', name: 'Ugali', desc: 'Firm white maize meal', price: 100, emoji: '🍚' },
  { id: 'sukuma', cat: 'Sides', name: 'Sukuma wiki', desc: 'Sautéed collard greens', price: 150, emoji: '🥬' },
  { id: 'chips', cat: 'Sides', name: 'Chips', desc: 'Hand-cut, lightly salted', price: 200, emoji: '🍟' },
  { id: 'soda', cat: 'Drinks', name: 'Soda', desc: '300 ml, chilled', price: 80, emoji: '🥤' },
  { id: 'juice', cat: 'Drinks', name: 'Fresh passion juice', desc: 'Pressed daily', price: 250, emoji: '🧃' },
  { id: 'chai', cat: 'Drinks', name: 'Chai', desc: 'Spiced milk tea', price: 100, emoji: '☕' },
]
const CATS = ['All', 'Fish', 'Sides', 'Drinks']
const STAGES = ['New', 'Preparing', 'Ready', 'Served']

const cat = ref('All')
const search = ref('')
const table = ref('T1')
const order = reactive(new Map())
const tickets = ref([])
let nextTicket = 101

const erp = ref({ state: 'checking', label: 'Checking ERP…' })
const release = ref('…')
const now = ref(new Date())
let clock

const kes = (n) => 'KES ' + n.toLocaleString('en-KE')
const visible = computed(() =>
  MENU.filter((m) => (cat.value === 'All' || m.cat === cat.value) &&
    m.name.toLowerCase().includes(search.value.trim().toLowerCase())),
)
const lines = computed(() => [...order.entries()].map(([id, qty]) => ({ ...MENU.find((m) => m.id === id), qty })))
const itemCount = computed(() => lines.value.reduce((n, l) => n + l.qty, 0))
const total = computed(() => lines.value.reduce((n, l) => n + l.qty * l.price, 0))
const byStage = computed(() => Object.fromEntries(STAGES.map((s) => [s, tickets.value.filter((t) => t.stage === s)])))
const takings = computed(() => tickets.value.filter((t) => t.stage === 'Served').reduce((n, t) => n + t.total, 0))

function add(item) { order.set(item.id, (order.get(item.id) || 0) + 1) }
function dec(id) {
  const q = (order.get(id) || 0) - 1
  q > 0 ? order.set(id, q) : order.delete(id)
}
function place() {
  if (!itemCount.value) return
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

onMounted(async () => {
  clock = setInterval(() => (now.value = new Date()), 1000)
  try {
    const r = await fetch('/api/method/ping')
    const body = await r.json()
    erp.value = body.message === 'pong'
      ? { state: 'ok', label: 'ERP connected' }
      : { state: 'warn', label: 'ERP responded unexpectedly' }
  } catch {
    erp.value = { state: 'off', label: 'Offline preview' }
  }
  try {
    const html = await (await fetch('/cb_release')).text()
    release.value = html.match(/id="cb-release">([^<]+)</)?.[1] ?? 'unknown'
  } catch {
    release.value = 'local'
  }
})
onUnmounted(() => clearInterval(clock))
</script>

<template>
  <div class="shell">
    <header class="top">
      <div class="brand">
        <span class="mark" aria-hidden="true">MO</span>
        <div>
          <h1>Mama Oliech</h1>
          <p>Front of house · {{ now.toLocaleDateString('en-KE', { weekday: 'long', day: 'numeric', month: 'long' }) }}</p>
        </div>
      </div>
      <div class="status">
        <span class="chip" :class="erp.state"><i></i>{{ erp.label }}</span>
        <span class="chip neutral">Release {{ release }}</span>
        <span class="clock">{{ now.toLocaleTimeString('en-KE', { hour: '2-digit', minute: '2-digit' }) }}</span>
      </div>
    </header>

    <main class="grid">
      <section class="menu card">
        <div class="menu-head">
          <h2>Menu</h2>
          <input v-model="search" type="search" placeholder="Search dishes" aria-label="Search dishes" />
        </div>
        <nav class="tabs" role="tablist">
          <button v-for="c in CATS" :key="c" role="tab" :aria-selected="cat === c" :class="{ on: cat === c }" @click="cat = c">{{ c }}</button>
        </nav>
        <ul class="items">
          <li v-for="m in visible" :key="m.id">
            <button class="item" @click="add(m)">
              <span class="emoji" aria-hidden="true">{{ m.emoji }}</span>
              <span class="meta">
                <strong>{{ m.name }}</strong>
                <small>{{ m.desc }}</small>
              </span>
              <span class="price">{{ kes(m.price) }}</span>
              <span v-if="order.get(m.id)" class="badge">{{ order.get(m.id) }}</span>
            </button>
          </li>
          <li v-if="!visible.length" class="empty">No dishes match “{{ search }}”.</li>
        </ul>
      </section>

      <section class="order card">
        <div class="order-head">
          <h2>Current order</h2>
          <label>Table
            <select v-model="table">
              <option v-for="n in 12" :key="n" :value="'T' + n">T{{ n }}</option>
              <option value="Takeaway">Takeaway</option>
            </select>
          </label>
        </div>
        <ul v-if="lines.length" class="lines">
          <li v-for="l in lines" :key="l.id">
            <span>{{ l.name }}</span>
            <span class="qty">
              <button aria-label="Remove one" @click="dec(l.id)">−</button>
              {{ l.qty }}
              <button aria-label="Add one" @click="add(l)">+</button>
            </span>
            <span class="amt">{{ kes(l.qty * l.price) }}</span>
          </li>
        </ul>
        <p v-else class="empty">Tap a dish to start an order.</p>
        <div class="total"><span>{{ itemCount }} item{{ itemCount === 1 ? '' : 's' }}</span><strong>{{ kes(total) }}</strong></div>
        <button class="primary" :disabled="!itemCount" @click="place">Send to kitchen</button>
      </section>

      <section class="kitchen card">
        <div class="order-head">
          <h2>Kitchen</h2>
          <span class="takings">Served today <strong>{{ kes(takings) }}</strong></span>
        </div>
        <div class="lanes">
          <div v-for="s in STAGES" :key="s" class="lane">
            <h3>{{ s }} <span>{{ byStage[s].length }}</span></h3>
            <TransitionGroup name="t" tag="div" class="stack">
              <article v-for="t in byStage[s]" :key="t.no" class="ticket" :class="s.toLowerCase()">
                <header><strong>#{{ t.no }}</strong><span>{{ t.table }} · {{ t.at }}</span></header>
                <ul><li v-for="i in t.items" :key="i">{{ i }}</li></ul>
                <footer>
                  <span>{{ kes(t.total) }}</span>
                  <button v-if="s !== 'Served'" @click="advance(t)">{{ s === 'Ready' ? 'Serve' : 'Next' }} →</button>
                </footer>
              </article>
            </TransitionGroup>
          </div>
        </div>
      </section>
    </main>
    <footer class="foot">Demo system generated and deployed by CentralBench · Powered by ERPNext</footer>
  </div>
</template>
