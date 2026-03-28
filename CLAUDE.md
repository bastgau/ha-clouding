# ha-clouding — Project context for Claude Code

Home Assistant integration to monitor and control [Clouding.io](https://clouding.io) VMs.

## File structure

```
custom_components/clouding/
├── manifest.json           domain=clouding, version=0.0.0, iot_class=cloud_polling, type=hub
├── const.py                Global constants
├── __init__.py             Entry setup, registers the 6 services
├── coordinator.py          DataUpdateCoordinator → GET /servers every N seconds
├── config_flow.py          UI config: api_key + name; options: update_interval (15-3600s)
├── sensor.py               12 sensors per server
├── binary_sensor.py        1 binary sensor per server (is_running)
├── services.py             Dispatcher for the 6 server actions
├── device_info.py          Builds HA DeviceInfo (manufacturer=Clouding.io)
├── helpers.py              purge_entities() — exists but IS NOT CALLED
└── pythonclouding/
    ├── clouding.py         aiohttp HTTP client, base_url=https://api.clouding.io/v1
    ├── models.py           CloudingServer, CloudingServerImage, CloudingPublicPorts (mashumaro)
    ├── const.py            BASE_URL
    └── exceptions.py       CloudingError > Auth / BadRequest / Connection / InvalidAPIResponse
```

## Key constants (const.py)

| Constant | Value |
|---|---|
| `DOMAIN` | `"clouding"` |
| `MIN_TIME_BETWEEN_UPDATES` | `timedelta(seconds=300)` |
| `CONF_UPDATE_INTERVAL` | `"update_interval"` |
| `DEFAULT_NAME` | `"Clouding.io"` |
| `PORTAL_URL` | `"https://portal.clouding.io"` |

## Clouding.io API

- **Base URL**: `https://api.clouding.io/v1`
- **Auth**: header `X-API-KEY: {api_key}`
- **Timeout**: 10s (aiohttp ClientTimeout)
- **Endpoints used**:
  - `GET /servers` → lists all servers for the account
  - `POST /servers/{server_id}/{action}` → action: `start`, `stop`, `reboot`, `hard-reboot`, `archive`, `unarchive`

## Exposed entities (per server)

### Sensors (12)
`flavor`, `hostname`, `private_ip`, `ram_gb` (DATA_SIZE, GB), `created_at` (TIMESTAMP), `dns_address`, `name`, `power_state`, `public_ip`, `status` (dynamic icon), `vcores`, `volume_size_gb` (DATA_SIZE, GB)

**Status sensor** — dynamic icon based on value:
- `archived` → `mdi:archive-check-outline`
- `archiving`/`unarchiving` → `mdi:archive-clock-outline`
- `stopped` → `mdi:close-circle-outline`
- `starting`/`stopping` → `mdi:refresh-circle`
- others → `mdi:check-circle-outline`

### Binary sensor (1)
- `is_running` — device_class=RUNNING, extra_attr: `{"Value": power_state_string}`

## HA services (6, all device-targeted via device_id)

| Service | API action |
|---|---|
| `start_server` | `start` |
| `stop_server` | `stop` |
| `reboot_server` | `reboot` |
| `hard_reboot_server` | `hard-reboot` |
| `archive_server` | `archive` |
| `unarchive_server` | `unarchive` |

After each action → `coordinator.async_refresh()` to pull the updated state.

## CloudingServer model (mashumaro DataClassDictMixin)

JSON fields → `attr_*` properties:
- `id`, `name`, `hostname`, `flavor`, `status`, `powerState`, `privateIp`, `publicIp`
- `dnsAddress`, `ramGb`, `vCores`, `volumeSizeGb`, `createdAt` (UTC datetime)
- `image` (CloudingServerImage: id, name)
- `publicPorts` (list of CloudingPublicPorts)
- `attr_is_running` → bool: `powerState != "shutdown"`

## Architectural patterns

- **DataUpdateCoordinator**: centralised polling, all entities subscribe to it
- **CoordinatorEntity**: base class for both sensors and binary sensors
- **PARALLEL_UPDATES = 0**: sequential entity updates
- `_handle_coordinator_update()`: comparison guard — only calls `async_write_ha_state` when value, icon, or attributes actually changed (DB optimisation)
- **Config entry data**: `{CONF_NAME, CONF_API_KEY, CONF_UPDATE_INTERVAL}`
- **No external dependencies**: `requirements=[]` in manifest, aiohttp is provided by HA

## Known issues / constraints

1. **`purge_entities()` not called** — servers deleted in Clouding.io leave ghost devices in HA (manual removal required)
2. **No per-server filtering** — all servers in the API account are imported
3. **Reload required** — changing `update_interval` requires an integration reload or HA restart
4. **No webhooks** — pure polling, no event-driven updates
5. **English only** — only `translations/en.json` provided
6. **Server-side validation** — services do not check action feasibility before the API call (e.g. stopping an already-stopped server → 400)

## Key decisions history

- **Removed `Last Refresh`** from binary sensor extra_attributes: `dt_util.utcnow()` changed on every poll, forcing HA to write a new state row to the DB even when nothing had changed → DB bloat.
- **Comparison guard** in `_handle_coordinator_update()` (sensor + binary sensor): only triggers `async_write_ha_state` when the value or attributes have actually changed.
- **`_attr_is_on`** used in the binary sensor (native HA attribute) instead of `_attr_native_value`, which is reserved for `SensorEntity`.
