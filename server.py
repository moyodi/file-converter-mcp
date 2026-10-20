"""
file-converter-mcp
업로드 없이, 유료 결제 없이, 대화 한 줄로 끝나는 파일 변환 MCP 서버

1단계: 이미지 변환 (PNG · JPG · WebP · HEIC · GIF · BMP · TIFF)
- 파일은 내 컴퓨터 밖으로 나가지 않습니다.
- 원본은 절대 덮어쓰지 않고, 변환 결과는 별도 폴더에 저장합니다.
"""

from __future__ import annotations

import sys
from pathlib import Path

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from PIL import Image, ImageOps

# 아이폰 사진(HEIC) 지원 — 설치돼 있으면 자동으로 켜짐
try:
    from pillow_heif import register_heif_opener

    register_heif_opener()
    HEIC_SUPPORTED = True
except ImportError:
    HEIC_SUPPORTED = False


mcp = MCPServer(
    name="file-convert",
    instructions=(
        "로컬 파일 변환 도구입니다. 사용자가 이미지 확장자 변경, 용량 줄이기, "
        "크기 줄이기, 폴더 일괄 변환을 요청하면 이 도구를 사용하세요. "
        "경로는 사용자 컴퓨터의 절대 경로(~ 사용 가능)를 넘기세요."
    ),
)

# 바꿀 수 있는 형식: 사용자가 쓰는 이름 → Pillow 저장 형식
OUTPUT_FORMATS = {
    "jpg": "JPEG",
    "jpeg": "JPEG",
    "png": "PNG",
    "webp": "WEBP",
    "gif": "GIF",
    "bmp": "BMP",
    "tiff": "TIFF",
}

# 읽을 수 있는 확장자
INPUT_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".tif", ".tiff"}
if HEIC_SUPPORTED:
    INPUT_EXTENSIONS |= {".heic", ".heif"}

# 투명 배경을 지원하지 않는 형식
NO_ALPHA = {"JPEG", "BMP"}


def _log(msg: str) -> None:
    # stdio MCP는 표준출력을 통신에 쓰므로, 로그는 반드시 stderr로
    print(msg, file=sys.stderr)


def _human_size(num_bytes: int) -> str:
    size = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024 or unit == "GB":
            return f"{size:.1f}{unit}" if unit != "B" else f"{int(size)}B"
        size /= 1024
    return f"{size:.1f}GB"


def _unique_path(path: Path) -> Path:
    """같은 이름 파일이 있으면 _1, _2 를 붙여서 덮어쓰기 방지"""
    if not path.exists():
        return path
    i = 1
    while True:
        candidate = path.with_name(f"{path.stem}_{i}{path.suffix}")
        if not candidate.exists():
            return candidate
        i += 1


def _normalize_format(to_format: str) -> tuple[str, str]:
    key = to_format.lower().lstrip(".").strip()
    if key not in OUTPUT_FORMATS:
        raise ToolError(
            f"'{to_format}' 형식은 아직 지원하지 않아요. "
            f"가능한 형식: {', '.join(sorted(set(OUTPUT_FORMATS)))}"
        )
    ext = "jpg" if key == "jpeg" else key
    return OUTPUT_FORMATS[key], ext


def _convert_one(
    src: Path,
    out_dir: Path,
    pil_format: str,
    ext: str,
    quality: int,
    max_width: int | None,
) -> dict:
    with Image.open(src) as img:
        # 휴대폰 사진이 옆으로 눕는 문제 방지 (EXIF 회전값 반영)
        img = ImageOps.exif_transpose(img)

        # 가로 크기 제한 (비율 유지, 확대는 하지 않음)
        if max_width and img.width > max_width:
            ratio = max_width / img.width
            img = img.resize((max_width, round(img.height * ratio)), Image.LANCZOS)

        # JPG처럼 투명도가 없는 형식은 흰 배경으로 합성
        if pil_format in NO_ALPHA and img.mode in ("RGBA", "LA", "P"):
            img = img.convert("RGBA")
            background = Image.new("RGB", img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[-1])
            img = background
        elif pil_format in NO_ALPHA and img.mode != "RGB":
            img = img.convert("RGB")

        save_kwargs: dict = {}
        if pil_format in ("JPEG", "WEBP"):
            save_kwargs["quality"] = quality
        if pil_format == "JPEG":
            save_kwargs["optimize"] = True
        if pil_format == "PNG":
            save_kwargs["optimize"] = True

        out_dir.mkdir(parents=True, exist_ok=True)
        dst = _unique_path(out_dir / f"{src.stem}.{ext}")
        img.save(dst, pil_format, **save_kwargs)
        width, height = img.size

    before, after = src.stat().st_size, dst.stat().st_size
    return {
        "원본": str(src),
        "결과": str(dst),
        "크기": f"{width}x{height}",
        "용량": f"{_human_size(before)} → {_human_size(after)}",
        "_before": before,
        "_after": after,
    }


