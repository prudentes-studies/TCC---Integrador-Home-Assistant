const logEl = document.getElementById('event-log');
const mqttStatusEl = document.getElementById('mqtt-status');
const healthStatusEl = document.getElementById('health-status');

const appendLog = (type, payload) => {
  const line = `[${new Date().toLocaleTimeString()}] ${type}: ${JSON.stringify(payload)}\n`;
  logEl.textContent = `${line}${logEl.textContent}`.slice(0, 8000);
};

const refreshHealth = async () => {
  const response = await fetch('/health');
  const data = await response.json();
  healthStatusEl.textContent = `${data.status} | MQTT: ${data.mqttConnected ? 'on' : 'off'} | HA: ${data.haEnabled ? 'on' : 'off'}`;
};

subscribeSse((type, payload) => {
  if (type === 'status') {
    mqttStatusEl.textContent = payload.message;
  }
  appendLog(type, payload);
});

refreshHealth();

const form = document.getElementById('publish-form');
form.addEventListener('submit', async (event) => {
  event.preventDefault();
  const device = document.getElementById('device').value;
  const action = document.getElementById('action').value;
  const payloadText = document.getElementById('payload').value;
  const payload = payloadText ? JSON.parse(payloadText) : {};
  await fetch('/api/mqtt/publish', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ device, action, payload }),
  });
});
