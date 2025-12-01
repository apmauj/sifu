# 🛠️ SIFU Setup & Configuration Scripts

This directory contains setup and configuration scripts for SIFU.

## 📁 Scripts

### 🔧 Setup Scripts

- **`setup_https.py`** - Configure HTTPS/SSL certificates
- **`setup_production.py`** - Production environment setup
- **`setup_rbac.py`** - Configure Role-Based Access Control
- **`start_secure.py`** - Start server with security features
- **`start_server.py`** - Start development server

### 🎬 Demo Scripts

See `../demo/` for demonstration scripts.

## 🚀 Usage

```bash
# Run setup scripts
python -m scripts.setup.setup_https
python -m scripts.setup.setup_production
python -m scripts.setup.setup_rbac

# Start servers
python -m scripts.setup.start_server
python -m scripts.setup.start_secure
```

## 📝 Creating New Setup Scripts

1. Place in `scripts/setup/`
2. Name: `setup_*.py` or `start_*.py`
3. Include docstring explaining purpose
4. Use argparse for CLI arguments

Example:
```python
#!/usr/bin/env python3
"""
Setup script for X feature
Usage: python -m scripts.setup.my_setup
"""

def main():
    """Main setup logic"""
    pass

if __name__ == "__main__":
    main()
```

## 🗂️ Related Directories

- `../deploy/` - Deployment automation scripts
- `../monitoring/` - Monitoring and health check scripts
- `../util/` - Utility helper scripts
- `../archive/` - Legacy scripts (deprecated)
- `../demo/` - Demo and example scripts
