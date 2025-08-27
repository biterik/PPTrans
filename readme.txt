# PPTrans - PowerPoint Translation Tool

A cross-platform desktop application for translating PowerPoint presentations while preserving all formatting, fonts, images, and layout.

![PPTrans Logo](assets/icon.png)

## Features

- 🌐 **Multi-language Translation**: Supports 100+ languages via Google Translate API
- 🎨 **Format Preservation**: Maintains fonts, sizes, colors, alignment, and all visual elements
- 📊 **Selective Translation**: Choose specific slide ranges to translate
- 🖥️ **Cross-platform**: Works on macOS (M1/M2), Windows, and Linux
- 📱 **User-friendly GUI**: Intuitive interface built with Tkinter
- 🔧 **Professional Logging**: Comprehensive debugging and error tracking
- ⚡ **Batch Processing**: Handle multiple slides efficiently

## Quick Start

### Prerequisites

- Python 3.11+
- Conda (recommended) or pip

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/PPTrans.git
cd PPTrans
```

2. Create conda environment:
```bash
conda env create -f environment.yml
conda activate pptrans
```

3. Run the application:
```bash
python src/main.py
```

### Building Executable

For macOS:
```bash
bash scripts/build.sh mac
```

For Windows:
```bash
scripts/build.bat windows
```

For Linux:
```bash
bash scripts/build.sh linux
```

## Usage

1. Launch PPTrans
2. Select your PowerPoint file (.pptx)
3. Choose slide range (e.g., "1-10" or "all")
4. Select source and target languages
5. Click "Translate" and wait for processing
6. Your translated presentation will be saved with "_translated" suffix

## Development

See [docs/development.md](docs/development.md) for detailed development setup and contribution guidelines.

## Architecture

- **GUI Layer**: Tkinter-based interface (`src/gui/`)
- **Core Logic**: Translation and PPTX processing (`src/core/`)
- **Utilities**: Logging, configuration, exceptions (`src/utils/`)

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Support

- 📖 Documentation: [docs/](docs/)
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/PPTrans/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/yourusername/PPTrans/discussions)