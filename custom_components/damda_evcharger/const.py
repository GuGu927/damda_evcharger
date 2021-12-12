"""Constants for the Damda EV integration."""
import homeassistant.helpers.config_validation as cv
from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
from homeassistant.components.binary_sensor import DOMAIN as BSENSOR_DOMAIN
from homeassistant.components.sensor import SensorDeviceClass

VERSION = "1.2.3"
BRAND = "Damda"
NAME = "Damda EV"
NAME_KOR = "담다EV"
DOMAIN = "damda_evcharger"
MODEL = "damda_ev"
MANUFACTURER = "data.go.kr"
API_NAME = "de_api"
EV_DATA = "de_data"
EV_DATA2 = "de_data2"
EV_LIST = "de_station"
PLATFORMS = [SENSOR_DOMAIN, BSENSOR_DOMAIN]

ENTRY_LIST = "entry_list"
KECO_DATA = "keco_data"

DEVICE_DOMAIN = "domain"
DEVICE_ENTITY = "entity"
DEVICE_UPDATE = "update"
DEVICE_REG = "register"
DEVICE_TRY = "try"
DEFAULT_AVAILABLE = "available"

DEVICE_ICON = "icon"
DEVICE_CLASS = "device_class"
DEVICE_UNIT = "unit_of_measurement"
DEVICE_ATTR = "attributes"
DEVICE_STATE = "state"
DEVICE_UNIQUE = "unique_id"
DEVICE_ID = "entity_id"
DEVICE_NAME = "entity_name"

CONF_API = "api_key"
CONF_EV = "ev_station"
CONF_PERSON = "ev_person"
CONF_NEAR = "ev_near"
Z_CODE_ID = {
    "11": "서울",
    "26": "부산",
    "27": "대구",
    "28": "인천",
    "29": "광주",
    "30": "대전",
    "31": "울산",
    "36": "세종",
    "41": "경기",
    "42": "강원",
    "43": "충북",
    "44": "충남",
    "45": "전북",
    "46": "전남",
    "47": "경북",
    "48": "경남",
    "50": "제주",
}
Z_CODE_NAME = {name: id for id, name in Z_CODE_ID.items()}
ZC_LIST = [name for id, name in Z_CODE_ID.items()]

EV_INFO_URL = "http://apis.data.go.kr/B552584/EvCharger/getChargerInfo?serviceKey={}&numOfRows=9999&pageNo={}"
EV_STATUS_URL = "http://apis.data.go.kr/B552584/EvCharger/getChargerStatus?serviceKey={}&numOfRows=9999"

CAST_EI = "getChargerInfo"
CAST_ES = "getChargerStatus"
CAST = {CAST_EI: "충전소정보", CAST_ES: "충전소상태"}
CAST_EN = {
    CAST_EI: "keco",
    CAST_ES: "keco",
}
CAST_TYPE = "type"

ITEM_STATE = "stat"
ITEM_ST_NAME = "statNm"
ITEM_ST_ID = "statId"
ITEM_CH_ID = "chgerId"
ITEM_CH_TP = "chgerType"
ITEM_ADDR = "addr"
ITEM_LOC = "location"
ITEM_LAT = "lat"
ITEM_LONG = "lng"
ITEM_USE = "useTime"
ITEM_BS_ID = "busiId"
ITEM_BS_NAME = "bnm"
ITEM_BS_BNM = "busiNm"
ITEM_BS_CALL = "busiCall"
ITEM_UP = "statUpdDt"
ITEM_LAST_CS = "lastTsdt"
ITEM_LAST_CE = "lastTedt"
ITEM_LAST_C = "nowTsdt"
ITEM_OUTPUT = "output"
ITEM_METHOD = "method"
ITEM_ZONE = "zcode"
ITEM_PKF = "parkingFree"
ITEM_NOTE = "note"
ITEM_LIMIT = "limitYn"
ITEM_LIMIT_NOTE = "limitDetail"
ITEM_DEL = "delYn"
ITEM_DEL_NOTE = "delDetail"


CHARGER_TYPE = {
    "01": "DC차데모",
    "02": "AC완속",
    "03": "DC차데모+AC3상",
    "04": "DC콤보",
    "05": "DC차데모+DC콤보",
    "06": "DC차데모+AC3상+DC콤보",
    "07": "AC3상",
}

CHARGER_ICON = {
    "01": "mdi:ev-plug-chademo",
    "02": "mdi:ev-plug-type1",
    "03": "mdi:ev-plug-chademo",
    "04": "mdi:ev-plug-ccs1",
    "05": "mdi:ev-plug-ccs2",
    "06": "mdi:ev-plug-ccs2",
    "07": "mdi:ev-plug-type2",
}


def conv_charger_icon(value):
    """Convert charger type int to icon."""
    return CHARGER_ICON.get(value, value)


CHARGE_ERROR = "통신이상"
CHARGE_START = "충전중"
CHARGE_READY = "충전대기"
CHARGE_STOP = "운영중지"
CHARGE_CHECK = "점검중"
CHARGE_UNKNOWN = "상태미확인"


def conv_state(value):
    """Convert charger state."""
    return {
        "1": "통신이상",
        "2": "충전대기",
        "3": "충전중",
        "4": "운영중지",
        "5": "점검중",
        "9": "상태미확인",
    }.get(value, value)


