from dotenv import load_dotenv
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

def get_env_var(name: str, default: str = None) -> str:
    value = os.getenv(name, default)
    if value is None:
        raise ValueError(f"Biến môi trường {name} không được định nghĩa trong .env")
    return value

CRAWL_DB_CONFIG = {
    "host": get_env_var("CRAWL_DB_HOST", "localhost"),
    "port": get_env_var("CRAWL_DB_PORT", "5432"),
    "database": get_env_var("CRAWL_DB_NAME", "crawl_db"),
    "user": get_env_var("CRAWL_DB_USER", "postgres"),
    "password": get_env_var("CRAWL_DB_PASSWORD", "để mật khẩu của bạn")
}

TRAINING_DB_CONFIG = {
    "host": get_env_var("DASHBOARD_DB_HOST", "localhost"),
    "port": get_env_var("DASHBOARD_DB_PORT", "5432"),
    "database": get_env_var("DASHBOARD_DB_NAME", "dashboard_db"),
    "user": get_env_var("DASHBOARD_DB_USER", "postgres"),
    "password": get_env_var("DASHBOARD_DB_PASSWORD", "để mật khẩu postgreSQL của bạn")
}

MODEL_PATH = get_env_var("MODEL_PATH", "vị trí để file model .pth của bạn")
TRAINING_SERVICE_PORT = int(get_env_var("TRAINING_SERVICE_PORT", "8002"))
PHOBERT_MODEL_NAME = get_env_var("PHOBERT_MODEL_NAME", "vinai/phobert-base")
NUM_CLASSES = int(get_env_var("NUM_CLASSES", "3"))

SUSPICIOUS_URLS = [
    "https://www.facebook.com/viettan",
    "https://www.facebook.com/uocmoviettan",
    "https://www.facebook.com/nvdai0906",
    "https://www.facebook.com/profile.php?id=100068636220431",
    "https://www.facebook.com/groups/662872460757443/",
    "https://www.facebook.com/groups/662872460757443/user/100089083968498/",
    "https://www.facebook.com/nguyen.quang.517136/",
    "https://www.facebook.com/profile.php?id=100008185748988",
    "https://www.facebook.com/dongmauviet1990",
    "https://www.facebook.com/PolishEmbassyHanoi",
    "https://www.facebook.com/nguyenvandai0906/",
    "https://www.facebook.com/huuthanh.hoang.503"
]

