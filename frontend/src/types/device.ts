export interface Device {
  id: string
  device_code: string
  name: string
  mac_address?: string
  chip_type: string
  hardware_capabilities?: Record<string, boolean>
  current_config?: Record<string, any>
  status: 'online' | 'offline' | 'busy'
  last_seen_at?: string
  created_at: string
  updated_at: string
}

export interface TelemetryLog {
  id: number
  device_id: string
  cpu_temperature?: number
  free_heap?: number
  wifi_rssi?: number
  battery_voltage?: number
  custom_metrics?: Record<string, any>
  created_at: string
}

export interface CreateDevicePayload {
  device_code: string
  name: string
  mac_address?: string
  chip_type?: string
}
