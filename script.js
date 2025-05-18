class StatusMonitor {
  constructor() {
    this.ws = new WebSocket('ws://10.42.0.218:8081');
    this.startTime = Date.now();
    this.statusMap = this.createStatusMap();
    this.init();
  }

  createStatusMap() {
    return {
      navigation: {
        600: { text: '🕒 待机状态', color: '#7f8c8d' },
        601: { text: '🚗 路径执行中', color: '#3498db' },
        602: { text: '❌ 导航失败', color: '#e74c3c' },
        603: { text: '✅ 到达目标', color: '#2ecc71' },
        604: { text: '⏹️ 任务中止', color: '#f39c12' }
      },
      actuator: {
        pump: ['💧 喷水灭火', '🟢 待命'],
        siren: ['🚨 警报响起', '🔕 静音状态']
      }
    };
  }

  init() {
    this.ws.onmessage = (event) => this.handleMessage(event);
    setInterval(() => this.updateTimer(), 1000);
  }

  handleMessage(event) {
    try {
      const data = JSON.parse(event.data);
      this.updateInterface(data);
      this.logSystemStatus(data);
    } catch (error) {
      console.error('数据解析错误:', error);
    }
  }

  updateInterface(data) {
    this.updateSensors(data);
    this.updateActuators(data);
    this.updateNavigation(data);
    this.updateSystemMessage(data);
  }

  updateSensors(data) {
    // 传感器更新逻辑
    const sensors = [
      { id: 'smoke1', ip: '10.42.0.122', field: 'smoke_detected1' },
      // 其他传感器配置
    ];

    sensors.forEach(({ id, ip, field }) => {
      const element = document.getElementById(id);
      const isActive = data[ip]?.[field];
      element.querySelector('.status-value').textContent = isActive ? '报警' : '正常';
      element.querySelector('.status-indicator').className = 
        `status-indicator ${isActive ? 'alarm' : 'normal'}`;
    });
  }

  updateActuators(data) {
    // 执行机构更新逻辑
    const actuators = [
      { id: 'pump', ip: '10.42.0.177', field: 'put_out' },
      // 其他执行机构配置
    ];

    actuators.forEach(({ id, ip, field }) => {
      const element = document.getElementById(id);
      const state = data[ip]?.[field] ? 0 : 1;
      element.querySelector('.status-value').textContent = 
        this.statusMap.actuator[id][state];
    });
  }

  updateNavigation(data) {
    const element = document.getElementById('navigation');
    for (const ip in data) {
      if (data[ip].navigating) {
        const status = this.statusMap.navigation[data[ip].navigating];
        element.querySelector('.status-value').textContent = status.text;
        element.style.background = status.color;
        break;
      }
    }
  }

  updateSystemMessage(data) {
    const messageElement = document.getElementById('message');
    for (const ip in data) {
      if (data[ip].msg) {
        messageElement.textContent = data[ip].msg;
        return;
      }
    }
    messageElement.textContent = '系统运行正常';
  }

  updateTimer() {
    const elapsed = Math.floor((Date.now() - this.startTime) / 1000);
    document.getElementById('duration').textContent = 
      `运行时间: ${String(Math.floor(elapsed / 60)).padStart(2, '0')}:${String(elapsed % 60).padStart(2, '0')}`;
  }

  logSystemStatus(data) {
    if (process.env.NODE_ENV === 'development') {
      console.table(data);
    }
  }
}

// 初始化监控系统
new StatusMonitor();