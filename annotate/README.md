# 📝 CSV Phrase Annotation Tool

A clean, responsive web-based interface for annotating individual phrases from CSV files. Extracts sentences from articles and displays them prominently for efficient phrase-level annotation with fault tolerance and progress tracking.

## ✨ Features

- **Phrase-Level Annotation**: Automatically extracts and displays individual sentences from articles
- **Randomized Order**: Articles and phrases are shuffled for unbiased annotation (with fixed seed for reproducibility)
- **Prominent Display**: Large, centered phrase presentation for focused annotation
- **Responsive Design**: Clean, modern interface that works on desktop and mobile
- **Fault Tolerance**: Automatic progress saving and recovery from interruptions  
- **Keyboard Shortcuts**: Use arrow keys for fast annotation (← for No, → for Yes)
- **Visual Feedback**: Buttons turn green (Yes) or red (No) with satisfying animations
- **Progress Tracking**: Real-time progress bar and statistics at phrase level
- **Export Results**: Download annotated CSV files with phrase-level annotations and shuffle tracking
- **Multiple Files**: Support for annotating phrases from multiple CSV files
- **Context Display**: Shows source article information and phrase position

## 🚀 Quick Start

### Prerequisites

- Python 3.7 or higher
- CSV files in the `../data` folder with a 'content' column

### Installation

1. **Navigate to the annotate folder:**
   ```bash
   cd annotate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python app.py
   ```

4. **Open your browser:**
   Navigate to `http://localhost:5000`

## 📖 Usage Guide

### Getting Started

1. **Select a CSV File**: Choose from available CSV files in your data folder
2. **Start Annotating Phrases**: Read each extracted phrase and decide Yes (1) or No (0)
3. **Use Shortcuts**: Press → for Yes, ← for No, or click the buttons
4. **Track Progress**: Monitor your phrase annotation progress with the real-time progress bar
5. **Export Results**: Download your phrase-level annotations when complete

### Keyboard Shortcuts

- **→ (Right Arrow)**: Annotate as "Yes" (1)
- **← (Left Arrow)**: Annotate as "No" (0)  
- **Escape**: Return to file selection

### Visual Feedback

- **Green Button**: Confirmation when you select "Yes"
- **Red Button**: Confirmation when you select "No"
- **Progress Bar**: Shows completion percentage in real-time
- **Status Messages**: Success, error, and info notifications

### Fault Tolerance

The tool automatically saves your progress:
- **Auto-save**: Every annotation is immediately saved
- **Resume**: Restart from your last annotation point
- **Recovery**: Handles interruptions gracefully
- **Reset Option**: Clear all progress if needed

## 📁 File Structure

```
annotate/
├── app.py                 # Flask backend application
├── requirements.txt       # Python dependencies
├── README.md             # This documentation
├── templates/
│   └── index.html        # Main web interface
├── static/
│   ├── style.css         # Responsive styling
│   └── script.js         # Interactive functionality
├── results/              # Exported annotation files
└── annotation_progress.json  # Progress tracking (auto-generated)
```

## 🔧 Configuration

### CSV Requirements

Your CSV files must have:
- A `content` column with text to annotate
- Located in the `../data` folder relative to the annotate directory

### Optional Columns

The tool will display additional metadata if available:
- `headline`: Article or content headline
- `url`: Source URL (displayed as clickable link)
- `date_published`: Publication date

### Output Format

Exported CSV files include phrase-level annotations with:
- `phrase_index`: Sequential index of the phrase in annotation order
- `content`: The actual phrase text that was annotated
- `annotation`: Annotation value (1 for "Yes", 0 for "No")
- `shuffled_index`: Index after shuffling (for tracking randomization)
- `article_index`: Index of the source article (after article shuffling)
- `sentence_index`: Position of phrase within the article
- `original_article_index`: Original article index before shuffling
- `headline`: Source article headline
- `url`: Source article URL
- `date_published`: Publication date
- `timestamp`: When the annotation was made
- `source_file`: Original CSV filename

## 🛠️ Advanced Usage

### Multiple Files

- Annotate multiple CSV files in sequence
- Progress is tracked separately for each file
- Export results for individual files or all at once

### Progress Management

- **View Progress**: Real-time statistics and completion percentage
- **Resume Work**: Automatic resume from last annotation point
- **Reset Progress**: Clear all annotations and start fresh (with confirmation)

### Export Options

- **Individual Files**: Export annotations for specific files
- **Timestamped**: Files include timestamp for version control
- **Download Links**: Direct download from the web interface

## 🎯 Best Practices

1. **Regular Exports**: Export your progress periodically as backup
2. **Consistent Environment**: Use the same browser for consistent experience
3. **Keyboard Shortcuts**: Use arrow keys for faster annotation workflows
4. **Break Sessions**: Take breaks during long annotation sessions
5. **Verify Data**: Check a few exported annotations to ensure accuracy

## 🔍 Troubleshooting

### Common Issues

**CSV files not appearing:**
- Ensure files are in the `../data` folder
- Check that files have a 'content' column
- Verify files are not empty

**Progress not saving:**
- Check write permissions in the annotate folder
- Ensure sufficient disk space
- Restart the application if needed

**Application not starting:**
- Verify Python 3.7+ is installed
- Install all requirements: `pip install -r requirements.txt`
- Check port 5000 is not in use

### Error Recovery

If you encounter issues:
1. Check the console output for error messages
2. Refresh the browser page
3. Restart the Flask application
4. Check file permissions and disk space

## 📊 Data Privacy

- All processing happens locally on your machine
- No data is sent to external servers
- Progress files are stored locally
- You control all data and exports

## 🤝 Contributing

This tool is designed to be simple and focused. For enhancements:
1. Test thoroughly with your specific CSV formats
2. Ensure backward compatibility with existing progress files
3. Maintain the clean, responsive design principles

## 📝 License

This project is open source. See the parent directory for license information.

---

**Happy Annotating!** 🎉

For questions or issues, check the console output or restart the application. 