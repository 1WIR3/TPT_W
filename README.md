# 🌐 Torrent Peer Tracker

A web-based educational research tool for tracking peers on legal BitTorrent networks. Built for academic research, network analysis, and understanding BitTorrent protocol behavior.

## ✨ Features

- **🖥️ Web Interface**: Clean, modern web UI for easy peer tracking
- **📊 Real-time Tracking**: Live peer discovery and statistics
- **📈 Historical Reports**: Store and analyze tracking sessions over time
- **📄 Export Options**: CSV and JSON export for data analysis
- **🔧 Protocol Compliant**: Proper BitTorrent protocol implementation
- **🎯 Educational Focus**: Designed for research and learning purposes

## 🚀 Quick Start

### Prerequisites

```bash
pip install flask requests bencodepy
```

### Installation

1. **Clone or download the script**
2. **Run the application:**
   ```bash
   python app.py
   ```
3. **Open your browser and navigate to:**
   - Main tracker: `http://localhost:5000`
   - Reports dashboard: `http://localhost:5000/reports`

## 📖 Usage

### Basic Tracking

1. **Navigate to the main page** (`http://localhost:5000`)
2. **Enter torrent details:**
   - **Info Hash**: 40-character hex string (SHA-1 hash of torrent info)
   - **Tracker URL**: BitTorrent tracker announce URL
   - **Port**: Network port (default: 6881)
3. **Click "Track Peers"** to discover active peers

### Viewing Reports

1. **Go to Reports page** (`/reports`)
2. **View historical tracking sessions**
3. **Export data** using CSV or JSON buttons
4. **Refresh** to see latest tracking results

## 🎓 Educational Use Cases

- **Protocol Research**: Study BitTorrent tracker communication
- **Network Analysis**: Analyze peer distribution and behavior
- **Academic Projects**: Research P2P networking concepts
- **Legal Torrents**: Track peers for open-source distributions
  - Linux ISOs (Ubuntu, Debian, etc.)
  - Open-source software releases
  - Academic datasets
  - Creative Commons content

## 📊 Report Data

The application tracks and stores:

- **Peer Information**: IP addresses and ports
- **Swarm Statistics**: Seeders, leechers, and total peers
- **Tracker Responses**: Complete protocol responses
- **Session History**: Timestamped tracking sessions
- **Export Formats**: CSV for spreadsheets, JSON for analysis

## 🔧 Technical Details

### BitTorrent Protocol Support

- **Proper Peer ID Generation**: Follows BitTorrent conventions
- **Bencoding Support**: Correctly parses tracker responses
- **Compact Format**: Handles both compact and dictionary peer lists
- **Error Handling**: Robust error management and reporting

### Web Technology Stack

- **Backend**: Flask (Python web framework)
- **Frontend**: Modern HTML5/CSS3/JavaScript
- **Data Storage**: In-memory with export options
- **Protocol**: HTTP REST API for tracking operations

## 📁 File Structure

```
torrent-peer-tracker/
├── app.py                 # Main application
├── templates/
│   ├── index.html         # Main tracking interface
│   └── reports.html       # Reports dashboard
├── tracker_report.csv     # Generated CSV exports
├── tracker_report.json    # Generated JSON exports
└── README.md             # This file
```

## 🚨 Important Notes

### Legal and Ethical Use

- **Educational Purpose Only**: This tool is designed for research and education
- **Legal Torrents Only**: Use only with legally distributed content
- **Respect Networks**: Don't overwhelm trackers with excessive requests
- **Privacy Considerations**: Be mindful of network privacy when analyzing peers

### Limitations

- **No File Downloads**: This tool only tracks peers, doesn't download content
- **Tracker Dependent**: Results depend on tracker availability and response
- **Network Restrictions**: Some networks may block BitTorrent traffic
- **Rate Limiting**: Some trackers implement rate limiting

## 🛠️ Development

### Adding Features

The modular design makes it easy to extend:

- **New Export Formats**: Add functions in the `TorrentTracker` class
- **Additional Analytics**: Extend the reporting dashboard
- **Enhanced UI**: Modify templates for improved user experience
- **Database Storage**: Replace in-memory storage with persistent database

### API Endpoints

- `GET /` - Main tracking interface
- `POST /track` - Track peers for a torrent
- `GET /reports` - Reports dashboard
- `GET /api/reports` - JSON API for report data
- `GET /export/csv` - Download CSV report
- `GET /export/json` - Download JSON report

## 📜 License

This project is intended for educational and research purposes. Please ensure compliance with local laws and BitTorrent tracker terms of service.

## 🤝 Contributing

This is an educational tool. Suggestions for improvements in protocol implementation, user interface, or additional research features are welcome.

## 📞 Support

For technical issues or questions about BitTorrent protocol implementation, refer to:
- [BitTorrent Protocol Specification](http://bittorrent.org/beps/bep_0003.html)
- [Tracker Protocol Documentation](http://bittorrent.org/beps/bep_0023.html)

---

**Remember**: Always use this tool responsibly and only with legal torrents for educational and research purposes. 🎓
