#!/usr/bin/env python
"""
PDF Annotation GUI for PAGASA Typhoon Bulletins

A GUI tool for annotating PDFs with extracted JSON data from typhoon bulletins.
Uses TyphoonBulletinExtractor to automatically extract data and allows manual editing
before saving annotations.

Features:
- Split view: PDF viewer (left) and JSON editor (right)
- Automatic PDF discovery from dataset/pdfs/
- Automatic extraction using TyphoonBulletinExtractor
- Editable JSON with validation
- Navigation: Previous, Next, Save & Next
- Progress tracking
- Error handling and user feedback

Usage:
    python pdf_annotation_gui.py

Requirements:
    - Python 3.8+
    - tkinter (standard library)
    - pypdfium2 (for PDF rendering)
    - typhoon_extraction_ml.py (for extraction logic)
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import threading
from pathlib import Path
from typing import List, Optional, Dict
import pypdfium2 as pdfium
from PIL import Image, ImageTk
import sys
import traceback

# Import the extraction logic
try:
    from typhoon_extraction_ml import TyphoonBulletinExtractor
except ImportError as e:
    print(f"Error: Cannot import TyphoonBulletinExtractor: {e}")
    print("Make sure typhoon_extraction_ml.py is in the same directory.")
    sys.exit(1)


class PDFViewer(tk.Frame):
    """PDF viewer widget using pypdfium2 for rendering"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.current_pdf = None
        self.current_page = 0
        self.total_pages = 0
        
        # Create canvas for PDF display with scrollbar
        self.canvas_frame = tk.Frame(self)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.scrollbar_y = tk.Scrollbar(self.canvas_frame, orient=tk.VERTICAL)
        self.scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.scrollbar_x = tk.Scrollbar(self.canvas_frame, orient=tk.HORIZONTAL)
        self.scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.canvas = tk.Canvas(
            self.canvas_frame,
            bg='gray',
            xscrollcommand=self.scrollbar_x.set,
            yscrollcommand=self.scrollbar_y.set
        )
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.scrollbar_x.config(command=self.canvas.xview)
        self.scrollbar_y.config(command=self.canvas.yview)
        
        # Page navigation
        nav_frame = tk.Frame(self)
        nav_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
        
        self.page_label = tk.Label(nav_frame, text="Page 0 of 0")
        self.page_label.pack(side=tk.LEFT, padx=5)
        
        tk.Button(nav_frame, text="◀ Prev Page", command=self.prev_page).pack(side=tk.LEFT, padx=2)
        tk.Button(nav_frame, text="Next Page ▶", command=self.next_page).pack(side=tk.LEFT, padx=2)
    
    def load_pdf(self, pdf_path: str):
        """Load a PDF file and display the first page"""
        try:
            # Close previous PDF if any
            if self.current_pdf:
                self.current_pdf.close()
            
            # Open new PDF
            self.current_pdf = pdfium.PdfDocument(pdf_path)
            self.total_pages = len(self.current_pdf)
            self.current_page = 0
            
            self.render_page()
            
        except Exception as e:
            messagebox.showerror("PDF Load Error", f"Failed to load PDF:\n{e}")
            self.current_pdf = None
            self.total_pages = 0
            self.current_page = 0
    
    def render_page(self):
        """Render the current page to canvas"""
        if not self.current_pdf or self.total_pages == 0:
            self.canvas.delete("all")
            self.page_label.config(text="Page 0 of 0")
            return
        
        try:
            # Get the page
            page = self.current_pdf[self.current_page]
            
            # Render at reasonable resolution (scale factor 2 = 144 DPI)
            pil_image = page.render(scale=2).to_pil()
            
            # Convert to PhotoImage
            self.photo = ImageTk.PhotoImage(pil_image)
            
            # Clear canvas and display
            self.canvas.delete("all")
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
            
            # Update scroll region
            self.canvas.config(scrollregion=self.canvas.bbox("all"))
            
            # Update page label
            self.page_label.config(text=f"Page {self.current_page + 1} of {self.total_pages}")
            
        except Exception as e:
            messagebox.showerror("Render Error", f"Failed to render page:\n{e}")
    
    def next_page(self):
        """Go to next page"""
        if self.current_pdf and self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.render_page()
    
    def prev_page(self):
        """Go to previous page"""
        if self.current_pdf and self.current_page > 0:
            self.current_page -= 1
            self.render_page()
    
    def close(self):
        """Clean up resources"""
        if self.current_pdf:
            self.current_pdf.close()
            self.current_pdf = None


