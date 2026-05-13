# ReconLab

ペネトレーションテスト・セキュリティ調査向けの偵察（Recon）自動化バックエンド。
ターゲットURLを登録し、複数のOSSツールを組み合わせてサブドメイン列挙・ディレクトリスキャン・HTTPプローブ・ポートスキャンを実行、結果をREST APIで取得できる。

## 使用ツール

| ツール | 用途 |
|--------|------|
| [subfinder](https://github.com/projectdiscovery/subfinder) | サブドメイン列挙 |
| [gobuster](https://github.com/OJ/gobuster) | ディレクトリ・ファイル列挙 |
| [httpx](https://github.com/projectdiscovery/httpx) | HTTPプローブ（タイトル・ステータス・レスポンスタイム等） |
| [nmap](https://nmap.org/) | ポートスキャン |

## 技術スタック

- **Python 3.12+** / **FastAPI** — REST API
- **SQLModel** / **SQLite** — データ永続化
- **uvicorn** — ASGIサーバー

---

## セットアップ

### 1. 外部ツールのインストール

macOS (Homebrew):

```bash
brew install nmap gobuster
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest
```

Linux (apt):

```bash
sudo apt install nmap gobuster
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest
```

### 2. Pythonパッケージのインストール

```bash
cd backend
pip install fastapi uvicorn sqlmodel
```

### 3. サーバー起動

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

起動時に `reconlab.db`（SQLite）が自動生成される。

### 4. API ドキュメント確認

```
http://localhost:8000/docs
```

---

## 使い方

### 基本フロー

```
1. ターゲット登録
2. スキャン作成（ツール指定）
3. スキャン実行（gobuster / subfinder / httpx / nmap）
4. 結果取得
```

---

### ターゲット管理

```bash
# ターゲット登録
curl -X POST http://localhost:8000/targets \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
# => {"id": 1, "url": "https://example.com"}

# ターゲット一覧
curl http://localhost:8000/targets

# ターゲット取得
curl http://localhost:8000/targets/1

# ターゲット削除
curl -X DELETE http://localhost:8000/targets/1
```

---

### スキャン作成

各ツールを実行する前に、スキャンレコードを作成する。

```bash
curl -X POST http://localhost:8000/scans \
  -H "Content-Type: application/json" \
  -d '{"target_id": 1, "tool": "subfinder"}'
# => {"id": 1, "target_id": 1, "tool": "subfinder", "status": "pending"}
```

`tool` には `subfinder` / `gobuster` / `httpx` / `nmap` を指定。

---

### サブドメイン列挙（subfinder）

```bash
# スキャン開始（バックグラウンド実行）
curl -X POST http://localhost:8000/scans/1/subfinder \
  -H "Content-Type: application/json" \
  -d '{"timeout": 30, "threads": 10}'

# ステータス確認
curl http://localhost:8000/scans/1

# 結果取得
curl http://localhost:8000/scans/1/subdomains
```

オプション:

| パラメータ | デフォルト | 説明 |
|-----------|-----------|------|
| `timeout` | 30 | タイムアウト（秒） |
| `threads` | 10 | 並列スレッド数 |

---

### ディレクトリ列挙（gobuster）

```bash
# スキャン開始
curl -X POST http://localhost:8000/scans/2/gobuster \
  -H "Content-Type: application/json" \
  -d '{"wordlist": "/usr/share/wordlists/dirb/common.txt", "threads": 10}'

# 結果取得
curl http://localhost:8000/scans/2/dirs
```

オプション:

| パラメータ | デフォルト | 説明 |
|-----------|-----------|------|
| `wordlist` | `/usr/share/wordlists/dirb/common.txt` | ワードリストパス |
| `mode` | `dir` | gobusterモード（`dir` / `dns`） |
| `extensions` | `` | 拡張子フィルタ（例: `php,html`） |
| `threads` | 10 | 並列スレッド数 |

---

### HTTPプローブ（httpx）

subfinder で見つけたサブドメインに対してまとめてプローブをかけることができる。

```bash
# サブドメインスキャン(scan_id=1)の結果を使ってhttpxを実行
curl -X POST http://localhost:8000/scans/3/httpx \
  -H "Content-Type: application/json" \
  -d '{"source_scan_id": 1, "timeout": 10, "threads": 50}'

# 単一ターゲットに対してhttpxを実行（source_scan_id を省略）
curl -X POST http://localhost:8000/scans/3/httpx \
  -H "Content-Type: application/json" \
  -d '{"timeout": 10, "threads": 50}'

# 結果取得
curl http://localhost:8000/scans/3/http-probes
```

オプション:

| パラメータ | デフォルト | 説明 |
|-----------|-----------|------|
| `source_scan_id` | null | サブドメイン列挙スキャンID（指定時はそのサブドメイン一覧をターゲットにする） |
| `timeout` | 10 | タイムアウト（秒） |
| `threads` | 50 | 並列スレッド数 |

---

### ポートスキャン（nmap）

```bash
curl -X POST http://localhost:8000/scan \
  -H "Content-Type: application/json" \
  -d '{"target": "example.com"}'
```

> nmap は同期実行でレスポンスにそのまま結果を返す。

---

### スキャン一覧・ステータス確認

```bash
# ターゲットに紐づくスキャン一覧
curl http://localhost:8000/targets/1/scans

# スキャン詳細（status: pending / running / done / error）
curl http://localhost:8000/scans/1
```

---

## API エンドポイント一覧

| Method | Path | 説明 |
|--------|------|------|
| POST | `/targets` | ターゲット登録 |
| GET | `/targets` | ターゲット一覧 |
| GET | `/targets/{id}` | ターゲット取得 |
| DELETE | `/targets/{id}` | ターゲット削除 |
| POST | `/scans` | スキャン作成 |
| GET | `/scans/{id}` | スキャン詳細・ステータス |
| GET | `/targets/{id}/scans` | ターゲット別スキャン一覧 |
| POST | `/scans/{id}/subfinder` | サブドメイン列挙開始 |
| GET | `/scans/{id}/subdomains` | サブドメイン結果取得 |
| POST | `/scans/{id}/gobuster` | ディレクトリ列挙開始 |
| GET | `/scans/{id}/dirs` | ディレクトリ結果取得 |
| POST | `/scans/{id}/httpx` | HTTPプローブ開始 |
| GET | `/scans/{id}/http-probes` | HTTPプローブ結果取得 |
| GET | `/scans/{id}/ports` | ポートスキャン結果取得 |
| POST | `/scan` | nmap スキャン（同期・レガシー） |

---

## 注意事項

- 本ツールは**自分が管理するシステム、または調査許可を得たシステムに対してのみ**使用すること。
- 無許可のスキャンは法律に抵触する可能性がある。
