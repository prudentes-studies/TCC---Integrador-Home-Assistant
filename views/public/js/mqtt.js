const mqttLogEl = document.getElementById('mqtt-log');

subscribeSse((type, payload) => {
  if (type === 'mqtt') {
    const line = `[${new Date().toLocaleTimeString()}] ${payload.topic} => ${JSON.stringify(payload.payload)}\n`;
    mqttLogEl.textContent = `${line}${mqttLogEl.textContent}`.slice(0, 8000);
  }
  if (type === 'status') {
    const line = `[${new Date().toLocaleTimeString()}] status => ${payload.message}\n`;
    mqttLogEl.textContent = `${line}${mqttLogEl.textContent}`.slice(0, 8000);
  }
});
