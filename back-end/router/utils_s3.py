import os, boto3, json, urllib.parse, httpx, logging
from typing import Any, Optional

# AWS S3 클라이언트 초기화 (환경변수에서 키/시크릿/리전 불러옴)
_s3 = boto3.client(
    "s3",
    aws_access_key_id     = os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name           = os.getenv("AWS_REGION", "ap-northeast-2"),
)

# 기본 버킷 이름을 환경 변수 또는 상수로 설정
DEFAULT_BUCKET = os.getenv("AWS_S3_BUCKET_NAME", "testgrid-pitch-bgvoice-yousync")

def _parse_s3(url: str) -> Optional[tuple[str, str]]:
    if not url:
        return None
    # 1) s3:// 접두사가 있는 경우 처리
    if url.startswith("s3://"):
        p = urllib.parse.urlparse(url)
        return p.netloc, p.path.lstrip("/")
    # 2) 버킷 가상 호스트 형식 URL ( .s3. 포함 ) 처리
    if ".s3." in url:
        p = urllib.parse.urlparse(url)
        bucket_name = p.netloc.split(".s3.")[0]
        return bucket_name, p.path.lstrip("/")
    # 3) 별도 프로토콜 없는 경우 -> S3 키로 간주
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme == "" and parsed.netloc == "":
        # 기본 버킷과 조합하여 반환
        return DEFAULT_BUCKET, parsed.path.lstrip("/")
    return None

async def load_json(url: Optional[str]) -> Any:
    if not url:
        return None
    bk = _parse_s3(url)
    try:
        if bk:
            # _parse_s3가 (bucket, key)를 반환한 경우 S3에서 객체 가져오기
            b, k = bk
            obj = _s3.get_object(Bucket=b, Key=k)
            return json.load(obj["Body"])
        # _parse_s3가 None이면 (예: 일반 http URL인 경우) httpx로 요청
        async with httpx.AsyncClient(timeout=10.0) as c:
            r = await c.get(url)
            r.raise_for_status()
            return r.json()
    except Exception as e:
        logging.warning("pitch.json load error %s", e)
        return None

def presign(url: Optional[str], exp: int = 900) -> Optional[str]:
    if not url:
        return None
    bk = _parse_s3(url)
    if bk:
        # S3 경로로 인식되면 프리사인 URL 생성
        b, k = bk
        return _s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": b, "Key": k},
            ExpiresIn=exp,
        )
    # S3 경로가 아니라고 판단된 경우 원본 그대로 반환 (이미 퍼블릭 URL 등)
    return url