# Scrapsama Web Interface - Features and Screenshots

## Overview

The Scrapsama web interface is a modern, responsive streaming site for browsing and watching anime episodes. It provides a Netflix-like experience with search, browse, and player functionality.

## Features

### 1. Home Page (`/`)

**Features:**
- Large hero section with welcome message
- Real-time search bar with autocomplete
- Grid display of all available anime series
- Responsive card layout with thumbnails
- Category badges for each series

**User Flow:**
1. User lands on home page
2. Can search for anime using the search bar
3. Search results appear in dropdown with thumbnails
4. Can browse all series in grid below
5. Click on any series card to view details

### 2. Search Functionality

**Features:**
- Real-time search as you type (300ms debounce)
- Search by series name
- Results show thumbnail, title, and categories
- Click any result to go to series page
- Dropdown hides when clicking outside

**Technical Implementation:**
- AJAX request to `/search?q=<query>`
- JSON response with series data
- Dynamic HTML generation with JavaScript

### 3. Series Detail Page (`/series/<id>`)

**Features:**
- Large banner image of the series
- Full series information:
  - Title and 18+ badge if mature
  - Categories and genres as badges
  - Synopsis/description
  - Advancement status (ongoing/completed)
  - Available languages
- Grid of all seasons
- Breadcrumb navigation
- Click season to view episodes

**Display Information:**
- Series name
- Image/poster
- Genres (e.g., Action, Comedy, Drama)
- Categories (e.g., Anime, Film)
- Languages (e.g., VOSTFR, VF)
- Synopsis
- Advancement
- Correspondence

### 4. Season Detail Page (`/season/<id>`)

**Features:**
- Breadcrumb navigation (Home > Series > Season)
- Season header with series name
- Available languages display
- Grid of all episodes
- Episode cards showing episode number and name
- Click episode to watch

**Display Information:**
- Season name
- Series name
- List of episodes with numbers
- Available languages for the season

### 5. Episode Player Page (`/episode/<id>`)

**Features:**
- Breadcrumb navigation (Home > Series > Season > Episode)
- Episode title and information
- Language selector dropdown
- Player selector dropdown (multiple players per language)
- Embedded video player (iframe)
- Responsive 16:9 aspect ratio player

**User Controls:**
1. Select language from dropdown
2. Select player/host from dropdown
3. Video loads automatically in iframe
4. Watch episode directly in browser

**Player Information:**
- Player URL embedded in iframe
- Player hostname displayed in dropdown
- Multiple players per language for redundancy
- Player order preserved from database

## Design

### Color Scheme
- Dark theme (Netflix-inspired)
- Primary color: Red (#e50914)
- Background: Dark gray (#1a1a1a, #2d2d2d)
- Text: Light gray (#e0e0e0, #b3b3b3)

### Layout
- Responsive grid system
- Mobile-friendly breakpoints
- Hover effects on cards
- Smooth transitions
- Modern card-based UI

### Typography
- Font family: Segoe UI, sans-serif
- Hierarchical heading sizes
- Readable line height (1.6)

## API Endpoints

### Public Routes
- `GET /` - Home page
- `GET /series/<id>` - Series detail page
- `GET /season/<id>` - Season detail page  
- `GET /episode/<id>` - Episode player page

### API Routes
- `GET /search?q=<query>` - Search for series (returns JSON)
- `GET /api/series` - List all series (returns JSON, max 100)

## Database Integration

The web interface queries the MySQL database for:
- **series table**: Series information, genres, categories
- **seasons table**: Season list for each series
- **episodes table**: Episode list for each season
- **players table**: Player URLs grouped by language

## Technical Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Database**: MySQL
- **Deployment**: Docker container
- **Server**: Built-in Flask development server

## Browser Compatibility

- Modern browsers (Chrome, Firefox, Safari, Edge)
- Responsive design for mobile and tablet
- HTML5 video player support required for iframe embedding

## Security Considerations

- Database credentials from environment variables
- Error handling for database failures
- Input sanitization for search queries
- XSS protection via template escaping
- No authentication required (public access)

## Future Enhancements

Possible improvements:
- User accounts and watch history
- Favorites and watchlist
- Episode progress tracking
- Comments and ratings
- Recommendations
- Advanced filtering (by genre, year, status)
- Pagination for large series lists
- Keyboard shortcuts for player
- Download links
- Multiple language UI
- Dark/light theme toggle
