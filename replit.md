# Overview

This is "النبأ العظيم" (The Great News) - a comprehensive Flask-based Quran web application that provides multiple sections for exploring the Quran and its sciences. The application features an enhanced search interface with autocomplete functionality, five main navigation tabs (Search, Tafsir, Sciences, Mushafs, Language), and intelligent result ranking. It integrates local verses database with external API calls and presents content through a modern, responsive, Arabic-optimized RTL interface.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
- **Template Engine**: Jinja2 (Flask's default templating engine)
- **Styling**: Custom CSS with gradient header and modern tab navigation
- **Typography**: Cairo font from Google Fonts optimized for Arabic text
- **Layout**: Right-to-left (RTL) responsive design with mobile-first approach
- **Navigation**: Five-tab structure with JavaScript-powered tab switching
- **Structure**: Template inheritance with header, navigation tabs, and content sections

## Backend Architecture
- **Framework**: Flask (Python web framework)
- **Request Handling**: Single route handling both GET and POST requests
- **API Integration**: External API calls using the requests library
- **Error Handling**: Form validation and API error management
- **Logging**: Basic logging configuration for debugging

## Data Storage
- **Local Database**: verses_db.json containing Surah Al-Fatiha with authentic Arabic text and English tafsir
- **Hybrid Architecture**: Local data for Al-Fatiha, external API for additional Surahs
- **Session Management**: None (no user sessions required)
- **Data Loading**: verses_db.json loaded once at server startup for optimal performance

# Key Components

## Main Application (main.py)
- **Enhanced Search Engine**: Multiple endpoints for homepage, autocomplete, search, and Surah display
- **Autocomplete System**: Real-time suggestions for Surah names and verse references with 250ms debouncing
- **Advanced Search Logic**: Supports reference format (2:5), Surah names (Arabic/English), and text search
- **Result Ranking**: Intelligent scoring system prioritizing exact matches and keyword frequency
- **Search Results**: Displays only verse text with clickable links to view full Surah (no tafsir in search)
- **Surah Display**: Complete Surah viewing with all verses in clean, numbered format
- **Input Validation**: Comprehensive validation for reference format and Surah/Aya ranges
- **API Integration**: Optimized calls to Quran.com API v4 with proper error handling and timeout management
- **Text Processing**: Arabic text normalization for diacritics and character variants

## Template System
- **Base Template (layout.html)**: Provides header with site title "النبأ العظيم", navigation tabs, and footer
- **Content Template (index.html)**: Contains five tab sections with search functionality and placeholder content
- **Surah Template (surah.html)**: Displays complete Surah with all verses in clean, numbered format
- **Navigation Structure**: Search, Tafsir, Sciences, Mushafs, and Language tabs
- **Template Variables**: Passes search results, Surah data, and navigation between backend and frontend

## Static Assets
- **CSS Styling**: Custom responsive design with RTL support
- **Navigation**: Sticky navigation bar with logo and menu items
- **Form Styling**: Clean, accessible form design with proper labeling

# Data Flow

1. **User Request**: User accesses the homepage or submits search form
2. **Input Validation**: Backend validates Sura and Aya numbers
3. **API Call**: If valid, makes HTTP request to Quran.com API
4. **Response Processing**: Extracts tafsir text from API response
5. **Template Rendering**: Passes data to Jinja2 templates for HTML generation
6. **Error Handling**: Displays appropriate error messages for invalid inputs or API failures

# External Dependencies

## Required Libraries
- **Flask**: Web framework for routing and templating
- **requests**: HTTP library for API calls

## External Services
- **Quran.com API v4**: Primary data source for tafsir content
  - Endpoint: `https://api.quran.com/api/v4/verses/by_key/{sura}:{aya}`
  - Parameters: Arabic language, tafsir translation ID 131
  - Timeout: 10 seconds

## External Resources
- **Google Fonts**: Cairo font family for Arabic text rendering
- **CDN**: Font delivery via Google's CDN

# Deployment Strategy

## Environment Setup
- **Python Version**: 3.x required
- **Dependencies**: Managed via requirements.txt
- **Replit Configuration**: Uses .replit file for environment setup

## File Structure
```
/ (root)
├── .replit              # Replit runtime configuration
├── pyproject.toml       # Python dependencies
├── main.py             # Flask application entry point
├── verses_db.json      # Local Quran verses database (Al-Fatiha)
├── templates/
│   ├── layout.html     # Base template
│   └── index.html      # Enhanced search interface
└── static/
    └── style.css       # Modern responsive CSS styles
```

## Scalability Considerations
- **Stateless Design**: No database or session dependencies
- **API Rate Limiting**: Consider implementing caching for frequently requested verses
- **Performance**: Lightweight CSS and minimal JavaScript for fast loading
- **Error Resilience**: Proper error handling for API unavailability