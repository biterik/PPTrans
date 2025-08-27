"""
Application dialogs for PPTrans
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any, Optional
from utils.config import Config

class SettingsDialog:
    """Settings configuration dialog"""
    
    def __init__(self, parent: tk.Widget, config: Config):
        """
        Initialize settings dialog
        
        Args:
            parent: Parent widget
            config: Configuration manager instance
        """
        self.parent = parent
        self.config = config
        self.dialog = None
        self.settings = {}
        
        # Load current settings
        self._load_current_settings()
    
    def _load_current_settings(self):
        """Load current configuration settings"""
        self.settings = {
            # GUI settings
            'window_width': self.config.get('gui.window_width', 800),
            'window_height': self.config.get('gui.window_height', 600),
            'remember_window_size': self.config.get('gui.remember_window_size', True),
            'remember_last_directory': self.config.get('gui.remember_last_directory', True),
            
            # Translation settings
            'default_source_language': self.config.get('translation.default_source_language', 'auto'),
            'default_target_language': self.config.get('translation.default_target_language', 'en'),
            'chunk_size': self.config.get('translation.chunk_size', 5000),
            'max_retries': self.config.get('translation.max_retries', 3),
            'retry_delay': self.config.get('translation.retry_delay', 1.0),
            'timeout': self.config.get('translation.timeout', 30),
            
            # Advanced settings
            'preserve_animations': self.config.get('advanced.preserve_animations', True),
            'backup_original': self.config.get('advanced.backup_original', True),
            'parallel_processing': self.config.get('advanced.parallel_processing', False),
            'max_workers': self.config.get('advanced.max_workers', 4),
            
            # Logging settings
            'log_level': self.config.get('logging.level', 'INFO'),
            'console_output': self.config.get('logging.console_output', True),
            'file_output': self.config.get('logging.file_output', True),
        }
    
    def show(self):
        """Show the settings dialog"""
        if self.dialog:
            self.dialog.focus_set()
            return
        
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Settings")
        self.dialog.resizable(True, True)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Set size and position
        self.dialog.geometry("600x500")
        self._center_dialog()
        
        # Create content
        self._create_content()
        
        # Handle close
        self.dialog.protocol("WM_DELETE_WINDOW", self._close)
    
    def _center_dialog(self):
        """Center dialog on parent window"""
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        x = parent_x + (parent_width - 600) // 2
        y = parent_y + (parent_height - 500) // 2
        
        self.dialog.geometry(f"600x500+{x}+{y}")
    
    def _create_content(self):
        """Create dialog content"""
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill="both", expand=True)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
        # Create notebook for tabbed interface
        notebook = ttk.Notebook(main_frame)
        notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Create tabs
        self._create_gui_tab(notebook)
        self._create_translation_tab(notebook)
        self._create_advanced_tab(notebook)
        self._create_logging_tab(notebook)
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Buttons
        ttk.Button(button_frame, text="Reset to Defaults", 
                  command=self._reset_defaults).pack(side="left")
        
        button_right_frame = ttk.Frame(button_frame)
        button_right_frame.pack(side="right")
        
        ttk.Button(button_right_frame, text="Cancel", 
                  command=self._close).pack(side="right", padx=(5, 0))
        ttk.Button(button_right_frame, text="Apply", 
                  command=self._apply_settings).pack(side="right", padx=(5, 0))
        ttk.Button(button_right_frame, text="OK", 
                  command=self._ok_clicked).pack(side="right", padx=(5, 0))
    
    def _create_gui_tab(self, notebook: ttk.Notebook):
        """Create GUI settings tab"""
        frame = ttk.Frame(notebook, padding="10")
        notebook.add(frame, text="Interface")
        
        # Window settings
        window_group = ttk.LabelFrame(frame, text="Window Settings", padding="10")
        window_group.pack(fill="x", pady=(0, 10))
        
        # Window size
        size_frame = ttk.Frame(window_group)
        size_frame.pack(fill="x", pady=(0, 5))
        
        ttk.Label(size_frame, text="Default Window Size:").pack(side="left")
        
        self.width_var = tk.StringVar(value=str(self.settings['window_width']))
        width_spin = ttk.Spinbox(size_frame, from_=400, to=2000, textvariable=self.width_var, width=8)
        width_spin.pack(side="right", padx=(5, 0))
        
        ttk.Label(size_frame, text="×").pack(side="right")
        
        self.height_var = tk.StringVar(value=str(self.settings['window_height']))
        height_spin = ttk.Spinbox(size_frame, from_=300, to=1500, textvariable=self.height_var, width=8)
        height_spin.pack(side="right")
        
        # Remember settings
        self.remember_size_var = tk.BooleanVar(value=self.settings['remember_window_size'])
        ttk.Checkbutton(window_group, text="Remember window size and position", 
                       variable=self.remember_size_var).pack(anchor="w", pady=(5, 0))
        
        self.remember_dir_var = tk.BooleanVar(value=self.settings['remember_last_directory'])
        ttk.Checkbutton(window_group, text="Remember last used directory", 
                       variable=self.remember_dir_var).pack(anchor="w")
    
    def _create_translation_tab(self, notebook: ttk.Notebook):
        """Create translation settings tab"""
        frame = ttk.Frame(notebook, padding="10")
        notebook.add(frame, text="Translation")
        
        # Default languages
        lang_group = ttk.LabelFrame(frame, text="Default Languages", padding="10")
        lang_group.pack(fill="x", pady=(0, 10))
        lang_group.columnconfigure(1, weight=1)
        
        ttk.Label(lang_group, text="Source Language:").grid(row=0, column=0, sticky="w", pady=(0, 5))
        self.source_lang_var = tk.StringVar(value=self.settings['default_source_language'])
        source_combo = ttk.Combobox(lang_group, textvariable=self.source_lang_var, 
                                   values=['auto', 'en', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'ja', 'ko', 'zh-cn'])
        source_combo.grid(row=0, column=1, sticky="ew", padx=(5, 0), pady=(0, 5))
        
        ttk.Label(lang_group, text="Target Language:").grid(row=1, column=0, sticky="w")
        self.target_lang_var = tk.StringVar(value=self.settings['default_target_language'])
        target_combo = ttk.Combobox(lang_group, textvariable=self.target_lang_var,
                                   values=['en', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'ja', 'ko', 'zh-cn'])
        target_combo.grid(row=1, column=1, sticky="ew", padx=(5, 0))
        
        # Translation options
        options_group = ttk.LabelFrame(frame, text="Translation Options", padding="10")
        options_group.pack(fill="x", pady=(0, 10))
        options_group.columnconfigure(1, weight=1)
        
        # Chunk size
        ttk.Label(options_group, text="Text Chunk Size:").grid(row=0, column=0, sticky="w", pady=(0, 5))
        self.chunk_size_var = tk.StringVar(value=str(self.settings['chunk_size']))
        chunk_spin = ttk.Spinbox(options_group, from_=1000, to=10000, increment=1000,
                                textvariable=self.chunk_size_var, width=10)
        chunk_spin.grid(row=0, column=1, sticky="w", padx=(5, 0), pady=(0, 5))
        ttk.Label(options_group, text="characters").grid(row=0, column=2, sticky="w", padx=(5, 0), pady=(0, 5))
        
        # Max retries
        ttk.Label(options_group, text="Max Retries:").grid(row=1, column=0, sticky="w", pady=(0, 5))
        self.max_retries_var = tk.StringVar(value=str(self.settings['max_retries']))
        retry_spin = ttk.Spinbox(options_group, from_=1, to=10, textvariable=self.max_retries_var, width=10)
        retry_spin.grid(row=1, column=1, sticky="w", padx=(5, 0), pady=(0, 5))
        
        # Retry delay
        ttk.Label(options_group, text="Retry Delay:").grid(row=2, column=0, sticky="w", pady=(0, 5))
        self.retry_delay_var = tk.StringVar(value=str(self.settings['retry_delay']))
        delay_spin = ttk.Spinbox(options_group, from_=0.5, to=5.0, increment=0.5,
                                textvariable=self.retry_delay_var, width=10)
        delay_spin.grid(row=2, column=1, sticky="w", padx=(5, 0), pady=(0, 5))
        ttk.Label(options_group, text="seconds").grid(row=2, column=2, sticky="w", padx=(5, 0), pady=(0, 5))
        
        # Timeout
        ttk.Label(options_group, text="Request Timeout:").grid(row=3, column=0, sticky="w")
        self.timeout_var = tk.StringVar(value=str(self.settings['timeout']))
        timeout_spin = ttk.Spinbox(options_group, from_=10, to=120, increment=10,
                                  textvariable=self.timeout_var, width=10)
        timeout_spin.grid(row=3, column=1, sticky="w", padx=(5, 0))
        ttk.Label(options_group, text="seconds").grid(row=3, column=2, sticky="w", padx=(5, 0))
    
    def _create_advanced_tab(self, notebook: ttk.Notebook):
        """Create advanced settings tab"""
        frame = ttk.Frame(notebook, padding="10")
        notebook.add(frame, text="Advanced")
        
        # PowerPoint options
        pptx_group = ttk.LabelFrame(frame, text="PowerPoint Processing", padding="10")
        pptx_group.pack(fill="x", pady=(0, 10))
        
        self.preserve_animations_var = tk.BooleanVar(value=self.settings['preserve_animations'])
        ttk.Checkbutton(pptx_group, text="Preserve animations and transitions", 
                       variable=self.preserve_animations_var).pack(anchor="w", pady=(0, 5))
        
        self.backup_original_var = tk.BooleanVar(value=self.settings['backup_original'])
        ttk.Checkbutton(pptx_group, text="Create backup of original file", 
                       variable=self.backup_original_var).pack(anchor="w")
        
        # Performance options
        perf_group = ttk.LabelFrame(frame, text="Performance", padding="10")
        perf_group.pack(fill="x", pady=(0, 10))
        perf_group.columnconfigure(1, weight=1)
        
        self.parallel_processing_var = tk.BooleanVar(value=self.settings['parallel_processing'])
        parallel_check = ttk.Checkbutton(perf_group, text="Enable parallel processing (experimental)", 
                                        variable=self.parallel_processing_var,
                                        command=self._on_parallel_changed)
        parallel_check.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 5))
        
        ttk.Label(perf_group, text="Max Worker Threads:").grid(row=1, column=0, sticky="w")
        self.max_workers_var = tk.StringVar(value=str(self.settings['max_workers']))
        self.workers_spin = ttk.Spinbox(perf_group, from_=1, to=16, textvariable=self.max_workers_var, width=10)
        self.workers_spin.grid(row=1, column=1, sticky="w", padx=(5, 0))
        
        # Update worker spinbox state
        self._on_parallel_changed()
        
        # Warning
        warning_label = ttk.Label(frame, text="⚠️ Parallel processing may cause instability with some translation services.", 
                                 foreground="orange", font=("TkDefaultFont", 8))
        warning_label.pack(pady=(10, 0))
    
    def _create_logging_tab(self, notebook: ttk.Notebook):
        """Create logging settings tab"""
        frame = ttk.Frame(notebook, padding="10")
        notebook.add(frame, text="Logging")
        
        # Logging level
        level_group = ttk.LabelFrame(frame, text="Logging Level", padding="10")
        level_group.pack(fill="x", pady=(0, 10))
        level_group.columnconfigure(1, weight=1)
        
        ttk.Label(level_group, text="Log Level:").grid(row=0, column=0, sticky="w")
        self.log_level_var = tk.StringVar(value=self.settings['log_level'])
        level_combo = ttk.Combobox(level_group, textvariable=self.log_level_var, state="readonly",
                                  values=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'])
        level_combo.grid(row=0, column=1, sticky="w", padx=(5, 0))
        
        # Output options
        output_group = ttk.LabelFrame(frame, text="Output Options", padding="10")
        output_group.pack(fill="x", pady=(0, 10))
        
        self.console_output_var = tk.BooleanVar(value=self.settings['console_output'])
        ttk.Checkbutton(output_group, text="Enable console output", 
                       variable=self.console_output_var).pack(anchor="w", pady=(0, 5))
        
        self.file_output_var = tk.BooleanVar(value=self.settings['file_output'])
        ttk.Checkbutton(output_group, text="Enable file logging", 
                       variable=self.file_output_var).pack(anchor="w")
        
        # Log level descriptions
        desc_group = ttk.LabelFrame(frame, text="Log Level Descriptions", padding="10")
        desc_group.pack(fill="x")
        
        descriptions = {
            'DEBUG': 'Detailed information for debugging',
            'INFO': 'General information about program execution',
            'WARNING': 'Warning messages for potential issues',
            'ERROR': 'Error messages for serious problems',
            'CRITICAL': 'Critical errors that may cause program termination'
        }
        
        for level, desc in descriptions.items():
            ttk.Label(desc_group, text=f"{level}: {desc}", 
                     font=("TkDefaultFont", 8)).pack(anchor="w")
    
    def _on_parallel_changed(self):
        """Handle parallel processing checkbox change"""
        if self.parallel_processing_var.get():
            self.workers_spin.config(state="normal")
        else:
            self.workers_spin.config(state="disabled")
    
    def _reset_defaults(self):
        """Reset all settings to defaults"""
        if messagebox.askyesno("Reset Settings", 
                              "Are you sure you want to reset all settings to their default values?"):
            self.config.reset_to_defaults()
            self._load_current_settings()
            self._update_widgets()
            messagebox.showinfo("Settings Reset", "All settings have been reset to their default values.")
    
    def _update_widgets(self):
        """Update all widget values from current settings"""
        # GUI settings
        self.width_var.set(str(self.settings['window_width']))
        self.height_var.set(str(self.settings['window_height']))
        self.remember_size_var.set(self.settings['remember_window_size'])
        self.remember_dir_var.set(self.settings['remember_last_directory'])
        
        # Translation settings
        self.source_lang_var.set(self.settings['default_source_language'])
        self.target_lang_var.set(self.settings['default_target_language'])
        self.chunk_size_var.set(str(self.settings['chunk_size']))
        self.max_retries_var.set(str(self.settings['max_retries']))
        self.retry_delay_var.set(str(self.settings['retry_delay']))
        self.timeout_var.set(str(self.settings['timeout']))
        
        # Advanced settings
        self.preserve_animations_var.set(self.settings['preserve_animations'])
        self.backup_original_var.set(self.settings['backup_original'])
        self.parallel_processing_var.set(self.settings['parallel_processing'])
        self.max_workers_var.set(str(self.settings['max_workers']))
        
        # Logging settings
        self.log_level_var.set(self.settings['log_level'])
        self.console_output_var.set(self.settings['console_output'])
        self.file_output_var.set(self.settings['file_output'])
        
        # Update dependent widgets
        self._on_parallel_changed()
    
    def _apply_settings(self):
        """Apply current settings"""
        try:
            # Collect settings from widgets
            updates = {
                'gui.window_width': int(self.width_var.get()),
                'gui.window_height': int(self.height_var.get()),
                'gui.remember_window_size': self.remember_size_var.get(),
                'gui.remember_last_directory': self.remember_dir_var.get(),
                
                'translation.default_source_language': self.source_lang_var.get(),
                'translation.default_target_language': self.target_lang_var.get(),
                'translation.chunk_size': int(self.chunk_size_var.get()),
                'translation.max_retries': int(self.max_retries_var.get()),
                'translation.retry_delay': float(self.retry_delay_var.get()),
                'translation.timeout': int(self.timeout_var.get()),
                
                'advanced.preserve_animations': self.preserve_animations_var.get(),
                'advanced.backup_original': self.backup_original_var.get(),
                'advanced.parallel_processing': self.parallel_processing_var.get(),
                'advanced.max_workers': int(self.max_workers_var.get()),
                
                'logging.level': self.log_level_var.get(),
                'logging.console_output': self.console_output_var.get(),
                'logging.file_output': self.file_output_var.get(),
            }
            
            # Apply updates
            self.config.update(updates)
            messagebox.showinfo("Settings Applied", "Settings have been saved successfully.")
            
        except ValueError as e:
            messagebox.showerror("Invalid Input", f"Please check your input values: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")
    
    def _ok_clicked(self):
        """Handle OK button click"""
        self._apply_settings()
        self._close()
    
    def _close(self):
        """Close the dialog"""
        if self.dialog:
            self.dialog.destroy()
            self.dialog = None

class TranslationProgressDialog:
    """Specialized progress dialog for translation operations"""
    
    def __init__(self, parent: tk.Widget, total_elements: int):
        """
        Initialize translation progress dialog
        
        Args:
            parent: Parent widget
            total_elements: Total number of text elements to translate
        """
        self.parent = parent
        self.total_elements = total_elements
        self.current_element = 0
        self.cancelled = False
        
        # Translation statistics
        self.start_time = None
        self.translated_chars = 0
        self.errors = 0
        
        self._create_dialog()
    
    def _create_dialog(self):
        """Create the progress dialog"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Translation Progress")
        self.dialog.resizable(False, False)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Center dialog
        self.dialog.geometry("500x200")
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        x = parent_x + (parent_width - 500) // 2
        y = parent_y + (parent_height - 200) // 2
        
        self.dialog.geometry(f"500x200+{x}+{y}")
        
        # Create widgets
        self._create_widgets()
        
        # Handle close
        self.dialog.protocol("WM_DELETE_WINDOW", self.cancel)
        
        # Start timer
        import time
        self.start_time = time.time()
    
    def _create_widgets(self):
        """Create dialog widgets"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Translating PowerPoint Presentation", 
                               font=("TkDefaultFont", 12, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Main progress bar
        self.progress_var = tk.IntVar()
        self.progress_bar = ttk.Progressbar(
            main_frame, 
            variable=self.progress_var,
            maximum=self.total_elements,
            length=460
        )
        self.progress_bar.pack(pady=(0, 10))
        
        # Progress text
        self.progress_text_var = tk.StringVar(value=f"0 of {self.total_elements} elements")
        progress_text = ttk.Label(main_frame, textvariable=self.progress_text_var)
        progress_text.pack(pady=(0, 10))
        
        # Statistics frame
        stats_frame = ttk.Frame(main_frame)
        stats_frame.pack(fill="x", pady=(0, 10))
        
        # Left column - statistics
        left_frame = ttk.Frame(stats_frame)
        left_frame.pack(side="left", fill="x", expand=True)
        
        self.chars_var = tk.StringVar(value="Characters: 0")
        ttk.Label(left_frame, textvariable=self.chars_var, font=("TkDefaultFont", 8)).pack(anchor="w")
        
        self.time_var = tk.StringVar(value="Time: 00:00")
        ttk.Label(left_frame, textvariable=self.time_var, font=("TkDefaultFont", 8)).pack(anchor="w")
        
        self.speed_var = tk.StringVar(value="Speed: - chars/sec")
        ttk.Label(left_frame, textvariable=self.speed_var, font=("TkDefaultFont", 8)).pack(anchor="w")
        
        # Right column - errors
        right_frame = ttk.Frame(stats_frame)
        right_frame.pack(side="right")
        
        self.errors_var = tk.StringVar(value="Errors: 0")
        ttk.Label(right_frame, textvariable=self.errors_var, font=("TkDefaultFont", 8)).pack(anchor="e")
        
        self.eta_var = tk.StringVar(value="ETA: --:--")
        ttk.Label(right_frame, textvariable=self.eta_var, font=("TkDefaultFont", 8)).pack(anchor="e")
        
        # Cancel button
        ttk.Button(main_frame, text="Cancel", command=self.cancel).pack()
    
    def update_progress(self, element_index: int, char_count: int = 0, error_occurred: bool = False):
        """
        Update progress information
        
        Args:
            element_index: Current element index (0-based)
            char_count: Number of characters in current element
            error_occurred: Whether an error occurred with this element
        """
        self.current_element = element_index + 1
        self.progress_var.set(self.current_element)
        
        # Update character count
        if char_count > 0:
            self.translated_chars += char_count
        
        # Update error count
        if error_occurred:
            self.errors += 1
        
        # Update text displays
        self.progress_text_var.set(f"{self.current_element} of {self.total_elements} elements")
        self.chars_var.set(f"Characters: {self.translated_chars:,}")
        self.errors_var.set(f"Errors: {self.errors}")
        
        # Update time and speed
        if self.start_time:
            import time
            elapsed = time.time() - self.start_time
            
            # Format time
            minutes = int(elapsed // 60)
            seconds = int(elapsed % 60)
            self.time_var.set(f"Time: {minutes:02d}:{seconds:02d}")
            
            # Calculate speed
            if elapsed > 0:
                chars_per_sec = self.translated_chars / elapsed
                self.speed_var.set(f"Speed: {chars_per_sec:.1f} chars/sec")
                
                # Calculate ETA
                if self.current_element > 0:
                    total_time_estimate = elapsed * (self.total_elements / self.current_element)
                    remaining_time = total_time_estimate - elapsed
                    
                    if remaining_time > 0:
                        eta_minutes = int(remaining_time // 60)
                        eta_seconds = int(remaining_time % 60)
                        self.eta_var.set(f"ETA: {eta_minutes:02d}:{eta_seconds:02d}")
                    else:
                        self.eta_var.set("ETA: 00:00")
        
        # Update display
        self.dialog.update_idletasks()
    
    def cancel(self):
        """Handle cancel request"""
        self.cancelled = True
        self.dialog.destroy()
    
    def is_cancelled(self) -> bool:
        """Check if translation was cancelled"""
        return self.cancelled
    
    def close(self):
        """Close the dialog"""
        if self.dialog and self.dialog.winfo_exists():
            self.dialog.destroy()