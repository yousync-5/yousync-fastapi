# utils_s3.py
import os, boto3, json, urllib.parse, httpx, logging
from typing import Any, Optional

_s3 = boto3.client(
    "s3",
    aws_access_key_id    = os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key= os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name          = os.getenv("AWS_REGION", "ap-northeast-2"),
)

def _parse_s3(url: str) -> Optional[tuple[str, str]]:
    if url.startswith("s3://"):
        p = urllib.parse.urlparse(url)
        return p.netloc, p.path.lstrip("/")
    if ".s3." in url:               # virtual-hosted
        p = urllib.parse.urlparse(url)
        return p.netloc.split(".s3.")[0], p.path.lstrip("/")
    return None

async def load_json(url: Optional[str]) -> Optional[Any]:
    if not url:
        return None
    bk = _parse_s3(url)
    try:
        if bk:
            b, k = bk
            obj = _s3.get_object(Bucket=b, Key=k)
            return json.load(obj["Body"])
        async with httpx.AsyncClient(timeout=10.0) as c:
            r = await c.get(url); r.raise_for_status()
            return r.json()
    except Exception as e:
        logging.warning("pitch.json load error %s", e)
        return None

def presign(url: Optional[str], exp: int = 900) -> Optional[str]:
    if not url:
        return None
    bk = _parse_s3(url)
    if not bk:
        return url                   # 이미 퍼블릭
    b, k = bk
    return _s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": b, "Key": k},
        ExpiresIn=exp,
    )