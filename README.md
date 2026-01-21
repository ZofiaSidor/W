# Legal Act Change Tracker

A Python-based system for tracking legal amendments using blockchain-inspired hash-chaining technology and AI-powered simplification.

## 🎯 Overview

This project implements an immutable change tracking system for legal documents. It combines:
- **Hash-chaining** (blockchain-like) for tamper-proof amendment history
- **LLM integration** for converting complex legal text into plain language
- **FastAPI** for REST API endpoints
- **XML parsing** for ingesting legal documents from ISAP

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Verify Installation
```bash
python main.py
```
Expected output: `✅ RELEASE APPROVED - READY FOR PRODUCTION`

### 3. Start API Server
```bash
python -m uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Access API Documentation
Open browser: **http://localhost:8000/docs**

## 📁 Project Structure

```
W/
├── hash_chain.py          # Core hash-chaining engine
├── data_ingestion.py      # XML parser for legal documents
├── api.py                 # FastAPI REST endpoints
├── app.py                 # Alternative API implementation
├── main.py                # Entry point & orchestration
├── security_tests.py      # Security validation
├── final_validation.py    # Pre-release checks
├── crypto_utils.py        # Cryptographic utilities
├── file_utils.py          # File operations
├── xml_parser.py          # XML parsing utilities
├── tests.py               # Unit tests
├── START_HERE.py          # Quick start guide
├── config.json            # Configuration (gitignored)
└── constraints.txt        # System constraints
```

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API information |
| GET | `/health` | Health check |
| GET | `/amendments` | List all amendments |
| POST | `/amendments` | Add new amendment |
| POST | `/ingest` | Ingest XML document |
| GET | `/verify` | Verify chain integrity |
| GET | `/statistics` | System statistics |

## 🔐 Features

- **Immutable History**: Hash-chaining ensures amendments can't be altered without detection
- **AI Simplification**: LLM converts complex legal language to plain Polish
- **Integrity Verification**: Built-in cryptographic verification
- **REST API**: Full API for integration with web/mobile apps
- **XML Support**: Parse legal documents from government databases
- **Security Tested**: Comprehensive security validation

## 🛠️ Tech Stack

- **Backend**: Python 3.x
- **API Framework**: FastAPI
- **Hashing**: SHA-256
- **AI**: LLM integration (OpenAI, Claude, etc.)
- **Data Format**: JSON, XML

## 📊 Status

✅ **Production Ready**
- All tests passing
- Security validated
- Performance benchmarked

## 🤝 Contributing

This is a work-in-progress project. Contributions welcome!

## 📄 License

[Add license information]

---

**Note**: This project was developed as part of exploring blockchain-inspired solutions for legal tech applications.
