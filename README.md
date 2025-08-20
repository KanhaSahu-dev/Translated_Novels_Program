# Novel Translation Refiner

A comprehensive web application that extracts machine-translated novel text from websites and transforms it into more natural, human-like translations using advanced NLP techniques.

## 🌟 Features

### 🔍 Text Extraction Module
- Scrape chapters from novelhi.com (specifically Abyss Domination)
- Handle pagination and dynamic content loading
- Support both requests-based and Selenium-based extraction
- Automatic content cleaning and formatting

### 🌐 Translation Refinement Engine
- Advanced NLP processing using spaCy and transformers
- Grammar correction using T5-based models
- Style improvements and naturalness enhancement
- Context-aware corrections across chapters
- Machine translation artifact removal

### 🧠 Glossary & Context Tracker
- Maintain consistent character names, places, and terms
- Track entity variations across chapters
- Context-aware terminology management
- Bulk import/export functionality

### 🖥️ User Interface
- Modern Angular frontend with Material Design
- Side-by-side comparison of original vs refined text
- Manual editing capabilities
- Real-time processing status
- Batch processing support
- Download refined versions

## 🛠️ Tech Stack

### Backend
- **Python 3.8+** with FastAPI
- **NLP Libraries**: spaCy, transformers, NLTK, TextBlob
- **Web Scraping**: BeautifulSoup, Selenium, requests
- **Database**: SQLAlchemy with SQLite
- **API**: RESTful APIs with automatic documentation

### Frontend
- **Angular 20+** with TypeScript
- **UI**: Angular Material + Bootstrap
- **State Management**: RxJS Observables
- **HTTP Client**: Angular HttpClient

## 📋 Prerequisites

- Python 3.8 or higher
- Node.js 18+ and npm
- Chrome browser (for Selenium scraping)

## 🚀 Quick Start

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Download NLP models:**
   ```bash
   python -m spacy download en_core_web_sm
   python -c "import nltk; nltk.download('punkt')"
   ```

5. **Run the backend server:**
   ```bash
   cd app
   python main.py
   ```
   
   The API will be available at `http://localhost:8000`
   API documentation: `http://localhost:8000/docs`

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend/novel-refiner-app
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   ng serve
   ```
   
   The application will be available at `http://localhost:4200`

## 📖 Usage Guide

### 1. Search and Extract Novel
1. Open the application at `http://localhost:4200`
2. Use the search feature to find "Abyss Domination" on novelhi.com
3. Select the novel and configure extraction settings
4. Start the extraction process (runs in background)

### 2. Manage Glossary
1. Navigate to the Glossary Manager
2. Add character names, places, and terminology
3. Set preferred translations for consistency
4. Import/export glossary data

### 3. Refine Chapters
1. Go to the Chapter View
2. Select chapters to process
3. Choose refinement options
4. Review side-by-side comparison
5. Make manual edits if needed
6. Download refined versions

### 4. Batch Processing
1. Select multiple chapters or entire novel
2. Start batch refinement process
3. Monitor progress in real-time
4. Review and download results

## 🔧 Configuration

### Backend Configuration
Edit `backend/app/utils/config.py`:
- Database URL
- API settings
- NLP processing limits
- Scraping parameters

### Frontend Configuration
Edit Angular environment files for:
- API endpoint URLs
- Feature flags
- UI customization

## 📁 Project Structure

```
Transaltion_Novels_Expt/
├── backend/
│   ├── app/
│   │   ├── api/           # API routes
│   │   ├── models/        # Database models
│   │   ├── modules/       # Core processing modules
│   │   ├── utils/         # Utility functions
│   │   └── main.py        # FastAPI application
│   ├── requirements.txt   # Python dependencies
│   └── tests/            # Backend tests
│
├── frontend/
│   └── novel-refiner-app/
│       ├── src/
│       │   ├── app/
│       │   │   ├── components/    # Angular components
│       │   │   ├── services/      # API services
│       │   │   ├── models/        # TypeScript interfaces
│       │   │   └── app.ts         # Main app component
│       │   └── assets/            # Static assets
│       └── package.json           # Node dependencies
│
└── README.md
```

## 🔍 API Endpoints

### Novel Management
- `POST /api/scraper/search` - Search novels
- `POST /api/scraper/extract` - Extract novel chapters
- `GET /api/scraper/novels` - Get all novels
- `GET /api/scraper/novels/{id}` - Get novel by ID
- `GET /api/scraper/chapters/{id}` - Get chapter content

### NLP Processing
- `POST /api/nlp/initialize` - Initialize NLP models
- `POST /api/nlp/refine-text` - Refine text
- `POST /api/nlp/refine-chapter` - Refine chapter
- `POST /api/nlp/batch-refine` - Batch refinement
- `GET /api/nlp/processing-status/{novel_id}` - Processing status

### Glossary Management
- `POST /api/glossary/terms` - Create term
- `GET /api/glossary/terms/{novel_id}` - Get terms
- `PUT /api/glossary/terms/{id}` - Update term
- `DELETE /api/glossary/terms/{id}` - Delete term
- `POST /api/glossary/bulk-import` - Bulk import

## ⚠️ Important Notes

### Legal Considerations
- Ensure you have proper rights to scrape and process content
- This tool is designed for personal, educational, or fair use purposes
- Web scraping may violate website terms of service
- Always respect robots.txt and rate limiting

### Performance Considerations
- NLP processing is computationally intensive
- Large novels may take significant time to process
- Consider using GPU acceleration for transformer models
- Batch processing is more efficient than individual chapters

### Browser Requirements
- Chrome browser required for Selenium-based scraping
- Modern browser with JavaScript enabled for frontend
- Stable internet connection for scraping operations

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is for educational and personal use. Please ensure compliance with all applicable laws and website terms of service.

## 🆘 Support

If you encounter issues:
1. Check the console logs for error messages
2. Verify all dependencies are installed correctly
3. Ensure the backend server is running
4. Check network connectivity for scraping operations

## 🔮 Future Enhancements

- Support for additional novel websites
- More advanced NLP models (GPT-based refinement)
- Multi-language support
- Advanced context analysis
- User preference learning
- Cloud deployment options 