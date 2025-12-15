import axios from 'axios';

export class HomeAssistantClient {
  constructor(options = {}) {
    this.baseUrl = options.baseUrl || 'http://10.10.10.100:8123';
    this.token = options.token || '';
    this.enabled = options.enabled === true || options.enabled === 'true';
  }

  isEnabled() {
    return this.enabled && this.token;
  }

  async callService(domain, service, data = {}) {
    if (!this.isEnabled()) {
      throw new Error('Home Assistant desabilitado ou sem token');
    }
    const url = `${this.baseUrl}/api/services/${domain}/${service}`;
    const response = await axios.post(url, data, {
      headers: {
        Authorization: `Bearer ${this.token}`,
        'Content-Type': 'application/json',
      },
    });
    return response.data;
  }

  async fetchStates() {
    if (!this.isEnabled()) {
      return [];
    }
    const response = await axios.get(`${this.baseUrl}/api/states`, {
      headers: { Authorization: `Bearer ${this.token}` },
    });
    return response.data;
  }
}
