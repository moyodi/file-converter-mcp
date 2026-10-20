# file-converter-mcp

로컬에서 이미지·영상·음성 파일을 변환하는 MCP 서버입니다.
Cursor나 Claude 데스크톱 앱에 연결해 채팅으로 변환을 요청할 수 있습니다.

변환 사이트에 파일을 올리고 내려받는 과정이 번거롭고, 회사 파일을 외부에 올리기도 애매해서 만들었습니다.
모든 변환은 내 컴퓨터 안에서 처리되고, 원본 파일은 수정하지 않습니다.

## 기능

- 이미지 형식 변환 (PNG, JPG, WebP, HEIC, GIF, BMP, TIFF), 화질·크기 조절
- 영상 형식 변환 (MOV, MP4, WebM 등), 영상 → GIF
- 영상에서 소리 추출 (MP3, M4A, WAV)
- 폴더 단위 일괄 변환

변환 결과는 원본이 있는 폴더 안에 `converted_형식` 폴더를 만들어 저장합니다.

## 설치

macOS, Python 3.10 이상 기준입니다.

```bash
cd ~
git clone https://github.com/moyodi/file-converter-mcp.git
cd file-converter-mcp
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

영상 변환에 필요한 FFmpeg는 위 설치 과정에서 함께 설치됩니다.

## Cursor 연결

`~/.cursor/mcp.json`에 아래 내용을 추가합니다. `/Users/내이름` 부분은 본인 경로로 바꿔주세요.
(터미널에서 `echo $HOME` 으로 확인할 수 있습니다)

```json
{
  "mcpServers": {
    "file-convert": {
      "command": "/Users/내이름/file-converter-mcp/.venv/bin/python",
      "args": ["/Users/내이름/file-converter-mcp/server.py"]
    }
  }
}
```

Cursor를 재시작한 뒤 설정의 MCP 항목에서 `file-convert`가 연결됐는지 확인합니다.

Claude 데스크톱 앱은 `~/Library/Application Support/Claude/claude_desktop_config.json`에 같은 내용을 넣으면 됩니다.

## 사용 예시

채팅에서 파일 경로와 원하는 형식을 말하면 됩니다.

```
~/Downloads/IMG_1234.HEIC jpg로 바꿔줘
~/Desktop/상품사진 폴더 전부 webp로, 가로 1000으로 줄여서
~/Desktop/IMG_0001.MOV mp4로 바꿔줘
이 영상 5초부터 3초만 gif로 만들어줘
이 영상에서 소리만 mp3로 뽑아줘
```

Finder에서 파일을 우클릭한 상태로 option 키를 누르면 "경로 이름 복사"로 경로를 복사할 수 있습니다.

## 도구

| 도구 | 설명 |
|---|---|
| `convert_file` | 이미지 1개 변환 |
| `convert_folder` | 폴더 안 이미지 일괄 변환 |
| `convert_video` | 영상·음성 1개 변환 |
| `convert_video_folder` | 폴더 안 영상·음성 일괄 변환 |
| `list_formats` | 지원 형식 확인 |

주요 옵션

- `quality` : 이미지는 1~100 (기본 90), 영상은 high / medium / low (기본 medium)
- `max_width` : 가로 최대 픽셀. 비율을 유지하며 줄이고, 원본보다 키우지는 않습니다.
- `start`, `duration` : 영상 구간 지정 (초 단위). GIF는 지정하지 않으면 앞 10초만 만듭니다.
- `mute` : 영상에서 소리를 빼고 저장합니다.
- `include_subfolders` : 폴더 변환 시 하위 폴더까지 포함합니다.

## 업데이트

```bash
cd ~/file-converter-mcp && git pull && .venv/bin/pip install -r requirements.txt
```

업데이트 후 Cursor를 재시작해주세요.

## 참고

- 본인이 소유하거나 사용 권한이 있는 파일에 사용해주세요.
- 사용한 라이브러리: [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk), [Pillow](https://python-pillow.org), [pillow-heif](https://github.com/bigcat88/pillow_heif), [imageio-ffmpeg](https://github.com/imageio/imageio-ffmpeg)
- 앞으로 엑셀 ↔ CSV, 문서 → PDF, HWP 변환을 추가해볼 예정입니다.
