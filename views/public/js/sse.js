(() => {
  const eventSource = new EventSource('/api/events');
  const listeners = [];

  window.subscribeSse = (cb) => listeners.push(cb);

  eventSource.addEventListener('status', (event) => {
    const data = JSON.parse(event.data);
    listeners.forEach((cb) => cb('status', data));
  });

  eventSource.addEventListener('mqtt', (event) => {
    const data = JSON.parse(event.data);
    listeners.forEach((cb) => cb('mqtt', data));
  });
})();
