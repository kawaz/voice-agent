# Cross-Platform Consideration: macOS and Raspberry Pi

## Overview

This document outlines the considerations for running the voice agent on both macOS and Raspberry Pi platforms. It covers platform-specific challenges, abstraction strategies, performance considerations, and hardware requirements.

## Table of Contents

1. [Platform-Dependent Abstraction](#platform-dependent-abstraction)
2. [Raspberry Pi Performance Considerations](#raspberry-pi-performance-considerations)
3. [Hardware Requirements](#hardware-requirements)
4. [Deployment Method Differences](#deployment-method-differences)
5. [Recommended Raspberry Pi Models](#recommended-raspberry-pi-models)
6. [Microphone and Speaker Selection](#microphone-and-speaker-selection)
7. [Development Environment Setup](#development-environment-setup)

## Platform-Dependent Abstraction

### Audio I/O Layer

The most significant platform difference is audio handling:

#### macOS
- **Native Support**: Core Audio framework
- **Web API**: Web Speech API (browser-based)
- **Libraries**: PortAudio, PyAudio for Python implementations
- **Latency**: Generally low with proper configuration

#### Raspberry Pi
- **ALSA**: Advanced Linux Sound Architecture (low-level)
- **PulseAudio**: Higher-level audio server
- **Libraries**: PortAudio with ALSA backend
- **Challenges**: Driver configuration, hardware-specific quirks

#### Abstraction Strategy
```typescript
interface AudioInterface {
  initialize(): Promise<void>;
  startRecording(): Promise<AudioStream>;
  stopRecording(): Promise<void>;
  playAudio(buffer: AudioBuffer): Promise<void>;
}

// Platform-specific implementations
class MacOSAudioInterface implements AudioInterface { }
class RaspberryPiAudioInterface implements AudioInterface { }
```

### Speech Recognition Abstraction

#### macOS Options
- Web Speech API (browser)
- Whisper API (cloud)
- Local Whisper (CPU/GPU accelerated)
- Google Cloud Speech-to-Text

#### Raspberry Pi Options
- Whisper Tiny/Base models (local)
- Julius (lightweight, offline)
- Pocketsphinx (very lightweight)
- Cloud APIs (network dependent)

#### Abstraction Strategy
```typescript
interface SpeechRecognizer {
  initialize(config: RecognizerConfig): Promise<void>;
  recognize(audio: AudioStream): Promise<TranscriptionResult>;
  destroy(): Promise<void>;
}

// Configurable implementations
const recognizer = createRecognizer(platform, {
  offline: isRaspberryPi,
  modelSize: isRaspberryPi ? 'tiny' : 'large'
});
```

### Wake Word Detection Abstraction

Platform-agnostic interface with different backends:

```typescript
interface WakeWordDetector {
  initialize(wakeWords: string[]): Promise<void>;
  startListening(): Promise<void>;
  onWakeWord(callback: (word: string) => void): void;
}
```

## Raspberry Pi Performance Considerations

### CPU and Memory Constraints

#### Model Selection Guidelines
| Component | macOS | Raspberry Pi 4 | Raspberry Pi 3B+ | Pi Zero 2 W |
|-----------|-------|----------------|------------------|-------------|
| Whisper Model | Large/Medium | Base/Small | Tiny | Tiny (limited) |
| Wake Word | Any | Porcupine/Picovoice | Porcupine | Minimal only |
| Concurrent Processes | Unlimited | 3-4 | 2-3 | 1-2 |
| RAM Usage Target | < 4GB | < 2GB | < 1GB | < 512MB |

### Performance Optimization Strategies

#### 1. Audio Processing
- **Buffer Size**: Larger buffers on Pi (512-1024 samples vs 256 on macOS)
- **Sample Rate**: Consider 16kHz on Pi vs 44.1kHz on macOS
- **Bit Depth**: 16-bit on Pi is sufficient

#### 2. Model Optimization
- **Quantization**: Use INT8 quantized models where possible
- **Model Pruning**: Remove unnecessary layers
- **Caching**: Aggressive caching of recognition results

#### 3. Resource Management
```python
# Example: Adaptive quality based on CPU load
async def adaptive_recognition():
    cpu_usage = get_cpu_usage()
    if cpu_usage > 80:
        switch_to_cloud_api()
    elif cpu_usage > 60:
        use_smaller_model()
    else:
        use_optimal_model()
```

### Thermal Management
- Monitor CPU temperature
- Implement throttling at 70°C
- Consider passive/active cooling for 24/7 operation

## Hardware Requirements

### macOS Requirements
- **Minimum**: MacBook Air M1 or Intel i5
- **Recommended**: M1 Pro/Max or Intel i7
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 10GB for models and dependencies
- **Microphone**: Built-in or USB (any quality)

### Raspberry Pi Requirements

#### Minimum Configuration
- **Model**: Raspberry Pi 3B+
- **RAM**: 1GB
- **Storage**: 16GB SD card (Class 10)
- **Power**: 2.5A power supply
- **Cooling**: Heatsinks required

#### Recommended Configuration
- **Model**: Raspberry Pi 4 (4GB/8GB)
- **RAM**: 4GB minimum
- **Storage**: 32GB SD card or SSD via USB
- **Power**: 3A power supply (official)
- **Cooling**: Active cooling (fan)

#### Additional Hardware
- **Audio HAT**: For better audio quality
- **RTC Module**: For offline time keeping
- **UPS**: For power stability

## Deployment Method Differences

### macOS Deployment

#### Development
```bash
# Clone repository
git clone https://github.com/kawaz/voice-agent
cd voice-agent

# Install dependencies
npm install

# Run development server
npm run dev
```

#### Production
```bash
# Build application
npm run build

# Option 1: Run as service
npm run start

# Option 2: Package as macOS app
npm run package:macos
```

### Raspberry Pi Deployment

#### Initial Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y nodejs npm python3-pip portaudio19-dev

# Audio setup
sudo apt install -y alsa-utils pulseaudio
```

#### Application Deployment
```bash
# Clone and setup
git clone https://github.com/kawaz/voice-agent
cd voice-agent

# Install with Pi-specific flags
npm install --build-from-source

# Configure for Pi
cp config/raspberry-pi.json config/local.json

# Setup systemd service
sudo cp deploy/voice-agent.service /etc/systemd/system/
sudo systemctl enable voice-agent
sudo systemctl start voice-agent
```

#### Docker Deployment (Recommended)
```dockerfile
# Dockerfile.pi
FROM balenalib/raspberry-pi-debian:bullseye

RUN apt-get update && apt-get install -y \
    nodejs npm python3-pip portaudio19-dev \
    alsa-utils pulseaudio

WORKDIR /app
COPY . .
RUN npm install --production

CMD ["npm", "start"]
```

```bash
# Build and run
docker build -f Dockerfile.pi -t voice-agent-pi .
docker run -d --device /dev/snd --restart unless-stopped voice-agent-pi
```

## Recommended Raspberry Pi Models

### Production Use

#### Raspberry Pi 4 (8GB) - Best Choice
- **Pros**: 
  - Sufficient RAM for larger models
  - Quad-core 1.5GHz processor
  - USB 3.0 for fast storage
  - Gigabit Ethernet
- **Cons**: Higher power consumption (3A required)
- **Use Case**: Full-featured voice agent with local processing

#### Raspberry Pi 4 (4GB) - Good Balance
- **Pros**: 
  - Good price/performance ratio
  - Handles most voice tasks well
  - Lower cost than 8GB model
- **Cons**: Limited multitasking with large models
- **Use Case**: Standard voice agent deployment

### Development/Testing

#### Raspberry Pi 3B+
- **Pros**: 
  - Widely available
  - Lower power consumption
  - Adequate for basic testing
- **Cons**: 
  - Limited to lightweight models
  - Slower processing
- **Use Case**: Development and lightweight deployments

### Not Recommended

#### Raspberry Pi Zero 2 W
- Too limited for real-time voice processing
- Consider only for wake word detection nodes

#### Raspberry Pi Pico
- Microcontroller, not suitable for this application

## Microphone and Speaker Selection

### USB Microphones (Recommended)

#### Budget Option: Kinobo Akiro
- **Price**: ~$15-20
- **Pros**: Plug-and-play, omnidirectional
- **Cons**: Basic quality
- **Platform**: Works on both macOS and Pi

#### Mid-Range: Blue Snowball iCE
- **Price**: ~$40-50
- **Pros**: Good quality, cardioid pattern
- **Cons**: Larger size
- **Platform**: Excellent on both platforms

#### Premium: Audio-Technica ATR2100x-USB
- **Price**: ~$70-80
- **Pros**: Professional quality, multiple patterns
- **Platform**: Ideal for high-quality recognition

### I2S Microphones (Raspberry Pi Specific)

#### SeeedStudio ReSpeaker 2-Mics Pi HAT
- **Price**: ~$15-20
- **Pros**: 
  - Dual microphone array
  - Built-in algorithms
  - LED indicators
- **Setup**:
  ```bash
  git clone https://github.com/respeaker/seeed-voicecard
  cd seeed-voicecard
  sudo ./install.sh
  ```

#### Adafruit I2S MEMS Microphone
- **Price**: ~$10-15
- **Pros**: Very compact, low power
- **Cons**: Requires I2S configuration

### Speakers

#### USB Speakers
- **Recommended**: Any USB 2.0 powered speakers
- **Example**: Creative Pebble ($25-30)
- **Setup**: Plug-and-play on both platforms

#### 3.5mm Audio
- **macOS**: Built-in or any 3.5mm speakers
- **Raspberry Pi**: Requires good power supply
- **Note**: Pi's 3.5mm output quality varies

#### I2S Audio DACs
- **Example**: HiFiBerry DAC+
- **Pros**: High-quality audio output
- **Setup**: Requires device tree overlay configuration

### Bluetooth Audio
- **Pros**: Wireless, convenient
- **Cons**: 
  - Latency issues
  - Connection stability
  - Power consumption
- **Recommendation**: Avoid for real-time voice interaction

## Development Environment Setup

### macOS Development Environment

#### Prerequisites
```bash
# Install Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Node.js and Python
brew install node python@3.11

# Install audio libraries
brew install portaudio

# Install development tools
brew install git wget
```

#### IDE Setup
```bash
# VS Code with extensions
brew install --cask visual-studio-code

# Install extensions
code --install-extension dbaeumer.vscode-eslint
code --install-extension esbenp.prettier-vscode
code --install-extension ms-vscode.vscode-typescript-next
```

### Raspberry Pi Development Environment

#### Option 1: Direct Development on Pi

```bash
# Enable SSH
sudo systemctl enable ssh
sudo systemctl start ssh

# Install development tools
sudo apt install -y git vim build-essential

# Install Node.js (via NodeSource)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Python and audio libraries
sudo apt install -y python3-pip python3-venv
sudo apt install -y portaudio19-dev python3-pyaudio
```

#### Option 2: Cross-Platform Development

##### Setup on macOS
```bash
# Install cross-compilation tools
brew install arm-linux-gnueabihf-binutils

# Setup remote development
npm install -g remote-sync
```

##### VS Code Remote Development
1. Install "Remote - SSH" extension
2. Configure SSH connection to Pi
3. Develop on macOS, run on Pi

#### Option 3: Docker Development

```bash
# On macOS - build for ARM
docker buildx build --platform linux/arm/v7 -t voice-agent-pi .

# Transfer to Pi
docker save voice-agent-pi | ssh pi@raspberrypi docker load
```

### Testing Framework

#### Unit Tests
```bash
# Same on both platforms
npm test
```

#### Integration Tests
```javascript
// platform-test.js
const platform = process.platform === 'darwin' ? 'macos' : 'linux';
const audioTests = require(`./tests/${platform}/audio`);
```

#### Hardware-in-Loop Testing
```bash
# Raspberry Pi specific
sudo npm run test:hardware
```

### Debugging Tools

#### macOS
- Chrome DevTools (for web interface)
- Activity Monitor (resource usage)
- Console.app (system logs)

#### Raspberry Pi
- `htop` - Process monitoring
- `vcgencmd` - Hardware monitoring
- `journalctl` - System logs
- `alsamixer` - Audio debugging

### Performance Profiling

#### macOS
```bash
# CPU profiling
npm run profile:cpu

# Memory profiling
npm run profile:memory
```

#### Raspberry Pi
```bash
# Monitor resources
./scripts/monitor-pi.sh

# Check thermal throttling
vcgencmd measure_temp
vcgencmd get_throttled
```

## Conclusion

Successfully running the voice agent on both macOS and Raspberry Pi requires careful consideration of platform differences. Key strategies include:

1. **Abstract platform-specific code** early in development
2. **Choose appropriate models** based on hardware capabilities
3. **Optimize aggressively** for Raspberry Pi
4. **Test thoroughly** on target hardware
5. **Plan deployment** strategy based on use case

With proper abstraction and optimization, the same codebase can effectively serve both platforms while maintaining good performance and user experience.