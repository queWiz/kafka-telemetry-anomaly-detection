<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const alerts = ref([])
const isConnected = ref(false)
let socket = null

const connectWebSocket = () => {
  // Connect to the FastAPI backend
  socket = new WebSocket("ws://localhost:8000/ws/alerts")

  socket.onopen = () => {
    console.log("✅ Connected to Sentinel API")
    isConnected.value = true
  }

  socket.onmessage = (event) => {
    // We received an Alert from Kafka!
    const data = JSON.parse(event.data)
    
    // Add to the top of the list
    alerts.value.unshift(data)
    
    // Keep list clean (max 10 items)
    if (alerts.value.length > 10) {
      alerts.value.pop()
    }
  }

  socket.onclose = () => {
    console.log("❌ Disconnected")
    isConnected.value = false
  }
}

onMounted(() => {
  connectWebSocket()
})

onUnmounted(() => {
  if (socket) socket.close()
})
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

    <main>
      <div v-if="alerts.length === 0" class="empty-state">
        <p>Waiting for telemetry stream...</p>
        <div class="loader"></div>
      </div>

      <transition-group name="list" tag="div" class="alert-list">
        <div v-for="alert in alerts" :key="alert.timestamp" class="alert-card">
          <div class="alert-header">
            <span class="player-id">⚠️ PLAYER: {{ alert.player_id }}</span>
            <span class="timestamp">{{ new Date(alert.timestamp * 1000).toLocaleTimeString() }}</span>
          </div>
          
          <div class="stats-grid">
            <div class="stat">
              <label>Reaction Time</label>
              <div class="value danger">{{ alert.telemetry_snapshot.reaction_time_ms }}ms</div>
            </div>
            <div class="stat">
              <label>Accuracy</label>
              <div class="value">{{ (alert.telemetry_snapshot.accuracy_rating * 100).toFixed(1) }}%</div>
            </div>
            <div class="stat">
              <label>Mouse Speed</label>
              <div class="value">{{ alert.telemetry_snapshot.mouse_speed }} px/t</div>
            </div>
          </div>
          
          <div class="reason">
            DETECTED: {{ alert.reason }}
          </div>
        </div>
      </transition-group>
    </main>
  </div>
</template>

<style scoped>
/* Dark Mode Terminal Theme */
.dashboard-container {
  font-family: 'Courier New', Courier, monospace;
  background-color: #0d1117;
  color: #c9d1d9;
  min-height: 100vh;
  padding: 2rem;
}

header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 2px solid #30363d;
  padding-bottom: 1rem;
  margin-bottom: 2rem;
}

h1 {
  margin: 0;
  font-size: 1.5rem;
  color: #58a6ff;
}

.subtitle {
  font-size: 0.8rem;
  color: #8b949e;
  margin-left: 10px;
}

.status-indicator {
  display: flex;
  align-items: center;
  font-weight: bold;
  font-size: 0.8rem;
}

.dot {
  width: 10px;
  height: 10px;
  background-color: #da3633; /* Red by default */
  border-radius: 50%;
  margin-right: 8px;
  box-shadow: 0 0 5px #da3633;
}

.dot.active {
  background-color: #238636; /* Green when connected */
  box-shadow: 0 0 8px #238636;
}

.empty-state {
  text-align: center;
  margin-top: 5rem;
  color: #484f58;
}

/* Alert Cards */
.alert-card {
  background-color: #161b22;
  border: 1px solid #30363d;
  border-left: 5px solid #da3633; /* Red warning border */
  padding: 1rem;
  margin-bottom: 1rem;
  border-radius: 6px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.3);
}

.alert-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 1rem;
  font-weight: bold;
}

.player-id {
  color: #f85149;
  font-size: 1.2rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 10px;
  margin-bottom: 10px;
  background: #0d1117;
  padding: 10px;
  border-radius: 4px;
}

.stat label {
  display: block;
  font-size: 0.7rem;
  color: #8b949e;
}

.stat .value {
  font-size: 1.1rem;
  font-weight: bold;
}

.stat .value.danger {
  color: #f85149; /* Red text */
}

.reason {
  font-size: 0.9rem;
  color: #ffa657;
  margin-top: 0.5rem;
}

/* Animations */
.list-enter-active,
.list-leave-active {
  transition: all 0.5s ease;
}
.list-enter-from,
.list-leave-to {
  opacity: 0;
  transform: translateX(-30px);
}
</style>