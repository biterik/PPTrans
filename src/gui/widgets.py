"""
Custom GUI widgets for PPTrans application
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable

class ProgressDialog:
    """Modal progress dialog with progress bar and cancel option"""
    
    def __init__(self, parent: tk.Widget, total_items: int, title: str = "Processing..."):
        """
        Initialize progress dialog
        
        Args:
            parent: Parent widget
            total_items: Total number of items to process
            title: Dialog title
        """
        self.parent = parent
        self.total_items = total_items
        self.current_item = 0
        self.cancelled = False
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog
        self._center_dialog()
        
        # Create widgets
        self._create_widgets()
        
        # Handle window close
        self.dialog.protocol("WM_DELETE_WINDOW", self.cancel)
    
    def _center_dialog(self):
        """Center dialog on parent window"""
        self.dialog.geometry("400x120")
        
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        x = parent_x + (parent_width - 400) // 2
        y = parent_y + (parent_height - 120) // 2
        
        self.dialog.geometry(f"400x120+{x}+{y}")
    
    def _create_widgets(self):
        """Create dialog widgets"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        # Status label
        self.status_var = tk.StringVar(value="Starting...")
        status_label = ttk.Label(main_frame, textvariable=self.status_var)
        status_label.pack(pady=(0, 10))
        
        # Progress bar
        self.progress_var = tk.IntVar()
        self.progress_bar = ttk.Progressbar(
            main_frame, 
            variable=self.progress_var,
            maximum=self.total_items,
            length=360
        )
        self.progress_bar.pack(pady=(0, 10))
        
        # Progress text
        self.progress_text_var = tk.StringVar(value=f"0 of {self.total_items}")
        progress_text = ttk.Label(main_frame, textvariable=self.progress_text_var, 
                                 font=("TkDefaultFont", 8))
        progress_text.pack(pady=(0, 10))
        
        # Cancel button
        cancel_button = ttk.Button(main_frame, text="Cancel", command=self.cancel)
        cancel_button.pack()
    
    def update_status(self, status: str):
        """Update status message"""
        self.status_var.set(status)
        self.dialog.update_idletasks()
    
    def increment(self, amount: int = 1):
        """Increment progress by specified amount"""
        self.current_item = min(self.current_item + amount, self.total_items)
        self.progress_var.set(self.current_item)
        self.progress_text_var.set(f"{self.current_item} of {self.total_items}")
        
        # Calculate percentage
        percentage = int((self.current_item / self.total_items) * 100)
        self.status_var.set(f"Processing... {percentage}%")
        
        self.dialog.update_idletasks()
    
    def set_progress(self, value: int):
        """Set progress to specific value"""
        self.current_item = min(max(value, 0), self.total_items)
        self.progress_var.set(self.current_item)
        self.progress_text_var.set(f"{self.current_item} of {self.total_items}")
        
        percentage = int((self.current_item / self.total_items) * 100)
        self.status_var.set(f"Processing... {percentage}%")
        
        self.dialog.update_idletasks()
    
    def cancel(self):
        """Handle cancel request"""
        self.cancelled = True
        self.status_var.set("Cancelling...")
        self.dialog.update_idletasks()
    
    def is_cancelled(self) -> bool:
        """Check if dialog was cancelled"""
        return self.cancelled
    
    def close(self):
        """Close the dialog"""
        if self.dialog:
            self.dialog.destroy()
    
    def show(self):
        """Show the dialog"""
        self.dialog.deiconify()
        self.dialog.focus_set()

