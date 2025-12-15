const statesEl = document.getElementById('ha-states');
const refreshButton = document.getElementById('refresh-ha');

const loadStates = async () => {
  statesEl.textContent = 'Carregando...';
  const response = await fetch('/api/ha/states');
  const data = await response.json();
  statesEl.textContent = JSON.stringify(data, null, 2);
};

refreshButton.addEventListener('click', loadStates);

subscribeSse((type, payload) => {
  if (type === 'mqtt') {
    const current = statesEl.textContent;
    const line = `[${new Date().toLocaleTimeString()}] MQTT ${payload.topic} => ${JSON.stringify(payload.payload)}\n`;
    statesEl.textContent = `${line}${current}`.slice(0, 8000);
  }
});
