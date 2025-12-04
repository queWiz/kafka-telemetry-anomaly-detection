<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  PointElement,
  LinearScale
} from 'chart.js'
import { Scatter } from 'vue-chartjs'

// 1. Register ChartJS components
ChartJS.register(Title, Tooltip, Legend, PointElement, LinearScale)

const alerts = ref([])
const isConnected = ref(false)
let socket = null

// 2. Chart Configuration
const chartData = ref({
  datasets: [
    {
      label: 'Anomalies Detected',
      backgroundColor: '#f85149', // Red dots
      data: [] // We will push {x, y} objects here
    }
  ]
})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  scales: {
    x: {
      title: { display: true, text: 'Reaction Time (ms)', color: '#8b949e' },
      grid: { color: '#30363d' },
      ticks: { color: '#8b949e' }
    },
    y: {
      title: { display: true, text: 'Accuracy (0-1.0)', color: '#8b949e' },
      grid: { color: '#30363d' },
      ticks: { color: '#8b949e' },
      min: 0,
      max: 1.1
    }
  },
  plugins: {
    legend: { labels: { color: '#c9d1d9' } }
  }
}

const connectWebSocket = () => {
  socket = new WebSocket("ws://localhost:8000/ws/alerts")

  socket.onopen = () => {
    console.log("✅ Connected to Sentinel API")
    isConnected.value = true
  }

  socket.onmessage = (event) => {
    const data = JSON.parse(event.data)
    
    // Update List
    alerts.value.unshift(data)
    if (alerts.value.length > 10) alerts.value.pop()

    // 3. Update Chart
    const point = {
      x: data.telemetry_snapshot.reaction_time_ms,
      y: data.telemetry_snapshot.accuracy_rating
    }
    
    // Add point to chart
    const newData = [...chartData.value.datasets[0].data, point]
    // Keep only last 20 points on graph to keep it clean
    if (newData.length > 20) newData.shift()

    chartData.value = {
      datasets: [{ ...chartData.value.datasets[0], data: newData }]
    }
  }

  socket.onclose = () => {
    isConnected.value = false
  }
}

onMounted(() => connectWebSocket())
onUnmounted(() => { if (socket) socket.close() })
</script>

<template>
  <div class="dashboard-container">
    <header>
      <h1>🛡️ SENTINEL <span class="subtitle">Real-Time Anti-Cheat Engine</span></h1>
      <div class="status-indicator">
        <span class="dot" :class="{ active: isConnected }"></span>
        {{ isConnected ? 'SYSTEM ONLINE' : 'DISCONNECTED' }}
      </div>
    </header>

    <main class="main-layout">
      <!-- Left Column: The Live Graph -->
      <div class="chart-container">
        <h3>📊 Anomaly Cluster Analysis</h3>
        <div class="chart-wrapper">
          <Scatter :data="chartData" :options="chartOptions" />
        </div>
      </div>

      <!-- Right Column: The Alert Feed -->
      <div class="feed-container">
        <h3>🚨 Live Alert Feed</h3>
        <div v-if="alerts.length === 0" class="empty-state">
          <p>Waiting for telemetry stream...</p>
        </div>

        <transition-group name="list" tag="div" class="alert-list">
          <div v-for="alert in alerts" :key="alert.timestamp" class="alert-card">
            <div class="alert-header">
              <span class="player-id">⚠️ {{ alert.player_id }}</span>
              <span class="timestamp">{{ new Date(alert.timestamp * 1000).toLocaleTimeString() }}</span>
            </div>
            <div class="stats-grid">
              <div class="stat">
                <label>React</label>
                <div class="value danger">{{ alert.telemetry_snapshot.reaction_time_ms }}ms</div>
              </div>
              <div class="stat">
                <label>Acc</label>
                <div class="value">{{ (alert.telemetry_snapshot.accuracy_rating * 100).toFixed(0) }}%</div>
              </div>
              <div class="stat">
                <label>Speed</label>
                <div class="value">{{ alert.telemetry_snapshot.mouse_speed }}</div>
              </div>
            </div>
          </div>
        </transition-group>
      </div>
    </main>
  </div>
</template>

<style scoped>
/* Dark Mode Theme */
.dashboard-container {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background-color: #0d1117;
  color: #c9d1d9;
  min-height: 100vh;
  padding: 2rem;
}

header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #30363d;
  padding-bottom: 1rem;
  margin-bottom: 2rem;
}

h1 { margin: 0; color: #58a6ff; font-weight: 300; letter-spacing: 1px; }
.subtitle { font-size: 0.8rem; color: #8b949e; margin-left: 10px; }

/* Layout Grid */
.main-layout {
  display: grid;
  grid-template-columns: 2fr 1fr; /* Graph takes 2/3, Feed takes 1/3 */
  gap: 2rem;
}

.chart-container, .feed-container {
  background: #161b22;
  border: 1px solid #30363d;
  border-radius: 8px;
  padding: 1.5rem;
}

h3 { margin-top: 0; color: #8b949e; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px; }

.chart-wrapper {
  position: relative;
  height: 300px; /* Fixed height for graph */
}

/* Alert Cards */
.alert-card {
  background-color: #0d1117;
  border-left: 4px solid #f85149;
  padding: 1rem;
  margin-bottom: 0.8rem;
  border-radius: 4px;
}

.alert-header { display: flex; justify-content: space-between; margin-bottom: 0.5rem; }
.player-id { color: #f85149; font-weight: bold; }
.timestamp { font-size: 0.8rem; color: #8b949e; }

.stats-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 5px; }
.stat label { display: block; font-size: 0.7rem; color: #8b949e; }
.stat .value { font-weight: bold; font-family: monospace; }
.stat .value.danger { color: #f85149; }

/* Status Dot */
.dot { width: 10px; height: 10px; background-color: #da3633; border-radius: 50%; margin-right: 8px; display: inline-block; }
.dot.active { background-color: #238636; box-shadow: 0 0 8px #238636; }

/* Animations */
.list-enter-active, .list-leave-active { transition: all 0.5s ease; }
.list-enter-from, .list-leave-to { opacity: 0; transform: translateX(30px); }
</style>