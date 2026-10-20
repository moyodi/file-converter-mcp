# file-converter-mcp

> **업로드 없이, 유료 결제 없이, 대화 한 줄로 끝나는 파일 변환 MCP**

변환 사이트에 들어가서 업로드하고, 기다리고, 고화질은 유료 결제하고…
이 MCP를 Cursor(또는 Claude 데스크톱 앱)에 연결하면 **대화 한 줄**로 내 컴퓨터 안에서 바로 변환됩니다.

- 🔒 **파일이 내 컴퓨터 밖으로 나가지 않아요** — 회사 문서, 클라이언트 파일도 안심
- 🆓 **무료 · 원본 화질 그대로 · 용량/개수 제한 없음**
- 🗂️ **폴더 통째로 일괄 변환**
- 🛡️ **원본은 절대 덮어쓰지 않음** — 결과는 `converted_형식` 폴더에 따로 저장

```
"바탕화면 촬영본 폴더 사진 전부 webp로 바꾸고 가로 1080으로 줄여줘"
→ 38개 변환 완료 · 156.2MB → 19.4MB (88% 절감)
```

---

## 지원 형식 (1단계: 이미지)

| 읽기 | 변환 |
|---|---|
| PNG · JPG · WebP · GIF · BMP · TIFF · **HEIC(아이폰 사진)** | JPG · PNG · WebP · GIF · BMP · TIFF |

## 도구 목록

| 도구 | 하는 일 |
|---|---|
| `convert_file` | 파일 하나 변환 (화질·가로 크기 조절 가능) |
| `convert_folder` | 폴더 안 이미지 일괄 변환 (하위 폴더 포함 선택) |
| `list_formats` | 지원 형식 확인 |

---

## 설치 (맥 + Cursor 기준)

### 1. 내려받기

터미널을 열고 아래를 그대로 붙여넣으세요.

```bash
cd ~
git clone https://github.com/moyodi/file-converter-mcp.git
cd file-converter-mcp
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

> Python이 없다는 메시지가 나오면 [python.org](https://www.python.org/downloads/)에서 먼저 설치하세요. (3.10 이상)

### 2. 내 경로 확인

```bash
echo "$HOME/file-converter-mcp"
```

출력된 경로(예: `/Users/eunsong/file-converter-mcp`)를 아래 설정에 사용합니다.

### 3. Cursor에 연결

Cursor 설정 → **MCP** → **Add new global MCP server** 클릭 → 열리는 `mcp.json`에 붙여넣기
(`/Users/내이름` 부분을 2번에서 확인한 경로로 바꾸세요)

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

저장 후 Cursor를 재시작하면 MCP 목록에 `file-convert`가 초록불로 뜹니다.

<details>
<summary>Claude 데스크톱 앱에 연결하려면</summary>

`~/Library/Application Support/Claude/claude_desktop_config.json` 파일에 위와 같은 내용을 넣고 앱을 재시작하세요.

</details>

---

## 사용 예시

Cursor 채팅(Agent 모드)에서 이렇게 말하면 됩니다.

- `~/Downloads/IMG_1234.HEIC 를 jpg로 바꿔줘`
- `~/Desktop/로고.png 를 webp로 바꿔줘, 화질 80`
- `~/Desktop/상품사진 폴더 전부 jpg로, 가로 1000px로 줄여서`
- `~/Pictures/여행 폴더 하위 폴더까지 전부 webp로 변환해줘`

> 💡 Finder에서 파일을 우클릭하고 `option` 키를 누르면 **"경로 이름 복사"**가 나와요. 그대로 붙여넣으면 됩니다.

---

## 로드맵

- [x] 1단계 — 이미지 변환 (HEIC 포함)
- [ ] 2단계 — 엑셀 ↔ CSV ↔ JSON
- [ ] 3단계 — DOCX · PPTX · XLSX → PDF (LibreOffice)
- [ ] 4단계 — HWP → PDF / DOCX
- [ ] 5단계 — 영상 · 음성 (MOV → MP4, MP4 → GIF, 영상 → MP3)

---

Made by [MYD Studio](https://myd-studio.com) · Python + [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) + Pillow
