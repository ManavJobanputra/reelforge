# ReelForge 🎬⚡

**ReelForge** is an end-to-end, serverless AI pipeline that transforms long-form landscape videos (such as podcasts, interviews, and masterclasses) into vertical, viral-ready short-form reels (TikTok, YouTube Shorts, Instagram Reels) with active speaker tracking and dynamic captions.

---

## 🌟 Key Features

- **Serverless Cloud GPU Processing**: Built on [Modal](https://modal.com/) leveraging NVIDIA L40S GPUs and CUDA 12.4 containers for fast parallel rendering.
- **High-Accuracy Transcription**: Powered by **WhisperX** (OpenAI Whisper large-v2 + wav2vec2 forced alignment) for word-level timestamps.
- **LLM Viral Moment Detection**: Automatically detects engaging 30–60s question-and-answer moments and stories using **Google Gemini** (`gemini-2.5-flash`).
- **Active Speaker Detection (LR-ASD)**: Integrates Lightweight and Robust Network for Active Speaker Detection (IJCV 2025) and S3FD face detection to identify who is speaking in real-time.
- **Intelligent Dynamic Re-Framing (9:16)**:
  - Dynamically crops landscape 16:9 frames to focus on the active speaker's face.
  - Automatically falls back to centered framing with Gaussian-blurred background padding when no single speaker is active.
- **Karaoke-Style Subtitles**: Renders synchronized ASS subtitles with Anton typography via `pysubs2` and FFmpeg.
- **AWS S3 Cloud Ingestion & Output**: Downloads source videos from and uploads generated reels to AWS S3.

---

## 🏗️ Architecture Pipeline

```text
[AWS S3 Source Video]
        │
        ▼
[Modal Container (NVIDIA L40S)]
        │
        ├─► 1. Extract 16kHz Mono Audio (FFmpeg)
        │
        ├─► 2. WhisperX: Transcribe & Align (Word-Level Timestamps)
        │
        ├─► 3. Google Gemini: Extract Engaging Segments (30-60s Q&A)
        │
        ├─► 4. S3FD Face Detection & LR-ASD Active Speaker Scoring
        │
        ├─► 5. Frame Generation: Dynamic Crop / Blurred Background (1080x1920)
        │
        ├─► 6. Burn Animated Subtitles (pysubs2 + Anton Font + FFmpeg)
        │
        ▼
[AWS S3 Destination (reel-forge bucket)]
```

---

## 📂 Repository Structure

```text
reelforge/
├── main.py                    # Modal serverless pipeline & FastAPI endpoint
├── requirements.txt            # Python dependencies (Torch, WhisperX, Modal, etc.)
├── ytdownload.py              # YouTube video downloader utility
├── .gitignore                 # Excluded environments, temp files, and media
├── eval/                      # Evaluation & benchmarking suite
│   └── eval_moments.py        # Gemini moment-selection validation script
└── asd/                       # Active Speaker Detection (LR-ASD) module
    ├── ASD.py                 # Core Active Speaker Detection runner
    ├── Columbia_test.py       # Inference & evaluation script
    ├── loss.py                # Loss functions for ASD training
    ├── dataLoader.py          # Data loaders for audio-visual streams
    ├── model/                 # Model architectures (Classifier, Encoder, S3FD)
    ├── utils/                 # Evaluation and metric calculation tools
    └── weight/                # Pretrained model weights (AVA, TalkSet)
```

---

## 📊 Evaluation: Gemini Moment Selection Validation

ReelForge includes an evaluation script (`eval/eval_moments.py`) to validate raw Gemini moment-selection responses across test videos.

### Metrics Evaluated

1. **Valid-JSON Rate**: Percentage of raw LLM outputs successfully parsed as JSON clip lists (stripping markdown fences).
2. **Duration Compliance (30–60s)**: Proportion of detected moments adhering strictly to the 30–60 second duration target.
3. **Non-Overlap Rate**: Fraction of videos whose extracted clips contain zero timestamp overlaps.

### Usage

```bash
python eval/eval_moments.py responses/*.json
```

Each JSON file contains the raw text output returned by Gemini for one video. The script outputs:
```text
responses: 20
valid JSON list: 20/20
clips in 30-60s: 38/40
overlap-free responses: 20/20
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- FFmpeg installed locally
- Modal account (`pip install modal && modal setup`)
- Google Gemini API key (`GEMINI_API_KEY`)
- AWS Credentials configured with S3 access

### Local Setup

```bash
git clone https://github.com/ManavJobanputra/reelforge.git
cd reelforge
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Deploy to Modal

1. Create required Modal secrets and volumes:
   ```bash
   modal secret create reelforge-secret GEMINI_API_KEY=your_key AUTH_TOKEN=your_token AWS_ACCESS_KEY_ID=your_id AWS_SECRET_ACCESS_KEY=your_secret
   modal volume create reelforge-model-cache
   ```

2. Deploy the app:
   ```bash
   modal deploy main.py
   ```

3. Trigger video processing:
   ```bash
   curl -X POST "https://<your-modal-app-url>/process_video" \
     -H "Authorization: Bearer <AUTH_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"s3_key": "raw_videos/sample.mp4"}'
   ```

---

## 📜 Acknowledgements & References

- [LR-ASD: Lightweight and Robust Network for Active Speaker Detection (IJCV 2025)](https://github.com/Junhua-Liao/Light-ASD)
- [WhisperX: Fast Automatic Speech Recognition with Word-Level Timestamps](https://github.com/m-bain/whisperX)
- [Modal Labs: Serverless Cloud Infrastructure](https://modal.com/)

