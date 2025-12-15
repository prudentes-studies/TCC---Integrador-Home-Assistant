import mqtt from 'mqtt';
import { v4 as uuidv4 } from 'uuid';

const brokerUrl = process.env.MQTT_BROKER_URL || 'mqtt://localhost:1883';
const topic = process.env.MQTT_TOPIC || 'tcc/demo/log';
const clientId = `demo-publisher-${uuidv4()}`;

const client = mqtt.connect(brokerUrl, { clientId });

const publishLoop = () => {
  const payload = {
    message: 'demo heartbeat',
    timestamp: new Date().toISOString(),
    status: 'ok',
  };
  client.publish(topic, JSON.stringify(payload));
};

client.on('connect', () => {
  console.log(`Connected to MQTT broker at ${brokerUrl} with topic ${topic}`);
  setInterval(publishLoop, 2000);
});

client.on('error', (err) => {
  console.error('MQTT error', err);
});
