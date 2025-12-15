import express from 'express';
import morgan from 'morgan';
import compression from 'compression';
import cors from 'cors';
import bodyParser from 'body-parser';
import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';
import expressLayouts from 'express-ejs-layouts';
import swaggerUi from 'swagger-ui-express';
import yaml from 'js-yaml';
import fs from 'fs';

import { MqttBridge } from './mqtt.js';
import { HomeAssistantClient } from './ha.js';

dotenv.config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const app = express();
const port = process.env.PORT || 3000;

app.use(cors());
app.use(compression());
app.use(morgan('dev'));
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));
app.use(express.static(path.join(__dirname, '..', 'views', 'public')));
app.use(expressLayouts);
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, '..', 'views'));
app.set('layout', 'layout');

const mqttBridge = new MqttBridge({ brokerUrl: process.env.MQTT_BROKER_URL });
const haClient = new HomeAssistantClient({
  baseUrl: process.env.HA_BASE_URL,
  token: process.env.HA_TOKEN,
  enabled: process.env.ENABLE_HA,
});

let sseClients = [];

const broadcast = (event, data) => {
  sseClients.forEach((client) => {
    client.res.write(`event: ${event}\n`);
    client.res.write(`data: ${JSON.stringify(data)}\n\n`);
  });
};

mqttBridge.on('message', (payload) => broadcast('mqtt', payload));
mqttBridge.on('status', (payload) => broadcast('status', payload));
mqttBridge.start();

app.get('/', (req, res) => {
  res.render('index', {
    mqttControlCenter: process.env.MQTT_CONTROL_CENTER || 'http://localhost:8080',
  });
});

app.get('/devices', (req, res) => {
  res.render('devices');
});

app.get('/mqtt', (req, res) => {
  res.render('mqtt');
});

app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    mqttConnected: mqttBridge?.client?.connected || false,
    haEnabled: haClient.isEnabled(),
    timestamp: new Date().toISOString(),
  });
});

app.get('/api/events', (req, res) => {
  res.setHeader('Content-Type', 'text/event-stream');
  res.setHeader('Cache-Control', 'no-cache');
  res.setHeader('Connection', 'keep-alive');
  res.flushHeaders();

  const clientId = Date.now();
  sseClients.push({ id: clientId, res });
  req.on('close', () => {
    sseClients = sseClients.filter((client) => client.id !== clientId);
  });
});

app.post('/api/mqtt/publish', (req, res) => {
  const { device, action, payload } = req.body;
  mqttBridge.publishCommand(device, action, payload || {});
  res.json({ status: 'queued' });
});

app.get('/api/ha/states', async (req, res) => {
  try {
    const states = await haClient.fetchStates();
    res.json({ states });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.post('/api/ha/service', async (req, res) => {
  const { domain, service, data } = req.body;
  try {
    const result = await haClient.callService(domain, service, data);
    res.json({ result });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

const swaggerPath = path.join(__dirname, '..', 'docs', 'swagger.yaml');
const swaggerDocument = yaml.load(fs.readFileSync(swaggerPath, 'utf8'));
app.use('/swagger', swaggerUi.serve, swaggerUi.setup(swaggerDocument));

app.listen(port, () => {
  // eslint-disable-next-line no-console
  console.log(`Servidor iniciado na porta ${port}`);
});