@mcp.tool()
def list_formats() -> dict:
    """변환할 수 있는 파일 형식 목록을 알려줍니다."""
    return {
        "읽기 가능": sorted(e.lstrip(".") for e in INPUT_EXTENSIONS),
        "변환 가능": sorted({"jpg", "png", "webp", "gif", "bmp", "tiff"}),
        "HEIC(아이폰 사진) 지원": HEIC_SUPPORTED,
    }


@mcp.tool()
def convert_file(
    path: str,
    to_format: str,
    quality: int = 90,
    max_width: int | None = None,
    output_dir: str | None = None,
) -> dict:
    """
    이미지 파일 하나를 다른 형식으로 변환합니다. 원본은 그대로 둡니다.

    Args:
        path: 변환할 파일 경로 (예: ~/Desktop/photo.heic)
        to_format: 바꿀 형식 (jpg, png, webp, gif, bmp, tiff)
        quality: 화질 1~100 (jpg·webp에만 적용, 기본 90)
        max_width: 가로 최대 픽셀. 지정하면 비율 유지하며 줄임 (예: 1080)
        output_dir: 저장할 폴더. 비우면 원본 옆 'converted_형식' 폴더에 저장
    """
    src = Path(path).expanduser().resolve()
    if not src.is_file():
        raise ToolError(f"파일을 찾을 수 없어요: {src}")
    if src.suffix.lower() not in INPUT_EXTENSIONS:
        raise ToolError(f"이미지 파일이 아니거나 아직 지원하지 않는 형식이에요: {src.name}")

    pil_format, ext = _normalize_format(to_format)
    quality = max(1, min(100, quality))
    out_dir = Path(output_dir).expanduser().resolve() if output_dir else src.parent / f"converted_{ext}"

    result = _convert_one(src, out_dir, pil_format, ext, quality, max_width)
    _log(f"[file-convert] {src.name} → {result['결과']}")
    return {k: v for k, v in result.items() if not k.startswith("_")}


@mcp.tool()
def convert_folder(
    folder: str,
    to_format: str,
    quality: int = 90,
    max_width: int | None = None,
    include_subfolders: bool = False,
    output_dir: str | None = None,
) -> dict:
    """
    폴더 안의 이미지를 한 번에 변환합니다. 원본은 그대로 둡니다.

    Args:
        folder: 이미지가 들어 있는 폴더 경로 (예: ~/Desktop/촬영본)
        to_format: 바꿀 형식 (jpg, png, webp, gif, bmp, tiff)
        quality: 화질 1~100 (jpg·webp에만 적용, 기본 90)
        max_width: 가로 최대 픽셀. 지정하면 비율 유지하며 줄임 (예: 1080)
        include_subfolders: 하위 폴더까지 포함할지 여부
        output_dir: 저장할 폴더. 비우면 대상 폴더 안 'converted_형식' 폴더에 저장
    """
    base = Path(folder).expanduser().resolve()
    if not base.is_dir():
        raise ToolError(f"폴더를 찾을 수 없어요: {base}")

    pil_format, ext = _normalize_format(to_format)
    quality = max(1, min(100, quality))
    out_root = Path(output_dir).expanduser().resolve() if output_dir else base / f"converted_{ext}"

    pattern = "**/*" if include_subfolders else "*"
    files = sorted(
        p for p in base.glob(pattern)
        if p.is_file()
        and p.suffix.lower() in INPUT_EXTENSIONS
        and out_root not in p.parents
        # 이전에 만든 converted_ 폴더 속 결과물은 다시 변환하지 않음
        and not any(part.startswith("converted_") for part in p.relative_to(base).parts[:-1])
    )
    if not files:
        return {"메시지": "변환할 이미지가 없어요.", "폴더": str(base)}

    done, failed = [], []
    total_before = total_after = 0
    for src in files:
        # 하위 폴더 구조를 결과 폴더에도 그대로 유지
        target_dir = out_root / src.parent.relative_to(base)
        try:
            r = _convert_one(src, target_dir, pil_format, ext, quality, max_width)
            total_before += r["_before"]
            total_after += r["_after"]
            done.append(Path(r["결과"]).name)
        except Exception as e:  # 한 장이 깨져도 나머지는 계속
            failed.append({"파일": src.name, "이유": str(e)})

    saved = (1 - total_after / total_before) * 100 if total_before else 0
    _log(f"[file-convert] {len(done)}/{len(files)}개 변환 → {out_root}")
    return {
        "변환 완료": f"{len(done)}개",
        "실패": failed,
        "저장 위치": str(out_root),
        "전체 용량": f"{_human_size(total_before)} → {_human_size(total_after)} ({saved:.0f}% 절감)"
        if saved >= 0
        else f"{_human_size(total_before)} → {_human_size(total_after)} ({-saved:.0f}% 증가)",
        "파일 목록": done[:50],
    }


if __name__ == "__main__":
    mcp.run()