class AboutDialog:
    """About dialog showing application information"""
    
    def __init__(self, parent: tk.Widget):
        """
        Initialize about dialog
        
        Args:
            parent: Parent widget
        """
        self.parent = parent
        self.dialog = None
    
    def show(self):
        """Show the about dialog"""
        if self.dialog:
            self.dialog.focus_set()
            return
        
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("About PPTrans")
        self.dialog.resizable(False, False)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Center dialog
        self.dialog.geometry("450x350")
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        x = parent_x + (parent_width - 450) // 2
        y = parent_y + (parent_height - 350) // 2
        
        self.dialog.geometry(f"450x350+{x}+{y}")
        
        # Create content
        self._create_content()
        
        # Handle close
        self.dialog.protocol("WM_DELETE_WINDOW", self._close)
    
    def _create_content(self):
        """Create dialog content"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        # Application icon/logo placeholder
        logo_frame = ttk.Frame(main_frame)
        logo_frame.pack(pady=(0, 20))
        
        # You could add an actual logo here
        logo_label = ttk.Label(logo_frame, text="🔄", font=("TkDefaultFont", 48))
        logo_label.pack()
        
        # Application name and version
        name_label = ttk.Label(main_frame, text="PPTrans", font=("TkDefaultFont", 18, "bold"))
        name_label.pack()
        
        version_label = ttk.Label(main_frame, text="Version 1.0.0", font=("TkDefaultFont", 10))
        version_label.pack(pady=(5, 20))
        
        # Description
        desc_text = """PowerPoint Translation Tool

A cross-platform desktop application for translating 
PowerPoint presentations while preserving all formatting, 
fonts, images, and layout.

Features:
• Multi-language translation support
• Format preservation
• Batch processing
• Cross-platform compatibility"""
        
        desc_label = ttk.Label(main_frame, text=desc_text, justify="center", 
                              font=("TkDefaultFont", 9))
        desc_label.pack(pady=(0, 20))
        
        # Copyright and links
        copyright_label = ttk.Label(main_frame, text="© 2025 Erik Bitzek", 
                                   font=("TkDefaultFont", 8))
        copyright_label.pack(pady=(0, 10))
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack()
        
        # GitHub link button (placeholder)
        github_button = ttk.Button(button_frame, text="GitHub", 
                                  command=self._open_github)
        github_button.pack(side="left", padx=(0, 10))
        
        # Close button
        close_button = ttk.Button(button_frame, text="Close", command=self._close)
        close_button.pack(side="left")
        
        # Focus close button
        close_button.focus_set()
    
    def _open_github(self):
        """Open GitHub repository"""
        import webbrowser
        webbrowser.open("https://github.com/yourusername/PPTrans")
    
    def _close(self):
        """Close the dialog"""
        if self.dialog:
            self.dialog.destroy()
            self.dialog = None

class LanguageSearchDialog:
    """Dialog for searching and selecting languages"""
    
    def __init__(self, parent: tk.Widget, language_manager, current_selection: str = ""):
        """
        Initialize language search dialog
        
        Args:
            parent: Parent widget
            language_manager: LanguageManager instance
            current_selection: Currently selected language
        """
        self.parent = parent
        self.language_manager = language_manager
        self.current_selection = current_selection
        self.selected_language = None
        self.dialog = None
    
    def show(self) -> Optional[str]:
        """
        Show dialog and return selected language
        
        Returns:
            Selected language code or None if cancelled
        """
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Select Language")
        self.dialog.resizable(True, True)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Set size and position
        self.dialog.geometry("500x400")
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        x = parent_x + (parent_width - 500) // 2
        y = parent_y + (parent_height - 400) // 2
        
        self.dialog.geometry(f"500x400+{x}+{y}")
        
        self._create_content()
        
        # Handle close
        self.dialog.protocol("WM_DELETE_WINDOW", self._cancel)
        
        # Wait for dialog to close
        self.dialog.wait_window()
        
        return self.selected_language
    
    def _create_content(self):
        """Create dialog content"""
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill="both", expand=True)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Search frame
        search_frame = ttk.Frame(main_frame)
        search_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        search_frame.columnconfigure(1, weight=1)
        
        ttk.Label(search_frame, text="Search:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.grid(row=0, column=1, sticky=(tk.W, tk.E))
        search_entry.bind('<KeyRelease>', self._on_search_changed)
        search_entry.focus_set()
        
        # Popular languages frame
        popular_frame = ttk.LabelFrame(main_frame, text="Popular Languages", padding="5")
        popular_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        popular_languages = self.language_manager.get_popular_languages()[:10]  # Top 10
        
        # Create buttons for popular languages
        col = 0
        row = 0
        for code, name in popular_languages:
            btn = ttk.Button(popular_frame, text=f"{name}", 
                           command=lambda c=code: self._select_language(c))
            btn.grid(row=row, column=col, padx=2, pady=2, sticky="ew")
            
            col += 1
            if col >= 5:  # 5 columns
                col = 0
                row += 1
        
        # Configure grid weights for popular frame
        for i in range(5):
            popular_frame.columnconfigure(i, weight=1)
        
        # Languages list frame
        list_frame = ttk.LabelFrame(main_frame, text="All Languages", padding="5")
        list_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # Create treeview for languages list
        self.tree = ttk.Treeview(list_frame, columns=("name", "code"), show="headings", height=10)
        self.tree.heading("name", text="Language")
        self.tree.heading("code", text="Code")
        self.tree.column("name", width=350)
        self.tree.column("code", width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Populate language list
        self._populate_language_list()
        
        # Bind double-click to select
        self.tree.bind("<Double-1>", self._on_tree_double_click)
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, pady=(10, 0))
        
        ttk.Button(button_frame, text="Select", command=self._select_from_tree).pack(side="left", padx=(0, 5))
        ttk.Button(button_frame, text="Cancel", command=self._cancel).pack(side="left")
    
    def _populate_language_list(self, filter_text: str = ""):
        """Populate the language list"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Get languages
        if filter_text:
            languages = self.language_manager.search_languages(filter_text)
        else:
            languages = self.language_manager.get_language_list(popular_first=True)
        
        # Add languages to tree
        for code, name in languages:
            self.tree.insert("", "end", values=(name, code))
    
    def _on_search_changed(self, event=None):
        """Handle search text change"""
        search_text = self.search_var.get()
        self._populate_language_list(search_text)
    
    def _on_tree_double_click(self, event=None):
        """Handle double-click on tree item"""
        self._select_from_tree()
    
    def _select_from_tree(self):
        """Select language from tree"""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            language_code = item['values'][1]
            self._select_language(language_code)
    
    def _select_language(self, language_code: str):
        """Select a language and close dialog"""
        self.selected_language = language_code
        self.dialog.destroy()
    
    def _cancel(self):
        """Cancel selection and close dialog"""
        self.selected_language = None
        self.dialog.destroy()

