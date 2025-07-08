#!/usr/bin/env python3
"""
CSV Text Annotation Tool

A web-based interface for annotating text content from CSV files.
Features fault tolerance, progress tracking, and responsive design.
"""

import os
import json
import pandas as pd
import re
import random
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file
from datetime import datetime

app = Flask(__name__)

# Configuration
DATA_DIR = Path("../data")
PROGRESS_FILE = "annotation_progress.json"
RESULTS_DIR = Path("results")
RESULTS_DIR.mkdir(exist_ok=True)

class AnnotationManager:
    """Manages annotation progress and data handling."""
    
    def __init__(self):
        self.current_file = None
        self.current_index = 0
        self.annotations = {}
        self.data = None
        self.phrases = []  # List of extracted phrases with metadata
        self.total_items = 0
        self.csv_files = []
        self.load_progress()
        self.load_csv_files()
    
    def extract_phrases(self, text, article_index, metadata):
        """Extract phrases (sentences) from text content with proper French abbreviation handling."""
        if not text or pd.isna(text):
            return []
        
        text = str(text).strip()
        if not text:
            return []
        
        # Common French abbreviations that shouldn't trigger sentence breaks
        french_abbreviations = {
            r'M\.', r'Mme\.', r'Mlle\.', r'Dr\.', r'Pr\.', r'St\.', r'Ste\.',
            r'etc\.', r'cf\.', r'vs\.', r'p\.', r'pp\.', r'vol\.', r'n°\.', r'art\.',
            r'ch\.', r'sect\.', r'al\.', r'op\.', r'loc\.', r'ibid\.', r'id\.',
            r'Jr\.', r'Sr\.', r'Lt\.', r'Col\.', r'Gen\.', r'Cdt\.', r'Cpt\.',
            r'MM\.', r'Mmes\.', r'Mlles\.', r'Drs\.', r'Prs\.', r'Sts\.', r'Stes\.',
            r'av\.', r'bd\.', r'rue\.', r'pl\.', r'sq\.', r'imp\.', r'all\.',
            r'janv\.', r'févr\.', r'mars\.', r'avr\.', r'mai\.', r'juin\.',
            r'juill\.', r'août\.', r'sept\.', r'oct\.', r'nov\.', r'déc\.'
        }
        
        # Use a simpler but effective approach:
        # 1. Replace periods in abbreviations with a special marker
        # 2. Split on sentence boundaries 
        # 3. Restore the periods in abbreviations
        
        # Replace periods in abbreviations temporarily
        temp_text = text
        abbrev_replacements = {}
        counter = 0
        
        for abbrev in french_abbreviations:
            # Remove the escape backslash for actual matching
            abbrev_clean = abbrev.replace(r'\.', '.')
            if abbrev_clean in temp_text:
                marker = f"__ABBREV_DOT_{counter}__"
                temp_text = temp_text.replace(abbrev_clean, abbrev_clean.replace('.', marker))
                abbrev_replacements[marker] = '.'
                counter += 1
        
        # Now split on sentence boundaries
        sentence_pattern = r'[.!?]+(?=\s+[A-ZÀÂÄÉÈÊËÏÎÔÖÙÛÜŸÇ]|\s*$|\s*["\'\(])'
        sentences = re.split(sentence_pattern, temp_text)
        
        phrases = []
        for sentence_index, sentence in enumerate(sentences):
            sentence = sentence.strip()
            
            # Restore abbreviation periods
            for marker, period in abbrev_replacements.items():
                sentence = sentence.replace(marker, period)
            
            # Clean up the sentence
            sentence = sentence.strip()
            sentence = re.sub(r'\s+', ' ', sentence)  # Normalize whitespace
            
            # Skip very short phrases (less than 15 characters) or empty ones
            # Increased threshold since we want meaningful phrases
            if len(sentence) >= 15:
                phrase_data = {
                    'text': sentence,
                    'article_index': article_index,
                    'sentence_index': sentence_index,
                    'metadata': metadata.copy()
                }
                phrases.append(phrase_data)
        
        return phrases
    
    def load_csv_files(self):
        """Load available CSV files from data directory."""
        try:
            csv_files = list(DATA_DIR.glob("*.csv"))
            self.csv_files = [f.name for f in csv_files if f.stat().st_size > 0]
        except Exception as e:
            print(f"Error loading CSV files: {e}")
            self.csv_files = []
    
    def load_progress(self):
        """Load annotation progress from file."""
        if os.path.exists(PROGRESS_FILE):
            try:
                with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
                    progress = json.load(f)
                    self.current_file = progress.get('current_file')
                    self.current_index = progress.get('current_index', 0)
                    self.total_items = progress.get('total_items', 0)
                    self.annotations = progress.get('annotations', {})
            except Exception as e:
                print(f"Error loading progress: {e}")
                self.reset_progress()
    
    def save_progress(self):
        """Save current annotation progress."""
        progress = {
            'current_file': self.current_file,
            'current_index': self.current_index,
            'total_items': self.total_items,
            'annotations': self.annotations,
            'last_updated': datetime.now().isoformat()
        }
        try:
            with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
                json.dump(progress, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving progress: {e}")
    
    def reset_progress(self):
        """Reset annotation progress."""
        self.current_file = None
        self.current_index = 0
        self.annotations = {}
        self.data = None
        self.phrases = []
        self.total_items = 0
    
    def load_csv_data(self, filename):
        """Load data from selected CSV file, extract and shuffle phrases."""
        try:
            filepath = DATA_DIR / filename
            if not filepath.exists():
                return False, f"File {filename} not found"
            
            # Read CSV with error handling
            self.data = pd.read_csv(filepath, encoding='utf-8')
            
            # Validate required column
            if 'content' not in self.data.columns:
                return False, f"'content' column not found in {filename}"
            
            # Filter out rows with empty content
            self.data = self.data.dropna(subset=['content'])
            self.data = self.data[self.data['content'].str.strip() != '']
            
            # Shuffle articles for randomized processing
            self.data = self.data.sample(frac=1, random_state=42).reset_index(drop=True)
            print(f"Shuffled {len(self.data)} articles")
            
            # Extract phrases from all articles
            self.phrases = []
            for article_index, row in self.data.iterrows():
                metadata = {
                    'headline': row.get('headline', ''),
                    'url': row.get('url', ''),
                    'date_published': row.get('date_published', ''),
                    'article_index': article_index,
                    'original_article_index': row.name if hasattr(row, 'name') else article_index
                }
                
                article_phrases = self.extract_phrases(row['content'], article_index, metadata)
                self.phrases.extend(article_phrases)
            
            # Shuffle phrases for completely randomized annotation order
            random.seed(42)  # Set seed for reproducibility
            random.shuffle(self.phrases)
            print(f"Shuffled {len(self.phrases)} phrases")
            
            # Update phrase indices after shuffling
            for i, phrase in enumerate(self.phrases):
                phrase['shuffled_index'] = i
            
            self.total_items = len(self.phrases)
            
            # Reset index if switching files or if current index is beyond data
            previous_file = self.current_file
            if filename != previous_file or self.current_index >= self.total_items:
                self.current_index = 0
            
            self.current_file = filename
            
            return True, f"Loaded and shuffled {len(self.data)} articles with {self.total_items} phrases from {filename}"
            
        except Exception as e:
            return False, f"Error loading {filename}: {str(e)}"
    
    def get_current_item(self):
        """Get current phrase for annotation."""
        if not self.phrases or self.current_index >= self.total_items:
            return None
        
        phrase = self.phrases[self.current_index]
        shuffled_idx = phrase.get('shuffled_index', self.current_index)
        return {
            'index': self.current_index,
            'total': self.total_items,
            'content': phrase['text'],
            'metadata': {
                'headline': phrase['metadata']['headline'],
                'url': phrase['metadata']['url'],
                'date_published': phrase['metadata']['date_published'],
                'article_index': phrase['metadata']['article_index'],
                'sentence_index': phrase['sentence_index'],
                'shuffled_index': shuffled_idx,
                'phrase_info': f"Phrase {phrase['sentence_index'] + 1} from shuffled article {phrase['metadata']['article_index'] + 1} (randomized order)"
            }
        }
    
    def annotate_current(self, annotation):
        """Annotate current phrase and move to next."""
        if not self.phrases:
            return False, "No phrases loaded"
        
        if self.current_index >= len(self.phrases):
            return False, "No more phrases to annotate"
        
        # Store annotation (1 for yes, 0 for no)
        phrase = self.phrases[self.current_index]
        item_id = f"{self.current_file}_phrase_{self.current_index}"
        self.annotations[item_id] = {
            'annotation': annotation,
            'timestamp': datetime.now().isoformat(),
            'content': phrase['text'],
            'article_index': phrase['metadata']['article_index'],
            'sentence_index': phrase['sentence_index'],
            'shuffled_index': phrase.get('shuffled_index', self.current_index),
            'original_article_index': phrase['metadata'].get('original_article_index', phrase['metadata']['article_index']),
            'metadata': phrase['metadata']
        }
        
        # Move to next phrase
        self.current_index += 1
        self.save_progress()
        
        return True, "Phrase annotation saved"
    
    def get_progress_stats(self):
        """Get annotation progress statistics."""
        if not self.current_file:
            return {
                'current_file': None,
                'progress': 0,
                'completed': 0,
                'total': 0,
                'percentage': 0
            }
        
        # Count phrase annotations for current file
        current_file_annotations = sum(
            1 for key in self.annotations.keys() 
            if key.startswith(f"{self.current_file}_phrase_")
        )
        
        return {
            'current_file': self.current_file,
            'progress': self.current_index,
            'completed': current_file_annotations,
            'total': self.total_items,
            'percentage': round((current_file_annotations / self.total_items * 100), 1) if self.total_items > 0 else 0
        }
    
    def export_annotations(self):
        """Export phrase annotations to CSV file."""
        if not self.annotations:
            return None, "No annotations to export"
        
        # Group phrase annotations by file
        files_data = {}
        for item_id, annotation_data in self.annotations.items():
            if not item_id.endswith('_phrase_' + item_id.split('_phrase_')[-1]):
                continue  # Skip non-phrase annotations
            
            file_name = item_id.split('_phrase_')[0]
            if file_name not in files_data:
                files_data[file_name] = []
            
            files_data[file_name].append({
                'phrase_index': int(item_id.split('_phrase_')[-1]),
                'annotation': annotation_data['annotation'],
                'content': annotation_data['content'],
                'article_index': annotation_data.get('article_index', ''),
                'sentence_index': annotation_data.get('sentence_index', ''),
                'shuffled_index': annotation_data.get('shuffled_index', ''),
                'original_article_index': annotation_data.get('original_article_index', ''),
                'timestamp': annotation_data['timestamp'],
                'metadata': annotation_data.get('metadata', {})
            })
        
        # Export phrase annotations for each file
        exported_files = []
        for file_name, phrase_annotations in files_data.items():
            try:
                # Create DataFrame with phrase annotations
                phrases_df = pd.DataFrame(phrase_annotations)
                phrases_df = phrases_df.sort_values('phrase_index')
                
                # Add source information
                phrases_df['source_file'] = file_name
                phrases_df['headline'] = phrases_df['metadata'].apply(lambda x: x.get('headline', '') if isinstance(x, dict) else '')
                phrases_df['url'] = phrases_df['metadata'].apply(lambda x: x.get('url', '') if isinstance(x, dict) else '')
                phrases_df['date_published'] = phrases_df['metadata'].apply(lambda x: x.get('date_published', '') if isinstance(x, dict) else '')
                
                # Select relevant columns for export
                export_columns = ['phrase_index', 'content', 'annotation', 'shuffled_index', 'article_index', 
                                'sentence_index', 'original_article_index', 'headline', 'url', 'date_published', 
                                'timestamp', 'source_file']
                phrases_df = phrases_df[export_columns]
                
                # Save annotated phrases file
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_filename = f"annotated_phrases_{file_name.replace('.csv', '')}_{timestamp}.csv"
                output_path = RESULTS_DIR / output_filename
                
                phrases_df.to_csv(output_path, index=False, encoding='utf-8')
                exported_files.append(output_filename)
                
            except Exception as e:
                print(f"Error exporting {file_name}: {e}")
        
        return exported_files, f"Exported {len(exported_files)} phrase annotation files"

# Global annotation manager
annotation_manager = AnnotationManager()

@app.route('/')
def index():
    """Main annotation interface."""
    return render_template('index.html')

@app.route('/api/files')
def get_files():
    """Get available CSV files."""
    return jsonify(annotation_manager.csv_files)

@app.route('/api/load_file', methods=['POST'])
def load_file():
    """Load selected CSV file."""
    filename = request.json.get('filename')
    success, message = annotation_manager.load_csv_data(filename)
    return jsonify({'success': success, 'message': message})

@app.route('/api/current_item')
def current_item():
    """Get current item for annotation."""
    item = annotation_manager.get_current_item()
    stats = annotation_manager.get_progress_stats()
    
    return jsonify({
        'item': item,
        'stats': stats,
        'has_data': item is not None
    })

@app.route('/api/annotate', methods=['POST'])
def annotate():
    """Submit annotation for current item."""
    annotation = request.json.get('annotation')  # 1 for yes, 0 for no
    
    if annotation not in [0, 1]:
        return jsonify({'success': False, 'message': 'Invalid annotation value'})
    
    success, message = annotation_manager.annotate_current(annotation)
    return jsonify({'success': success, 'message': message})

@app.route('/api/export')
def export():
    """Export annotations to CSV."""
    files, message = annotation_manager.export_annotations()
    return jsonify({'success': files is not None, 'files': files, 'message': message})

@app.route('/api/reset', methods=['POST'])
def reset():
    """Reset annotation progress."""
    annotation_manager.reset_progress()
    return jsonify({'success': True, 'message': 'Progress reset'})

@app.route('/download/<filename>')
def download_file(filename):
    """Download exported file."""
    file_path = RESULTS_DIR / filename
    if file_path.exists():
        return send_file(file_path, as_attachment=True)
    return "File not found", 404

if __name__ == '__main__':
    print("Starting CSV Annotation Tool...")
    print(f"Available CSV files: {annotation_manager.csv_files}")
    app.run(debug=True, host='0.0.0.0', port=5000) 