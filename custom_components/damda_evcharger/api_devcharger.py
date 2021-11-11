"""API for EV charging station from 'data.go.kr'."""
from homeassistant.const import DEVICE_CLASS_TIMESTAMP
from homeassistant.core import callback

from homeassistant.helpers.dispatcher import (
    async_dispatcher_connect,
    async_dispatcher_send,
)
import logging
import requests
import json
import xmltodict

from urllib.parse import urlparse
from urllib.parse import parse_qs
from zoneinfo import ZoneInfo
from datetime import datetime, timedelta, timezone  # , timedelta

from .const import (
    API_NAME,
    BRAND,
    CAST_ES,
    CAST_EI,
    CAST_TYPE,
    CHARGE_READY,
    CHARGE_START,
    # CHARGER_ICON,
    CONF_API,
    CONF_EV,
    # CONF_NEAR,
    # CONF_PERSON,
    # CONF_ZONE,
    # CONF_ZC,
    DEVICE_ATTR,
    DEVICE_CLASS,
    DEVICE_DOMAIN,
    DEVICE_ENTITY,
    DEVICE_ICON,
    DEVICE_ID,
    DEVICE_NAME,
    DEVICE_REG,
    DEVICE_STATE,
    DEVICE_UNIQUE,
    DEVICE_UNIT,
    DEVICE_UPDATE,
    DOMAIN,
    ENTRY_LIST,
    ERROR_CODE,
    EV_DATA,
    EV_INFO_URL,
    EV_ITEM,
    EV_STATUS_URL,
    ITEM_BS_ID,
    ITEM_CH_ID,
    # ITEM_CH_TP,
    ITEM_LAST_C,
    ITEM_LAST_CE,
    # ITEM_LAST_CS,
    ITEM_ST_ID,
    ITEM_ST_NAME,
    ITEM_STATE,
    ITEM_UP,
    MANUFACTURER,
    MODEL,
    NAME,
    NAME_KOR,
    VERSION,
    SENSOR_DOMAIN,
    BSENSOR_DOMAIN,
    # Z_CODE_NAME,
)

_LOGGER = logging.getLogger(__name__)
ZONE = ZoneInfo("Asia/Seoul")
DT_FMT = "%Y%m%d%H%M%S"
DT_FMT2 = "%Y-%m-%d %H:%M"

DEBUG = False


@callback
def get_api(hass, entry):
    """Return gateway with a matching entry_id."""
    return hass.data[DOMAIN][API_NAME].get(entry.entry_id)


def log(flag, val, debug=False):
    """0:debug, 1:info, 2:warning, 3:error."""
    if flag == 0 and (DEBUG or debug):
        _LOGGER.debug(f"[{NAME}] {val}")
    elif flag == 1:
        _LOGGER.info(f"[{NAME}] {val}")
    elif flag == 2:
        _LOGGER.warning(f"[{NAME}] {val}")
    elif flag == 3:
        _LOGGER.error(f"[{NAME}] {val}")


def isfloat(value):
    """Determine string is float."""
    try:
        float(value)
        return True
    except ValueError:
        return False


def isnumber(value):
    """Determine string is number."""
    return (
        value is not None
        and isinstance(value, (str, int, float))
        and (
            isinstance(value, str)
            and (value.isnumeric() or value.isdigit())
            or isfloat(value)
        )
    )


def to_second(fmt, f, b):
    """Diff time to seconds."""
    return int((datetime.strptime(f, fmt) - datetime.strptime(b, fmt)).total_seconds())


def dif_min(a, b):
    """Diff time to seconds."""
    return int((a - b).total_seconds() / 60)


def merge_dicts(a, b):
    """Merge dict."""
    c = a.copy()
    c.update(b)
    return c


def to_datetime(v):
    """Convert api dt to datetime."""
    try:
        if isinstance(v, str) and v != "00000000000000":
            dt = datetime.strptime(v, DT_FMT).replace(tzinfo=ZONE)
        else:
            dt = datetime.now(timezone.utc).astimezone(ZONE)
    except Exception as ex:
        log(3, f"to_datetime fail > {v} > {ex}")
    return dt


