#!/usr/bin/env python3
"""
System Requirements Checker for Forest Fire Prevention System
"""

import sys
import subprocess
import shutil

def check_python():
    """Check Python version"""
    version = sys.version_info
    if version >= (3, 9):
        print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} (requires 3.9+)")
        return False

def check_command(command, name, min_version=None):
    """Check if a command exists"""
    if shutil.which(command):
        try:
            result = subprocess.run([command, '--version'], 
                                  capture_output=True, text=True, timeout=5)
            version = result.stdout.split('\n')[0] if result.stdout else "unknown"
            print(f"✅ {name}: {version}")
            return True
        except:
            print(f"✅ {name}: installed")
            return True
    else:
        print(f"❌ {name}: not found")
        return False

def check_port(port):
    """Check if a port is available"""
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    if result == 0:
        print(f"⚠️  Port {port} is in use")
        return False
    else:
        print(f"✅ Port {port} is available")
        return True

def check_mongodb():
    """Check MongoDB connection"""
    try:
        result = subprocess.run(['mongosh', '--eval', 'db.adminCommand("ping")'],
                              capture_output=True, text=True, timeout=5)
        if 'ok: 1' in result.stdout or result.returncode == 0:
            print("✅ MongoDB is running and accessible")
            return True
        else:
            print("❌ MongoDB is not responding")
            return False
    except:
        print("❌ Cannot connect to MongoDB")
        return False

def check_serial_ports():
    """Check for available serial ports"""
    try:
        import serial.tools.list_ports
        ports = list(serial.tools.list_ports.comports())
        if ports:
            print(f"✅ Found {len(ports)} serial port(s):")
            for port in ports:
                print(f"   - {port.device}: {port.description}")
            return True
        else:
            print("⚠️  No serial ports found (ESP32 may not be connected)")
            return False
    except ImportError:
        print("⚠️  pyserial not installed (run: pip install pyserial)")
        return False

def main():
    print("🔥 Smart Forest Fire Prevention System")
    print("=" * 60)
    print("System Requirements Check\n")
    
    checks = []
    
    print("📦 Core Dependencies:")
    checks.append(check_python())
    checks.append(check_command('node', 'Node.js'))
    checks.append(check_command('npm', 'npm'))
    checks.append(check_command('mongosh', 'MongoDB Shell'))
    print()
    
    print("🔌 Database:")
    checks.append(check_mongodb())
    print()
    
    print("🌐 Ports:")
    checks.append(check_port(8000))  # FastAPI
    checks.append(check_port(3000))  # Next.js
    print()
    
    print("📡 Hardware:")
    check_serial_ports()
    print()
    
    print("=" * 60)
    passed = sum(checks)
    total = len(checks)
    
    if passed == total:
        print(f"✅ All checks passed! ({passed}/{total})")
        print("\n🚀 You're ready to start the system!")
        print("   Run: ./setup.sh")
    else:
        print(f"⚠️  {passed}/{total} checks passed")
        print("\n📚 Please install missing dependencies:")
        print("   - Python 3.9+: https://www.python.org/downloads/")
        print("   - Node.js 18+: https://nodejs.org/")
        print("   - MongoDB: https://www.mongodb.com/try/download/community")
        print("   - Or use Docker: docker run -d -p 27017:27017 mongo:latest")

if __name__ == "__main__":
    main()