EV_ITEM = {
    ITEM_ST_NAME: [
        "station_name",
        "충전소명",
        None,
        SENSOR_DOMAIN,
        "mdi:ev-station",
        None,
    ],
    ITEM_ST_ID: [
        "station_id",
        "충전소ID",
        None,
        SENSOR_DOMAIN,
        "mdi:ev-station",
        None,
    ],
    ITEM_CH_ID: [
        "charger_id",
        "충전기ID",
        None,
        SENSOR_DOMAIN,
        "mdi:ev-station",
        None,
    ],
    ITEM_CH_TP: [
        "charger_type",
        "충전기종류",
        CHARGER_TYPE,
        SENSOR_DOMAIN,
        conv_charger_icon,
        None,
    ],
    ITEM_ADDR: [
        "station_address",
        "주소",
        None,
        SENSOR_DOMAIN,
        "mdi:map-marker",
        None,
    ],
    ITEM_LOC: [
        "station_location",
        "상세위치",
        None,
        SENSOR_DOMAIN,
        "mdi:map-marker",
        None,
    ],
    ITEM_LAT: [
        "station_latitude",
        "위도",
        None,
        SENSOR_DOMAIN,
        "mdi:latitude",
        None,
    ],
    ITEM_LONG: [
        "station_longitude",
        "경도",
        None,
        SENSOR_DOMAIN,
        "mdi:longitude",
        None,
    ],
    ITEM_USE: [
        "station_usetime",
        "이용가능시간",
        None,
        SENSOR_DOMAIN,
        "mdi:clock-outline",
        None,
    ],
    ITEM_BS_ID: [
        "business_id",
        "기관ID",
        None,
        SENSOR_DOMAIN,
        "mdi:domain",
        None,
    ],
    ITEM_BS_NAME: [
        "business_name",
        "기관명",
        None,
        SENSOR_DOMAIN,
        "mdi:domain",
        None,
    ],
    ITEM_BS_BNM: [
        "business_operator",
        "운영기관명",
        None,
        SENSOR_DOMAIN,
        "mdi:domain",
        None,
    ],
    ITEM_BS_CALL: [
        "business_call",
        "운영기관연락처",
        None,
        SENSOR_DOMAIN,
        "mdi:domain",
        None,
    ],
    ITEM_STATE: [
        "station_state",
        "상태",
        conv_state,
        SENSOR_DOMAIN,
        "mdi:ev-station",
        None,
    ],
    ITEM_UP: [
        "time_last_change",
        "상태갱신일시",
        None,
        SENSOR_DOMAIN,
        "mdi:clock-outline",
        SensorDeviceClass.TIMESTAMP,
    ],
    ITEM_LAST_CS: [
        "time_last_plug",
        "충전기플러그",
        None,
        SENSOR_DOMAIN,
        "mdi:clock-outline",
        SensorDeviceClass.TIMESTAMP,
    ],
    ITEM_LAST_CE: [
        "time_last_unplug",
        "충전기언플러그",
        None,
        SENSOR_DOMAIN,
        "mdi:clock-outline",
        SensorDeviceClass.TIMESTAMP,
    ],
    ITEM_LAST_C: [
        "time_last_charge",
        "충전시작시간",
        None,
        SENSOR_DOMAIN,
        "mdi:clock-outline",
        SensorDeviceClass.TIMESTAMP,
    ],
    ITEM_OUTPUT: [
        "charger_output",
        "충전용량",
        None,
        SENSOR_DOMAIN,
        "mdi:fuel-cell",
        None,
    ],
    ITEM_METHOD: [
        "charger_method",
        "충전방식",
        None,
        SENSOR_DOMAIN,
        "mdi:help-circle-outline",
        None,
    ],
    ITEM_ZONE: [
        "station_sido",
        "지역코드",
        None,
        SENSOR_DOMAIN,
        "mdi:map-clock",
        None,
    ],
    ITEM_PKF: [
        "station_parking",
        "주차료무료",
        None,
        BSENSOR_DOMAIN,
        "mdi:map-clock",
        None,
    ],
    ITEM_NOTE: [
        "station_info",
        "충전소 안내사항",
        None,
        SENSOR_DOMAIN,
        "mdi:information-outline",
        None,
    ],
    ITEM_LIMIT: [
        "station_limit",
        "이용자제한",
        None,
        BSENSOR_DOMAIN,
        "mdi:block-helper",
        None,
    ],
    ITEM_LIMIT_NOTE: [
        "station_limit_info",
        "이용제한사유",
        None,
        SENSOR_DOMAIN,
        "mdi:block-helper",
        None,
    ],
    ITEM_DEL: [
        "station_delete",
        "충전기정보 삭제",
        None,
        SENSOR_DOMAIN,
        "mdi:delete",
        None,
    ],
    ITEM_DEL_NOTE: [
        "station_delete_info",
        "충전기정보 삭제사유",
        None,
        SENSOR_DOMAIN,
        "mdi:delete",
        None,
    ],
}


ERROR_CODE = {
    "01": "어플리케이션 에러",
    "02": "데이터베이스 에러",
    "03": "데이터없음 에러",
    "04": "HTTP 에러",
    "05": "서비스 연결실패 에러",
    "10": "잘못된 요청 파라메터 에러",
    "11": "필수요청 파라메터가 없음",
    "12": "해당 오픈 API서비스가 없거나 폐기됨",
    "20": "서비스 접근거부",
    "21": "일시적으로 사용할 수 없는 서비스키",
    "22": "서비스 요청제한횟수 초과 에러",
    "30": "등록되지 않은 서비스키",
    "31": "기한만료된 서비스키",
    "32": "등록되지 않은 IP",
    "33": "서명되지 않은 호출",
    "34": "등록되지 않은 호출",
    "99": "기타 에러",
}

OPT_MONITORING = "monitoring"
OPTION_MONITOR = [(OPT_MONITORING, False, cv.boolean)]
OPTION_DEFAULT = [
    (CONF_API, "API key from data.go.kr", cv.string),
]
OPTION_LIST = OPTION_DEFAULT + OPTION_MONITOR