class StatusBar(ttk.Frame):
    """Status bar widget with multiple sections"""
    
    def __init__(self, parent, **kwargs):
        """Initialize status bar"""
        super().__init__(parent, **kwargs)
        
        self.labels = {}
        self._create_widgets()
    
    def _create_widgets(self):
        """Create status bar widgets"""
        # Main status
        self.main_label = ttk.Label(self, text="Ready", relief="sunken", padding="2")
        self.main_label.pack(side="left", fill="x", expand=True)
        
        # Progress section (initially hidden)
        self.progress_frame = ttk.Frame(self, relief="sunken")
        self.progress_var = tk.IntVar()
        self.progress_bar = ttk.Progressbar(self.progress_frame, variable=self.progress_var, 
                                          length=100, height=15)
        self.progress_bar.pack(side="left", padx=2, pady=1)
        
        # Additional info sections
        self.info_frame = ttk.Frame(self, relief="sunken")
        
    def set_status(self, text: str):
        """Set main status text"""
        self.main_label.config(text=text)
    
    def show_progress(self, maximum: int = 100):
        """Show progress bar"""
        self.progress_bar.config(maximum=maximum)
        self.progress_frame.pack(side="right", padx=2)
    
    def hide_progress(self):
        """Hide progress bar"""
        self.progress_frame.pack_forget()
    
    def set_progress(self, value: int):
        """Set progress value"""
        self.progress_var.set(value)
    
    def add_section(self, name: str, text: str = "", width: int = 100):
        """Add a new status section"""
        label = ttk.Label(self.info_frame, text=text, relief="sunken", 
                         padding="2", width=width)
        label.pack(side="right", padx=1)
        self.labels[name] = label
        
        # Pack info frame
        if not self.info_frame.winfo_ismapped():
            self.info_frame.pack(side="right")
    
    def update_section(self, name: str, text: str):
        """Update text in a named section"""
        if name in self.labels:
            self.labels[name].config(text=text)
    
    def remove_section(self, name: str):
        """Remove a named section"""
        if name in self.labels:
            self.labels[name].destroy()
            del self.labels[name]
            
            # Hide info frame if no sections remain
            if not self.labels:
                self.info_frame.pack_forget()