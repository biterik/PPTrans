"""
Main GUI window for PPTrans application
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
from pathlib import Path
from typing import Optional, Callable

from utils.logger import LoggerMixin
from utils.config import Config
from utils.exceptions import create_user_friendly_message
from core.translator import PPTransTranslator
from core.pptx_processor import PPTXProcessor
from core.language_manager import LanguageManager
from .widgets import ProgressDialog, AboutDialog
from .dialogs import SettingsDialog

class PPTransMainWindow(LoggerMixin):
    """Main application window"""
    
    def __init__(self):
        """Initialize the main window"""
        self.config = Config()
        self.translator = PPTransTranslator(self.config.get_translation_settings())
        self.processor = PPTXProcessor(self.config.get_section("advanced"))
        self.language_manager = LanguageManager()
        
        # GUI state
        self.root = None
        self.current_file = None
        self.is_processing = False
        self.progress_dialog = None
        
        self.logger.info("Main window initialized")
        
        self._create_window()
        self._create_widgets()
        self._setup_bindings()
        self._load_window_state()
    
    def _create_window(self):
        """Create the main application window"""
        self.root = tk.Tk()
        self.root.title("PPTrans - PowerPoint Translation Tool")
        
        # Set window size and position
        window_width, window_height = self.config.get_window_size()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.minsize(600, 400)
        
        # Set icon if available
        icon_path = Path(__file__).parent.parent.parent / "assets" / "icon.png"
        if icon_path.exists():
            try:
                self.root.iconphoto(False, tk.PhotoImage(file=str(icon_path)))
            except Exception as e:
                self.logger.debug(f"Could not load icon: {e}")
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')  # Use a modern theme
    
    def _create_widgets(self):
        """Create all GUI widgets"""
        self._create_menu_bar()
        self._create_main_frame()
        self._create_file_selection_frame()
        self._create_options_frame()
        self._create_language_frame()
        self._create_action_frame()
        self._create_status_frame()
    
    def _create_menu_bar(self):
        """Create the menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open PPTX...", command=self._select_file, accelerator="Ctrl+O")
        file_menu.add_separator()
        file_menu.add_command(label="Settings...", command=self._show_settings)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._on_exit, accelerator="Ctrl+Q")
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Test Connection", command=self._test_connection)
        tools_menu.add_command(label="Clear Log", command=self._clear_log)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_about)
        help_menu.add_command(label="Documentation", command=self._show_documentation)
    
    def _create_main_frame(self):
        """Create the main content frame"""
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
    
    def _create_file_selection_frame(self):
        """Create file selection frame"""
        file_frame = ttk.LabelFrame(self.main_frame, text="PowerPoint File", padding="5")
        file_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        file_frame.columnconfigure(1, weight=1)
        
        ttk.Label(file_frame, text="File:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        
        self.file_var = tk.StringVar()
        self.file_entry = ttk.Entry(file_frame, textvariable=self.file_var, state="readonly")
        self.file_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        
        self.browse_button = ttk.Button(file_frame, text="Browse...", command=self._select_file)
        self.browse_button.grid(row=0, column=2, sticky=tk.E)
        
        # File info label
        self.file_info_var = tk.StringVar()
        self.file_info_label = ttk.Label(file_frame, textvariable=self.file_info_var, 
                                        foreground="gray", font=("TkDefaultFont", 8))
        self.file_info_label.grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=(5, 0))
    
    def _create_options_frame(self):
        """Create options frame"""
        options_frame = ttk.LabelFrame(self.main_frame, text="Options", padding="5")
        options_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        options_frame.columnconfigure(1, weight=1)
        
        ttk.Label(options_frame, text="Slide Range:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        
        self.slide_range_var = tk.StringVar(value="all")
        slide_range_frame = ttk.Frame(options_frame)
        slide_range_frame.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        self.slide_range_entry = ttk.Entry(slide_range_frame, textvariable=self.slide_range_var, width=20)
        self.slide_range_entry.pack(side=tk.LEFT)
        
        ttk.Label(slide_range_frame, text="(e.g., 'all', '1-5', '1,3,7')", 
                 foreground="gray", font=("TkDefaultFont", 8)).pack(side=tk.LEFT, padx=(5, 0))
    
    def _create_language_frame(self):
        """Create language selection frame"""
        lang_frame = ttk.LabelFrame(self.main_frame, text="Languages", padding="5")
        lang_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        lang_frame.columnconfigure(1, weight=1)
        lang_frame.columnconfigure(3, weight=1)
        
        # Source language
        ttk.Label(lang_frame, text="From:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        
        self.source_lang_var = tk.StringVar()
        self.source_lang_combo = ttk.Combobox(lang_frame, textvariable=self.source_lang_var, 
                                             state="readonly", width=25)
        self.source_lang_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # Target language
        ttk.Label(lang_frame, text="To:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        
        self.target_lang_var = tk.StringVar()
        self.target_lang_combo = ttk.Combobox(lang_frame, textvariable=self.target_lang_var, 
                                             state="readonly", width=25)
        self.target_lang_combo.grid(row=0, column=3, sticky=(tk.W, tk.E))
        
        # Populate language dropdowns
        self._populate_language_combos()
    
    def _create_action_frame(self):
        """Create action buttons frame"""
        action_frame = ttk.Frame(self.main_frame)
        action_frame.grid(row=3, column=0, columnspan=2, pady=(0, 10))
        
        self.translate_button = ttk.Button(action_frame, text="Translate", 
                                          command=self._start_translation, style="Accent.TButton")
        self.translate_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.cancel_button = ttk.Button(action_frame, text="Cancel", 
                                       command=self._cancel_translation, state="disabled")
        self.cancel_button.pack(side=tk.LEFT)
        
        # Configure accent button style
        style = ttk.Style()
        style.configure("Accent.TButton", foreground="white", background="#0078d4")
    
    def _create_status_frame(self):
        """Create status and log frame"""
        status_frame = ttk.LabelFrame(self.main_frame, text="Status", padding="5")
        status_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 0))
        status_frame.columnconfigure(0, weight=1)
        status_frame.rowconfigure(1, weight=1)
        self.main_frame.rowconfigure(4, weight=1)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(status_frame, textvariable=self.status_var)
        status_label.grid(row=0, column=0, sticky=tk.W)
        
        # Log text area
        log_frame = ttk.Frame(status_frame)
        log_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(5, 0))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = tk.Text(log_frame, height=8, wrap=tk.WORD, state="disabled")
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        log_scroll = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        log_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.log_text.configure(yscrollcommand=log_scroll.set)
    
    def _populate_language_combos(self):
        """Populate language combo boxes"""
        # Get languages with popular ones first
        languages = self.language_manager.get_language_list(popular_first=True)
        language_names = [f"{name} ({code})" for code, name in languages]
        
        # Source languages (include auto-detect)
        self.source_lang_combo['values'] = language_names
        
        # Target languages (exclude auto-detect)
        target_languages = self.language_manager.get_language_list(include_auto_detect=False, popular_first=True)
        target_names = [f"{name} ({code})" for code, name in target_languages]
        self.target_lang_combo['values'] = target_names
        
        # Set default values
        default_source = self.config.get("translation.default_source_language", "auto")
        default_target = self.config.get("translation.default_target_language", "en")
        
        self._set_language_combo_value(self.source_lang_combo, self.source_lang_var, default_source)
        self._set_language_combo_value(self.target_lang_combo, self.target_lang_var, default_target)
    
    def _set_language_combo_value(self, combo: ttk.Combobox, var: tk.StringVar, lang_code: str):
        """Set combo box value by language code"""
        try:
            lang_name = self.language_manager.get_language_name(lang_code)
            value = f"{lang_name} ({lang_code})"
            var.set(value)
        except Exception:
            # Fallback to first item if language not found
            if combo['values']:
                var.set(combo['values'][0])
    
    def _get_language_code_from_combo(self, combo_value: str) -> str:
        """Extract language code from combo box value"""
        # Extract code from format "Language Name (code)"
        if '(' in combo_value and ')' in combo_value:
            return combo_value.split('(')[-1].rstrip(')')
        return combo_value
    
    def _setup_bindings(self):
        """Setup keyboard bindings and events"""
        self.root.bind('<Control-o>', lambda e: self._select_file())
        self.root.bind('<Control-q>', lambda e: self._on_exit())
        self.root.protocol("WM_DELETE_WINDOW", self._on_exit)
        
        # File selection binding
        self.file_var.trace('w', self._on_file_changed)
    
    def _select_file(self):
        """Open file selection dialog"""
        initial_dir = self.config.get("gui.last_directory", os.path.expanduser("~"))
        
        filename = filedialog.askopenfilename(
            title="Select PowerPoint File",
            initialdir=initial_dir,
            filetypes=[
                ("PowerPoint files", "*.pptx"),
                ("All files", "*.*")
            ]
        )
        
        if filename:
            self.file_var.set(filename)
            self.current_file = filename
            
            # Remember directory
            if self.config.get("gui.remember_last_directory", True):
                self.config.set("gui.last_directory", os.path.dirname(filename))
            
            self._update_file_info()
            self.log_message(f"Selected file: {os.path.basename(filename)}")
    
    def _on_file_changed(self, *args):
        """Handle file selection change"""
        file_path = self.file_var.get()
        has_file = bool(file_path and os.path.exists(file_path))
        
        # Enable/disable translate button
        self.translate_button.config(state="normal" if has_file else "disabled")
        
        if has_file:
            self.status_var.set("File loaded - Ready to translate")
        else:
            self.status_var.set("Select a PowerPoint file to begin")
    
    def _update_file_info(self):
        """Update file information display"""
        if not self.current_file or not os.path.exists(self.current_file):
            self.file_info_var.set("")
            return
        
        try:
            # Load presentation to get info
            processor = PPTXProcessor()
            processor.load_presentation(self.current_file)
            info = processor.get_presentation_info()
            
            info_text = f"Slides: {info.get('total_slides', 0)}"
            file_size = os.path.getsize(self.current_file) / (1024 * 1024)  # MB
            info_text += f" | Size: {file_size:.1f} MB"
            
            self.file_info_var.set(info_text)
            
        except Exception as e:
            self.logger.warning(f"Could not read file info: {e}")
            self.file_info_var.set("File information unavailable")
    
    def _start_translation(self):
        """Start the translation process"""
        if self.is_processing:
            return
        
        # Validate inputs
        if not self.current_file or not os.path.exists(self.current_file):
            messagebox.showerror("Error", "Please select a valid PowerPoint file.")
            return
        
        slide_range = self.slide_range_var.get().strip()
        if not slide_range:
            slide_range = "all"
        
        source_lang = self._get_language_code_from_combo(self.source_lang_var.get())
        target_lang = self._get_language_code_from_combo(self.target_lang_var.get())
        
        if not source_lang or not target_lang:
            messagebox.showerror("Error", "Please select both source and target languages.")
            return
        
        # Start translation in background thread
        self.is_processing = True
        self._update_ui_state()
        
        translation_thread = threading.Thread(
            target=self._perform_translation,
            args=(self.current_file, slide_range, source_lang, target_lang),
            daemon=True
        )
        translation_thread.start()
    
    def _perform_translation(self, file_path: str, slide_range: str, source_lang: str, target_lang: str):
        """Perform translation in background thread"""
        try:
            self.log_message("Starting translation process...")
            self.status_var.set("Loading presentation...")
            
            # Load presentation
            self.processor.load_presentation(file_path)
            
            # Extract text elements
            self.status_var.set("Extracting text elements...")
            text_elements = self.processor.extract_text_elements(slide_range)
            
            if not text_elements:
                self.log_message("No text elements found to translate.")
                return
            
            self.log_message(f"Found {len(text_elements)} text elements to translate")
            
            # Create progress dialog
            self.root.after(0, self._create_progress_dialog, len(text_elements))
            
            # Translation function with progress updates
            def translate_with_progress(text: str) -> str:
                translated = self.translator.translate_text(text, source_lang, target_lang)
                if self.progress_dialog:
                    self.progress_dialog.increment()
                return translated
            
            # Perform translations
            self.status_var.set("Translating text...")
            self.processor.translate_text_elements(translate_with_progress)
            
            # Apply translations
            self.status_var.set("Applying translations...")
            self.processor.apply_translations()
            
            # Save translated presentation
            self.status_var.set("Saving presentation...")
            output_path = self.processor.save_presentation()
            
            # Show completion message
            stats = self.processor.get_processing_stats()
            message = (f"Translation completed successfully!\n\n"
                      f"Translated: {stats['translated_elements']} text elements\n"
                      f"Processed: {stats['processed_slides']} slides\n"
                      f"Output file: {os.path.basename(output_path)}")
            
            self.root.after(0, lambda: messagebox.showinfo("Success", message))
            self.log_message(f"Translation completed: {output_path}")
            
        except Exception as e:
            error_msg = create_user_friendly_message(e)
            self.logger.error(f"Translation failed: {e}")
            self.root.after(0, lambda: messagebox.showerror("Translation Error", error_msg))
            self.log_message(f"Translation failed: {error_msg}")
            
        finally:
            self.is_processing = False
            self.root.after(0, self._update_ui_state)
            self.root.after(0, self._close_progress_dialog)
            self.status_var.set("Ready")
    
    def _create_progress_dialog(self, total_items: int):
        """Create progress dialog"""
        self.progress_dialog = ProgressDialog(self.root, total_items)
        self.progress_dialog.show()
    
    def _close_progress_dialog(self):
        """Close progress dialog"""
        if self.progress_dialog:
            self.progress_dialog.close()
            self.progress_dialog = None
    
    def _cancel_translation(self):
        """Cancel ongoing translation"""
        if self.is_processing:
            # Note: This is a simplified cancellation
            # In a full implementation, you'd need thread-safe cancellation
            self.is_processing = False
            self._update_ui_state()
            self.log_message("Translation cancelled by user")
            self.status_var.set("Cancelled")
    
    def _update_ui_state(self):
        """Update UI state based on processing status"""
        if self.is_processing:
            self.translate_button.config(state="disabled")
            self.cancel_button.config(state="normal")
            self.browse_button.config(state="disabled")
            self.file_entry.config(state="disabled")
        else:
            has_file = bool(self.current_file and os.path.exists(self.current_file))
            self.translate_button.config(state="normal" if has_file else "disabled")
            self.cancel_button.config(state="disabled")
            self.browse_button.config(state="normal")
            self.file_entry.config(state="readonly")
    
    def _test_connection(self):
        """Test connection to translation service"""
        self.log_message("Testing translation service connection...")
        
        def test_in_background():
            try:
                success = self.translator.test_connection()
                if success:
                    message = "Connection to translation service successful!"
                    self.root.after(0, lambda: messagebox.showinfo("Connection Test", message))
                    self.log_message("Connection test passed")
                else:
                    message = "Connection to translation service failed."
                    self.root.after(0, lambda: messagebox.showerror("Connection Test", message))
                    self.log_message("Connection test failed")
            except Exception as e:
                error_msg = f"Connection test error: {str(e)}"
                self.root.after(0, lambda: messagebox.showerror("Connection Test", error_msg))
                self.log_message(error_msg)
        
        threading.Thread(target=test_in_background, daemon=True).start()
    
    def _show_settings(self):
        """Show settings dialog"""
        dialog = SettingsDialog(self.root, self.config)
        dialog.show()
    
    def _show_about(self):
        """Show about dialog"""
        dialog = AboutDialog(self.root)
        dialog.show()
    
    def _show_documentation(self):
        """Show documentation"""
        import webbrowser
        webbrowser.open("https://github.com/yourusername/PPTrans/docs")
    
    def _clear_log(self):
        """Clear the log display"""
        self.log_text.config(state="normal")
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state="disabled")
    
    def log_message(self, message: str):
        """Add message to log display"""
        timestamp = __import__('datetime').datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")
        
        self.logger.info(message)
    
    def _load_window_state(self):
        """Load saved window state"""
        if self.config.get("gui.remember_window_size", True):
            # Window state is already loaded in _create_window
            pass
    
    def _save_window_state(self):
        """Save current window state"""
        if self.config.get("gui.remember_window_size", True):
            geometry = self.root.geometry()
            if 'x' in geometry:
                width, rest = geometry.split('x')
                height = rest.split('+')[0]
                self.config.update({
                    "gui.window_width": int(width),
                    "gui.window_height": int(height)
                })
    
    def _on_exit(self):
        """Handle application exit"""
        if self.is_processing:
            if not messagebox.askyesno("Exit", "Translation is in progress. Exit anyway?"):
                return
        
        self._save_window_state()
        self.logger.info("Application closing")
        self.root.quit()
    
    def run(self):
        """Start the GUI event loop"""
        self.logger.info("Starting GUI event loop")
        self.root.mainloop()