TRUSTED_URLS = [
    "https://facebook.com/thongtinchinhphu",
    "https://facebook.com/BoYTe",
    "https://facebook.com/bo.congan",
    "https://facebook.com/boGDDT",
    "https://facebook.com/MICVietnam",
    "https://facebook.com/baonhandan",
    "https://facebook.com/VTVfan",
    "https://facebook.com/TTXVN",
    "https://facebook.com/baoquandoinhandan",
    "https://facebook.com/ubndhanoi",
    "https://facebook.com/ubndtp",
    "https://facebook.com/danang.gov.vn",
    "https://facebook.com/chongtingia",
    "https://facebook.com/vafc.mic",
    "https://facebook.com/VietnamMOF",
    "https://facebook.com/MOFVietnam",
    "https://facebook.com/MARDVietnam",
    "https://facebook.com/BGTVT",
    "https://facebook.com/BVHTTDL",
    "https://facebook.com/VOVfan",
    "https://facebook.com/congan.com.vn",
    "https://facebook.com/SaigonGiaiPhong",
    "https://facebook.com/baodaidoanket",
    "https://facebook.com/ThanhTraChinhPhu",
    "https://facebook.com/an.toan.thuc.pham",
    "https://facebook.com/qltt.gov.vn",
    "https://facebook.com/ubndnghean",
    "https://facebook.com/CanTho.gov.vn",
    "https://facebook.com/ubndquangninh",
    "https://facebook.com/TWDoan",
    "https://facebook.com/hoilhpnvietnam",
    "https://facebook.com/TongLienDoanLaoDongVietNam",
    "https://facebook.com/baophapluat",
    "https://facebook.com/kinhtedothi",
    "https://facebook.com/baolaodong",
    "https://facebook.com/baoHNMOI",
    "https://facebook.com/baotienphong",
    "https://facebook.com/VTCNow",
    "https://facebook.com/HTVOnline",
    "https://facebook.com/HanoiTV",
    "https://facebook.com/DRT.Danang",
    "https://facebook.com/TruyenHinhNhanDan",
    "https://facebook.com/giaoducthoidai",
    "https://facebook.com/suckhoedoisong",
    "https://facebook.com/baonongnghiep",
    "https://facebook.com/baokhoahocvaphattrien",
    "https://facebook.com/baocongthuong",
    "https://facebook.com/baophunuvietnam",
    "https://facebook.com/baogiaothong",
    "https://facebook.com/AnNinhThuDo",
    "https://facebook.com/thegioivavietnam",
    "https://facebook.com/QTVQuangNinh",
    "https://facebook.com/NTVNgheAn",
    "https://facebook.com/CTRTV",
    "https://facebook.com/THP.HaiPhong",
    "https://facebook.com/BTV.BinhDuong",
    "https://facebook.com/tnmtonline",
    "https://facebook.com/baoxaydung",
    "https://facebook.com/congantphcm",
    "https://facebook.com/baovanhoa",
    "https://facebook.com/vietnamplus",
    "https://facebook.com/tccs.vn",
    "https://facebook.com/QPTD.VN",
    "https://facebook.com/tapchidulich",
    "https://facebook.com/kinhtevietnam",
    "https://facebook.com/dangcongsan",
    "https://facebook.com/baocongly",
    "https://facebook.com/baovephapluat",
    "https://facebook.com/nguoilaodong",
    "https://facebook.com/anninhthegioi",
    "https://facebook.com/THTV.ThanhHoa",
    "https://facebook.com/DNRTV.DongNai",
    "https://facebook.com/LTV.LamDong",
    "https://facebook.com/BRTV.BaRiaVungTau",
    "https://facebook.com/ATV.AnGiang",
    "https://facebook.com/VOVgiaothong",
    "https://facebook.com/baothethaovhnt",
    "https://facebook.com/baocntt",
    "https://facebook.com/baohaiquan",
    "https://facebook.com/baochinhphu",
    "https://facebook.com/baodanang",
    "https://facebook.com/baoquangnam",
    "https://facebook.com/baothuathienhue",
    "https://facebook.com/baolongan",
    "https://facebook.com/baophuyen",
    "https://facebook.com/vnexpress.net",
    "https://facebook.com/dantri.com.vn",
    "https://facebook.com/tuoitre",
    "https://facebook.com/thanhnien",
    "https://facebook.com/baodautu",
    "https://facebook.com/baotintuc",
    "https://facebook.com/zaloanews",
    "https://facebook.com/VietNamNet",
    "https://facebook.com/ChinhphuVN",
    "https://facebook.com/quochoi",
    "https://www.facebook.com/thongtinchinhphu"
]

logger.info(f"CRAWL_DB_CONFIG: {CRAWL_DB_CONFIG}")
logger.info(f"TRAINING_DB_CONFIG: {TRAINING_DB_CONFIG}")
logger.info(f"TRAINING_SERVICE_PORT: {TRAINING_SERVICE_PORT}")
logger.info(f"MODEL_PATH: {MODEL_PATH}")
logger.info(f"PHOBERT_MODEL_NAME: {PHOBERT_MODEL_NAME}")
logger.info(f"NUM_CLASSES: {NUM_CLASSES}")
logger.info(f"SUSPICIOUS_URLS: {SUSPICIOUS_URLS}")
logger.info(f"TRUSTED_URLS: {TRUSTED_URLS}")