class DamdaEVChargerAPI:
    """DamdaEVChargerAPI API."""

    def __init__(self, hass, entry):
        """Initialize the Charger API."""
        self.hass = hass
        self.entry = entry
        self.api_key = self.get_data(CONF_API)
        self.station = self.get_data(CONF_EV)
        self.info_time = None
        self.station_page = int(self.get_data("station_page", 0))
        # self.person = self.get_data(CONF_PERSON)
        # self.near_number = self.get_data(CONF_NEAR)
        self.device = {}  # unique_id: device
        self.entities = {
            SENSOR_DOMAIN: {},
            BSENSOR_DOMAIN: {},
        }  # unique_id: True/False
        self.loaded = {SENSOR_DOMAIN: False, BSENSOR_DOMAIN: False}
        self.result = {}
        self.listeners = []
        self._start = False
        log(1, f"Loading API > {self.station}")

    def load(self, domain, async_add_entity):
        """Component loaded."""
        self.loaded[domain] = True
        self.listeners.append(
            async_dispatcher_connect(
                self.hass, self.async_signal_new_device(domain), async_add_entity
            )
        )
        if self.complete and not self._start:
            self._start = True
        log(1, f"Component loaded [{self.station}] -> {domain}")

    @property
    def complete(self):
        """Component loaded."""
        for v in self.loaded.values():
            if not v:
                return False
        return True

    def set_data(self, key, value):
        """Set entry data."""
        self.hass.config_entries.async_update_entry(
            entry=self.entry, data={**self.entry.data, key: value}
        )
        return value

    def get_data(self, key, default=False):
        """Get entry data."""
        return self.entry.data.get(key, default)

    @property
    def manufacturer(self) -> str:
        """Get manufacturer."""
        return MANUFACTURER

    @property
    def version(self) -> str:
        """Get version."""
        return VERSION

    @property
    def brand(self) -> str:
        """Get brand."""
        return BRAND

    @property
    def name(self) -> str:
        """Get name."""
        return NAME_KOR

    @property
    def model(self) -> str:
        """Get model."""
        return f"{MODEL}_{VERSION}"

    def async_signal_new_device(self, device_type) -> str:
        """Damda EV specific event to signal new device."""
        new_device = {
            SENSOR_DOMAIN: "devcharger_new_sensor",
            BSENSOR_DOMAIN: "devcharger_new_binary_sensor",
        }
        return f"{self.station}_{new_device[device_type]}"

    def async_add_device(self, device=None, force: bool = False) -> None:
        """Handle event of new device creation in devcharger."""

        if device is None or not isinstance(device, dict):
            return
        args = []
        unique_id = device.get(DEVICE_UNIQUE, None)
        domain = device.get(DEVICE_DOMAIN)
        if self.search_entity(domain, unique_id) or not self.loaded.get(domain, False):
            return

        args.append([device])

        async_dispatcher_send(self.hass, self.async_signal_new_device(domain), *args)

    def sensors(self):
        """Get sensors."""
        target = SENSOR_DOMAIN
        return self.get_entities(target)

    def binary_sensors(self):
        """Get binary_sensors."""
        target = BSENSOR_DOMAIN
        return self.get_entities(target)

    def init_device(self, unique_id, domain, device=None):
        """Init device."""
        init_info = {
            DEVICE_DOMAIN: domain,
            DEVICE_REG: self.register_update_state,
            DEVICE_UPDATE: None,
            DEVICE_UNIQUE: unique_id,
            DEVICE_ENTITY: device,
        }
        if domain in self.entities:
            self.entities[domain].setdefault(unique_id, False)
        if unique_id not in self.device:
            log(
                0,
                f"Initialize device of {self.station} > {domain} > {unique_id}",
            )
        return self.device.setdefault(unique_id, init_info)

    def search_device(self, unique_id):
        """Search self.device."""
        return self.device.get(unique_id)

    def search_entity(self, domain, unique_id):
        """Search self.entities domain unique_id."""
        return self.entities.get(domain, {}).get(unique_id, False)

    def registered(self, unique_id):
        """Check unique_id is registered."""
        device = self.search_device(unique_id)
        if device:
            return device.get(unique_id).get(DEVICE_UPDATE) is not None
        return False

    def get_entities(self, domain):
        """Get self.device from self.entites domain."""
        entities = []
        entity_list = self.entities.get(domain, {})
        for id in entity_list.keys():
            device = self.search_device(id)
            if device:
                entities.append(device)
            else:
                entities.append(self.init_device(id, domain))
        return entities

    def set_entity(self, domain, unique_id, state=False):
        """Set self.entities domain unique_id True/False."""
        if domain not in self.entities:
            log(1, f"set_entity > {domain} not exist.")
            pass
        if unique_id not in self.entities[domain]:
            log(1, f"set_entity > {domain} > {unique_id} not exist.")
            pass
        if state:
            self.entities[domain][unique_id] = state
            self.hass.data[DOMAIN][self.entry.entry_id][unique_id] = state
        else:
            self.entities[domain].pop(unique_id)
            self.hass.data[DOMAIN][self.entry.entry_id].pop(unique_id)

    def get_state(self, unique_id, target=DEVICE_STATE):
        """Get device state."""
        device = self.search_device(unique_id)
        if device:
            return device.get(DEVICE_ENTITY).get(target, None)
        return None

    def set_device(self, unique_id, entity):
        """Set device entity."""
        device = self.search_device(unique_id)
        if device:
            try:
                self.device[unique_id][DEVICE_ENTITY].update(entity)
            except Exception as ex:
                log(3, f"Set entity error > {unique_id} > {entity} > {ex}")

    def register_update_state(self, unique_id, cb=None):
        """Register device update function to update entity state."""
        device = self.search_device(unique_id)
        if device:
            if (device.get(DEVICE_UPDATE) is None and cb is not None) or (
                device.get(DEVICE_UPDATE) is not None and cb is None
            ):
                msg = f"{'Register' if cb is not None else 'Unregister'} device => {unique_id}"
                log(0, msg)
                self.device[unique_id][DEVICE_UPDATE] = cb

    def update_entity(self, unique_id, entity, available=True):
        """Update device state."""
        device = self.search_device(unique_id)
        if not device:
            return
        self.device[unique_id][DEVICE_ENTITY].update(entity)
        if device.get(DEVICE_UPDATE) is not None:
            device.get(DEVICE_UPDATE)(available)
        else:
            self.async_add_device(device)

    def make_entity(
        self, attr, icon, device_class, domain, state, unit, unique_id, entity_id, name
    ):
        """Make entity."""
        entity = {
            DEVICE_ATTR: {
                CONF_EV: self.station,
            },
            DEVICE_DOMAIN: domain,
            DEVICE_STATE: state,
            DEVICE_UNIQUE: unique_id,
            DEVICE_ID: entity_id,
            DEVICE_NAME: name,
        }
        if attr is not None:
            if "dev_updatetime" not in unique_id:
                entity[DEVICE_ATTR].update(attr)
            else:
                entity[DEVICE_ATTR] = attr
        if unit is not None:
            entity[DEVICE_UNIT] = unit
        if icon is not None:
            entity[DEVICE_ICON] = icon
        if device_class is not None:
            entity[DEVICE_CLASS] = device_class
        return entity

    def parse(self, url, result):
        """Parse result as url."""
        target = ""
        if CAST_EI in url:
            target = CAST_EI
        elif CAST_ES in url:
            target = CAST_ES
        return self.parse_ev(target, result, url)

    def parse_ev(self, target, result, url):
        """Parse EV Charge Station data."""
        data = {}
        r_res = result.get("response", {})
        r_header = r_res.get("header", {})
        r_code = r_header.get("resultCode", "99")
        r_msg = r_header.get("resultMsg", "")
        r_total = int(r_header.get("totalCount", 0))
        r_page = int(r_header.get("pageNo", 1))
        r_row = int(r_header.get("numOfRows", 1))
        try:
            if ERROR_CODE.get(r_code, None) is None:
                if target == CAST_EI:
                    last_page = (r_total // 9999) + 1
                    if self.station_page != last_page:
                        self.station_page = int(
                            self.set_data("station_page", last_page)
                        )
                r_body = r_res.get("body", {})
                r_item = r_body.get("items", {}).get("item", [])
                for c in r_item:
                    station_id = c.get(ITEM_ST_ID)
                    charger_id = c.get(ITEM_CH_ID)
                    data[f"{station_id}:{charger_id}"] = c
        except Exception as ex:
            log(
                3,
                f"target [{target}] > {r_msg} > {url} > {ex}",
            )
        log(
            0,
            f"{target} -> total:{r_total} page:{r_page} row:{r_row} > data:{len(data)}",
        )
        return "EV", data

    def getURL(self, name):
        """Get name's URL."""
        url = []
        if name == CAST_EI:
            now = datetime.now(timezone.utc).astimezone(ZONE)
            if self.info_time is None or (
                isinstance(self.info_time, datetime)
                and now - self.info_time > timedelta(seconds=3600)
            ):
                last_page = (self.station_page + 1) if self.station_page > 0 else 101
                for i in range(1, last_page):
                    url.append(EV_INFO_URL.format(self.api_key, i))
        elif name == CAST_ES:
            url.append(EV_STATUS_URL.format(self.api_key))
        return url

    async def get_target(self, target, target_list):
        """Get target data from target_list."""
        data = {}
        try:
            for target_name in target_list:
                cast_url = self.getURL(target_name)
                for url in cast_url:
                    uparse = urlparse(url)
                    qparse = parse_qs(uparse.query)
                    page_no = qparse.get("pageNo", ["0"])[0]
                    if self.station_page > 0 and int(page_no) > self.station_page:
                        break
                    response = await self.hass.async_add_executor_job(requests.get, url)
                    try:
                        r_parse = response.json()
                    except Exception:
                        r_xml = response.content
                        r_parse = json.loads(json.dumps(xmltodict.parse(r_xml)))
                    r_target, r_data = self.parse(url, r_parse)
                    if r_target == target:
                        for unique_id, v in r_data.items():
                            data.setdefault(unique_id, {})
                            data[unique_id].update(v)
        except Exception as ex:
            log(3, f"Error at get_target > [{target}] > {ex}")
        return data

    async def get_ev(self):
        """Get AirKorea data."""
        return await self.get_target("EV", [CAST_EI, CAST_ES])

    async def update(self):
        """Update data from KMA and AirKorea."""
        try:
            now_dt = datetime.now(timezone.utc).astimezone(ZONE)
            now_fmt = now_dt.strftime(DT_FMT)
            ev = {}

            last_update = self.hass.data[DOMAIN].get("last_update")
            if last_update is None or (
                last_update is not None
                and now_dt - last_update > timedelta(seconds=120)
            ):
                if self.hass.data[DOMAIN][ENTRY_LIST][0] == self.entry.entry_id:
                    ev = await self.get_ev()
                    self.hass.data[DOMAIN]["last_update"] = now_dt
                self.hass.data[DOMAIN][EV_DATA].update(ev)
            else:
                ev.update(self.hass.data[DOMAIN][EV_DATA])

            unique_id = "dev_updatetime_" + str(
                self.hass.data[DOMAIN][ENTRY_LIST].index(self.entry.entry_id)
            )
            update_time_attr = {CAST_TYPE: "업데이트"}
            self.result[unique_id] = self.make_entity(
                update_time_attr,
                "mdi:clock-outline",
                DEVICE_CLASS_TIMESTAMP,
                SENSOR_DOMAIN,
                now_dt.isoformat() if last_update is None else last_update.isoformat(),
                None,
                unique_id,
                unique_id,
                f"담다EV {self.station}",
            )

            ev_result = {}
            for data in ev.values():
                # 메인센서 = binary_sensor
                # 메인센서 = 이름:충전가능여부
                # 메인센서 = 이름:충전완료여부
                # 서브센서 = sensor
                # 서브센서 = 이름:충전시작시간
                # 서브센서 = 이름:충전완료시간 complete, state charge>ready
                # 서브센서 = 이름:실제 충전시간, complete - charge
                # 서브센서 = 이름:충전종료 후 과점유시간, state ready >> now - complete
                # 서브센서 = 이름:주차시간, unplug<charge, now - plug
                station_name = data.get(ITEM_ST_NAME, "")

                if self.station in station_name:
                    attr = {CAST_TYPE: self.station}
                    for category, c_list in EV_ITEM.items():
                        if category in [
                            ITEM_UP,
                            # ITEM_LAST_CS,
                            ITEM_LAST_CE,
                            ITEM_LAST_C,
                        ]:
                            value = to_datetime(data.get(category, now_dt)).strftime(
                                DT_FMT
                            )
                        else:
                            value = data.get(category, "null")
                        attr[c_list[1]] = value if value != "null" else ""
                    station_id = data.get(ITEM_ST_ID)
                    business_id = data.get(ITEM_BS_ID)
                    charger_id = data.get(ITEM_CH_ID)
                    # charger_type = data.get(ITEM_CH_TP)
                    # charger_icon = CHARGER_ICON.get(charger_type)
                    i_state = EV_ITEM.get(ITEM_STATE)
                    state = i_state[2](data.get(ITEM_STATE))
                    time_last_change = to_datetime(data.get(ITEM_UP, now_dt))
                    # time_last_plug = to_datetime(data.get(ITEM_LAST_CS, now_dt))
                    time_last_unplug = to_datetime(data.get(ITEM_LAST_CE, now_dt))
                    time_last_charge = to_datetime(data.get(ITEM_LAST_C, now_dt))
                    header = "dev"
                    unique_id = (
                        f"{header}_{business_id}_{station_id}_{charger_id}".lower()
                    )
                    entity_id = f"{header}_{station_id}_{charger_id}".lower()
                    entity_name = f"담다EV {self.station}{charger_id}"
                    old_state = self.get_state(unique_id + "state")
                    self.set_data(unique_id + "state", state)
                    time_last_complete = to_datetime(
                        self.get_data(unique_id + "time", now_fmt)
                    )
                    if old_state == CHARGE_START and state == CHARGE_READY:
                        self.set_data(
                            unique_id + "time", time_last_change.strftime(DT_FMT)
                        )
                        time_last_complete = time_last_change
                    charge_time, over_parking, parking_time = 0, 0, 0
                    if state == CHARGE_START:
                        charge_time = dif_min(now_dt, time_last_charge)
                    if (
                        state == CHARGE_READY
                        and time_last_charge > time_last_unplug
                        and now_dt > time_last_complete
                    ):
                        charge_time = dif_min(time_last_complete, time_last_charge)
                        over_parking = dif_min(now_dt, time_last_complete)
                    if time_last_charge > time_last_unplug:
                        parking_time = dif_min(now_dt, time_last_charge)
                    charge_available = state == CHARGE_READY and parking_time == 0
                    charge_complete = state == CHARGE_READY and over_parking > 0

                    entity_list = {
                        f"{unique_id}_charge_state": [
                            SENSOR_DOMAIN,
                            None,
                            state,
                            f"{entity_id}_charge_state",
                            f"{entity_name} 충전상태",
                            "mdi:ev-station",
                        ],
                        f"{unique_id}_charge_available": [
                            BSENSOR_DOMAIN,
                            None,
                            charge_available,
                            f"{entity_id}_charge_available",
                            f"{entity_name} 충전가능",
                            "mdi:ev-station",
                        ],
                        f"{unique_id}_charge_complete": [
                            BSENSOR_DOMAIN,
                            None,
                            charge_complete,
                            f"{entity_id}_charge_complete",
                            f"{entity_name} 충전완료",
                            "mdi:ev-station",
                        ],
                        f"{unique_id}_charge_start": [
                            SENSOR_DOMAIN,
                            None,
                            time_last_charge.strftime(DT_FMT2)
                            if charge_time > 0
                            else str(timedelta(seconds=0)),
                            f"{entity_id}_charge_start",
                            f"{entity_name} 충전시작시간",
                            "mdi:clock-outline",
                        ],
                        f"{unique_id}_charge_end": [
                            SENSOR_DOMAIN,
                            None,
                            time_last_complete.strftime(DT_FMT2)
                            if charge_complete
                            else str(timedelta(seconds=0)),
                            f"{entity_id}_charge_end",
                            f"{entity_name} 충전완료시간",
                            "mdi:clock-outline",
                        ],
                        f"{unique_id}_charge_time": [
                            SENSOR_DOMAIN,
                            None,
                            str(timedelta(seconds=charge_time)),
                            f"{entity_id}_charge_time",
                            f"{entity_name} 충전시간",
                            "mdi:clock-outline",
                        ],
                        f"{unique_id}_charge_over": [
                            SENSOR_DOMAIN,
                            None,
                            str(timedelta(seconds=over_parking)),
                            f"{entity_id}_charge_over",
                            f"{entity_name} 과점유시간",
                            "mdi:clock-outline",
                        ],
                        f"{unique_id}_charge_parking": [
                            SENSOR_DOMAIN,
                            None,
                            str(timedelta(seconds=parking_time)),
                            f"{entity_id}_charge_parking",
                            f"{entity_name} 주차시간",
                            "mdi:clock-outline",
                        ],
                    }
                    for uid, ulist in entity_list.items():
                        if self.get_state(uid) != ulist[2]:
                            ev_result[uid] = self.make_entity(
                                attr
                                if "_charge_available" in uid
                                else {CAST_TYPE: self.station},
                                ulist[5],
                                ulist[1],
                                ulist[0],
                                ulist[2],
                                None,
                                uid,
                                ulist[3],
                                ulist[4],
                            )
            self.result.update(ev_result)

            for unique_id, entity in self.result.items():
                target_domain = entity.get(DEVICE_DOMAIN)
                if not target_domain:
                    log(1, f"Device domain does not exist > {unique_id} > {entity}")
                    continue
                self.init_device(unique_id, target_domain, entity)
                self.update_entity(unique_id, entity)
            if len(ev_result) > 0:
                log(
                    1,
                    f"{self.station} Update > {now_dt.strftime(DT_FMT2)} > Total:{len(self.hass.data[DOMAIN][EV_DATA])} Entity:{len(ev_result)}/{len(self.result)}",
                )
        except Exception as ex:
            log(
                3,
                f"{self.station} Update Fail > {ex}",
            )