class JSONEditor(tk.Frame):
    """JSON editor widget with syntax validation"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        # Title
        title_label = tk.Label(self, text="Extracted JSON (Editable)", font=("Arial", 10, "bold"))
        title_label.pack(side=tk.TOP, pady=(5, 2))
        
        # Text widget with scrollbar
        self.text_widget = scrolledtext.ScrolledText(
            self,
            wrap=tk.NONE,
            font=("Courier", 9),
            undo=True,
            maxundo=-1
        )
        self.text_widget.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Status label
        self.status_label = tk.Label(self, text="", fg="green")
        self.status_label.pack(side=tk.BOTTOM, pady=2)
    
    def set_json(self, data: Dict):
        """Set JSON data in the editor"""
        try:
            json_str = json.dumps(data, indent=2, ensure_ascii=False)
            self.text_widget.delete(1.0, tk.END)
            self.text_widget.insert(1.0, json_str)
            self.status_label.config(text="✓ Valid JSON", fg="green")
        except Exception as e:
            self.status_label.config(text=f"✗ Error: {e}", fg="red")
    
    def get_json(self) -> Optional[Dict]:
        """Get JSON data from editor with validation"""
        try:
            json_str = self.text_widget.get(1.0, tk.END).strip()
            if not json_str:
                return None
            data = json.loads(json_str)
            self.status_label.config(text="✓ Valid JSON", fg="green")
            return data
        except json.JSONDecodeError as e:
            self.status_label.config(text=f"✗ Invalid JSON: {e}", fg="red")
            return None
        except Exception as e:
            self.status_label.config(text=f"✗ Error: {e}", fg="red")
            return None
    
    def clear(self):
        """Clear the editor"""
        self.text_widget.delete(1.0, tk.END)
        self.status_label.config(text="", fg="black")


class PDFAnnotationApp:
    """Main application window"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("PAGASA PDF Annotation Tool")
        self.root.geometry("1400x900")
        
        # State
        self.pdf_files: List[Path] = []
        self.current_index = 0
        self.extractor = None
        self.is_processing = False
        
        # Setup UI
        self.setup_ui()
        
        # Initialize extractor in background
        self.init_extractor()
        
        # Load PDFs
        self.load_pdf_list()
    
    def setup_ui(self):
        """Create the user interface"""
        
        # Top bar with title and file counter
        top_frame = tk.Frame(self.root, bg="#2c3e50", height=40)
        top_frame.pack(side=tk.TOP, fill=tk.X)
        top_frame.pack_propagate(False)
        
        title_label = tk.Label(
            top_frame,
            text="📄 PAGASA PDF Annotation Tool",
            font=("Arial", 14, "bold"),
            fg="white",
            bg="#2c3e50"
        )
        title_label.pack(side=tk.LEFT, padx=20, pady=5)
        
        self.file_counter_label = tk.Label(
            top_frame,
            text="File 0 of 0",
            font=("Arial", 12),
            fg="white",
            bg="#2c3e50"
        )
        self.file_counter_label.pack(side=tk.RIGHT, padx=20, pady=5)
        
        # Main content area with split view
        content_frame = tk.Frame(self.root)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Use PanedWindow for resizable split view
        paned_window = tk.PanedWindow(content_frame, orient=tk.HORIZONTAL, sashrelief=tk.RAISED)
        paned_window.pack(fill=tk.BOTH, expand=True)
        
        # Left panel: PDF viewer
        left_frame = tk.Frame(paned_window, relief=tk.SUNKEN, borderwidth=1)
        self.pdf_viewer = PDFViewer(left_frame)
        self.pdf_viewer.pack(fill=tk.BOTH, expand=True)
        paned_window.add(left_frame, minsize=400)
        
        # Right panel: JSON editor
        right_frame = tk.Frame(paned_window, relief=tk.SUNKEN, borderwidth=1)
        self.json_editor = JSONEditor(right_frame)
        self.json_editor.pack(fill=tk.BOTH, expand=True)
        paned_window.add(right_frame, minsize=400)
        
        # Bottom bar with navigation buttons
        bottom_frame = tk.Frame(self.root, bg="#ecf0f1", height=60)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)
        bottom_frame.pack_propagate(False)
        
        # Progress bar
        self.progress_label = tk.Label(
            bottom_frame,
            text="Ready",
            font=("Arial", 9),
            bg="#ecf0f1"
        )
        self.progress_label.pack(side=tk.TOP, pady=(5, 0))
        
        self.progress_bar = ttk.Progressbar(
            bottom_frame,
            mode='indeterminate',
            length=200
        )
        
        # Navigation buttons
        button_frame = tk.Frame(bottom_frame, bg="#ecf0f1")
        button_frame.pack(side=tk.BOTTOM, pady=10)
        
        self.prev_button = tk.Button(
            button_frame,
            text="◀ Previous",
            command=self.prev_file,
            width=12,
            font=("Arial", 10)
        )
        self.prev_button.pack(side=tk.LEFT, padx=5)
        
        self.save_next_button = tk.Button(
            button_frame,
            text="💾 Save & Next",
            command=self.save_and_next,
            width=15,
            font=("Arial", 10, "bold"),
            bg="#3498db",
            fg="white"
        )
        self.save_next_button.pack(side=tk.LEFT, padx=5)
        
        self.next_button = tk.Button(
            button_frame,
            text="Next ▶",
            command=self.next_file,
            width=12,
            font=("Arial", 10)
        )
        self.next_button.pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="🔄 Re-analyze",
            command=self.reanalyze_current,
            width=12,
            font=("Arial", 10)
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="❌ Quit",
            command=self.quit_app,
            width=10,
            font=("Arial", 10)
        ).pack(side=tk.LEFT, padx=20)
    
    def init_extractor(self):
        """Initialize the TyphoonBulletinExtractor in background"""
        def init_task():
            try:
                self.update_progress("Initializing extractor...")
                self.extractor = TyphoonBulletinExtractor()
                self.update_progress("Extractor ready", hide_after=2)
            except Exception as e:
                self.update_progress(f"Extractor init failed: {e}", hide_after=5)
                messagebox.showerror("Initialization Error", 
                                   f"Failed to initialize extractor:\n{e}\n\nSome features may not work.")
        
        threading.Thread(target=init_task, daemon=True).start()
    
    def load_pdf_list(self):
        """Find all PDFs in dataset/pdfs/ directory"""
        try:
            pdf_dir = Path("dataset/pdfs")
            if not pdf_dir.exists():
                messagebox.showwarning(
                    "Directory Not Found",
                    f"PDF directory not found: {pdf_dir}\n\nPlease create it and add PDFs."
                )
                return
            
            # Find all PDFs recursively
            self.pdf_files = sorted(list(pdf_dir.rglob("*.pdf")))
            
            if not self.pdf_files:
                messagebox.showinfo(
                    "No PDFs Found",
                    f"No PDF files found in {pdf_dir}\n\nPlease add PDFs to annotate."
                )
                return
            
            # Load first PDF
            self.current_index = 0
            self.load_current_pdf()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load PDF list:\n{e}")
    
    def load_current_pdf(self):
        """Load and analyze the current PDF"""
        if not self.pdf_files:
            return
        
        if self.is_processing:
            messagebox.showinfo("Processing", "Please wait for current operation to complete.")
            return
        
        try:
            current_file = self.pdf_files[self.current_index]
            
            # Update UI
            self.update_file_counter()
            self.pdf_viewer.load_pdf(str(current_file))
            
            # Check if annotation already exists
            annotation_path = self.get_annotation_path(current_file)
            if annotation_path.exists():
                # Load existing annotation
                with open(annotation_path, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
                self.json_editor.set_json(existing_data)
                self.update_progress(f"Loaded existing annotation", hide_after=3)
            else:
                # Analyze in background
                self.analyze_pdf_async(current_file)
        
        except Exception as e:
            messagebox.showerror("Load Error", f"Failed to load PDF:\n{e}\n\n{traceback.format_exc()}")
    
    def analyze_pdf_async(self, pdf_path: Path):
        """Analyze PDF in background thread"""
        if not self.extractor:
            self.json_editor.set_json({"error": "Extractor not initialized"})
            return
        
        def analyze_task():
            try:
                self.is_processing = True
                self.update_progress(f"Analyzing {pdf_path.name}...")
                self.toggle_buttons(False)
                
                # Extract data
                data = self.extractor.extract_from_pdf(str(pdf_path))
                
                # Update UI in main thread
                self.root.after(0, lambda: self.on_analysis_complete(data))
                
            except Exception as e:
                error_data = {
                    "error": f"Extraction failed: {e}",
                    "traceback": traceback.format_exc()
                }
                self.root.after(0, lambda: self.on_analysis_complete(error_data))
            finally:
                self.is_processing = False
                self.root.after(0, lambda: self.toggle_buttons(True))
        
        threading.Thread(target=analyze_task, daemon=True).start()
    
    def on_analysis_complete(self, data: Dict):
        """Handle completed analysis"""
        if data:
            self.json_editor.set_json(data)
            if "error" in data:
                self.update_progress(f"Extraction failed", hide_after=5)
            else:
                self.update_progress(f"Extraction complete", hide_after=3)
        else:
            self.json_editor.set_json({"error": "No data extracted"})
            self.update_progress(f"No data extracted", hide_after=5)
    
    def reanalyze_current(self):
        """Re-analyze the current PDF"""
        if not self.pdf_files:
            return
        
        if self.is_processing:
            messagebox.showinfo("Processing", "Please wait for current operation to complete.")
            return
        
        if messagebox.askyesno("Re-analyze", "Re-analyze this PDF? Current edits will be lost."):
            current_file = self.pdf_files[self.current_index]
            self.json_editor.clear()
            self.analyze_pdf_async(current_file)
    
    def get_annotation_path(self, pdf_path: Path) -> Path:
        """Get the annotation file path for a PDF"""
        # Get relative path from dataset/pdfs/
        pdf_dir = Path("dataset/pdfs")
        relative_path = pdf_path.relative_to(pdf_dir)
        
        # Create annotation path
        annotation_dir = Path("dataset/pdfs_annotation") / relative_path.parent
        annotation_path = annotation_dir / f"{pdf_path.stem}.json"
        
        return annotation_path
    
    def save_current_annotation(self) -> bool:
        """Save the current annotation"""
        if not self.pdf_files:
            return False
        
        try:
            # Get and validate JSON
            json_data = self.json_editor.get_json()
            if json_data is None:
                messagebox.showerror("Invalid JSON", "Cannot save invalid JSON. Please fix errors first.")
                return False
            
            # Get annotation path
            current_file = self.pdf_files[self.current_index]
            annotation_path = self.get_annotation_path(current_file)
            
            # Create directory if needed
            annotation_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save JSON
            with open(annotation_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)
            
            self.update_progress(f"Saved: {annotation_path.name}", hide_after=3)
            return True
            
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save annotation:\n{e}")
            return False
    
    def prev_file(self):
        """Go to previous PDF"""
        if not self.pdf_files:
            return
        
        if self.is_processing:
            messagebox.showinfo("Processing", "Please wait for current operation to complete.")
            return
        
        if self.current_index > 0:
            self.current_index -= 1
            self.load_current_pdf()
        else:
            messagebox.showinfo("First File", "Already at the first file.")
    
    def next_file(self):
        """Go to next PDF"""
        if not self.pdf_files:
            return
        
        if self.is_processing:
            messagebox.showinfo("Processing", "Please wait for current operation to complete.")
            return
        
        if self.current_index < len(self.pdf_files) - 1:
            self.current_index += 1
            self.load_current_pdf()
        else:
            messagebox.showinfo("Last File", "Already at the last file.")
    
    def save_and_next(self):
        """Save current annotation and move to next"""
        if not self.pdf_files:
            return
        
        if self.is_processing:
            messagebox.showinfo("Processing", "Please wait for current operation to complete.")
            return
        
        # Save current
        if self.save_current_annotation():
            # Move to next
            if self.current_index < len(self.pdf_files) - 1:
                self.current_index += 1
                self.load_current_pdf()
            else:
                messagebox.showinfo("Complete", "All files processed!")
    
    def update_file_counter(self):
        """Update the file counter label"""
        if self.pdf_files:
            current_file = self.pdf_files[self.current_index]
            text = f"File {self.current_index + 1} of {len(self.pdf_files)}: {current_file.name}"
        else:
            text = "No files loaded"
        
        self.file_counter_label.config(text=text)
    
    def update_progress(self, message: str, hide_after: int = 0):
        """Update progress message"""
        self.progress_label.config(text=message)
        
        if hide_after > 0:
            self.root.after(hide_after * 1000, lambda: self.progress_label.config(text="Ready"))
    
    def toggle_buttons(self, enabled: bool):
        """Enable/disable navigation buttons"""
        state = tk.NORMAL if enabled else tk.DISABLED
        self.prev_button.config(state=state)
        self.next_button.config(state=state)
        self.save_next_button.config(state=state)
        
        # Show/hide progress bar
        if enabled:
            self.progress_bar.pack_forget()
            self.progress_bar.stop()
        else:
            self.progress_bar.pack(side=tk.TOP, pady=2)
            self.progress_bar.start(10)
    
    def quit_app(self):
        """Quit the application"""
        if self.is_processing:
            messagebox.showinfo("Processing", "Please wait for current operation to complete.")
            return
        
        if messagebox.askyesno("Quit", "Are you sure you want to quit?"):
            # Clean up
            self.pdf_viewer.close()
            self.root.quit()
            self.root.destroy()


def main():
    """Main entry point"""
    try:
        # Create root window
        root = tk.Tk()
        
        # Create app
        app = PDFAnnotationApp(root)
        
        # Run
        root.mainloop()
        
    except Exception as e:
        print(f"Fatal error: {e}")
        traceback.print_exc()
        messagebox.showerror("Fatal Error", f"Application crashed:\n{e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
