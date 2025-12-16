import mqtt from 'mqtt';
import EventEmitter from 'events';
import { v4 as uuidv4 } from 'uuid';

const DEFAULT_TOPICS = {
  command: 'tcc/demo/cmd/+/+',
  state: 'tcc/demo/state/+',
  ack: 'tcc/demo/ack/+',
  log: 'tcc/demo/log'
};

export class MqttBridge extends EventEmitter {
  constructor(options = {}) {
    super();
    this.brokerUrl = options.brokerUrl || 'mqtt://localhost:1883';
    this.topics = { ...DEFAULT_TOPICS, ...(options.topics || {}) };
    this.clientId = options.clientId || `codex-dashboard-${uuidv4()}`;
    this.client = null;
  }

  start() {
    this.client = mqtt.connect(this.brokerUrl, {
      clientId: this.clientId,
      protocolVersion: 5,
      clean: true
    });
    this.client.on('connect', () => {
      this.emit('status', { level: 'info', message: 'MQTT conectado', clientId: this.clientId });
      this.subscribeToTopics();
    });

    this.client.on('message', (topic, message) => {
      const payload = this.safeParse(message);
      this.emit('message', { topic, payload });
    });

    this.client.on('error', (error) => {
      this.emit('status', { level: 'error', message: `Erro MQTT: ${error.message}` });
    });

    this.client.on('close', () => {
      this.emit('status', { level: 'warn', message: 'MQTT desconectado' });
    });
  }

  subscribeToTopics() {
    const topicList = Object.values(this.topics);
    topicList.forEach((topic) => this.client.subscribe(topic));
  }

  safeParse(buffer) {
    try {
      return JSON.parse(buffer.toString());
    } catch (err) {
      return buffer.toString();
    }
  }

  publishCommand(device, action, payload) {
    const topic = `tcc/demo/cmd/${device}/${action}`;
    this.client.publish(topic, JSON.stringify(payload));
    this.emit('message', { topic, payload: { simulated: true, ...payload } });
  }
}
