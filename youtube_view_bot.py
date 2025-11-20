"""YouTube View Bot - Main Application

GUI-based bot to automate YouTube video views with proxy rotation,
profile management, and realistic browsing behavior.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import queue
import time
from typing import Optional
import random

from proxy_module import ProxyManager, ProxyListManager
from hidemium_module import HidemiumClient
from youtube_bot.worker import ViewBotWorker
from youtube_bot.youtube_helper import get_latest_video_url


class YouTubeViewBotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube View Bot")
        self.root.geometry("800x600")
        
        # State
        self.is_running = False
        self.workers = []
        self.log_queue = queue.Queue()

        # Managers
        self.proxy_manager = ProxyManager()
        self.proxy_list_manager: Optional[ProxyListManager] = None
        self.hidemium_client = HidemiumClient()
        
        self.setup_gui()
        self.check_log_queue()
    
    def setup_gui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Input fields
        row = 0
        
        # Channel URL
        ttk.Label(main_frame, text="YouTube Channel URL:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.channel_url_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.channel_url_var, width=50).grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        # Number of threads
        ttk.Label(main_frame, text="Số luồng:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.threads_var = tk.StringVar(value="3")
        ttk.Entry(main_frame, textvariable=self.threads_var, width=20).grid(row=row, column=1, sticky=tk.W, pady=5)
        row += 1
        
        # Watch time (seconds)
        ttk.Label(main_frame, text="Thời gian xem (giây):").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.watch_time_var = tk.StringVar(value="60")
        ttk.Entry(main_frame, textvariable=self.watch_time_var, width=20).grid(row=row, column=1, sticky=tk.W, pady=5)
        row += 1
        
        # View count
        ttk.Label(main_frame, text="Số lượng view:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.view_count_var = tk.StringVar(value="10")
        ttk.Entry(main_frame, textvariable=self.view_count_var, width=20).grid(row=row, column=1, sticky=tk.W, pady=5)
        row += 1

        # Proxy source selection
        ttk.Label(main_frame, text="Nguồn Proxy:").grid(row=row, column=0, sticky=tk.W, pady=5)
        proxy_source_frame = ttk.Frame(main_frame)
        proxy_source_frame.grid(row=row, column=1, sticky=tk.W, pady=5)

        self.proxy_source_var = tk.StringVar(value="api")
        ttk.Radiobutton(proxy_source_frame, text="API Server", variable=self.proxy_source_var,
                       value="api", command=self.on_proxy_source_change).grid(row=0, column=0, padx=5)
        ttk.Radiobutton(proxy_source_frame, text="Import File", variable=self.proxy_source_var,
                       value="file", command=self.on_proxy_source_change).grid(row=0, column=1, padx=5)
        row += 1

        # Network interface (only for API mode)
        ttk.Label(main_frame, text="Network Interface:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.interface_var = tk.StringVar(value="Ethernet")
        self.interface_entry = ttk.Entry(main_frame, textvariable=self.interface_var, width=20)
        self.interface_entry.grid(row=row, column=1, sticky=tk.W, pady=5)
        row += 1

        # Proxy file selection (only for file mode)
        ttk.Label(main_frame, text="Proxy File:").grid(row=row, column=0, sticky=tk.W, pady=5)
        proxy_file_frame = ttk.Frame(main_frame)
        proxy_file_frame.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)

        self.proxy_file_var = tk.StringVar()
        self.proxy_file_entry = ttk.Entry(proxy_file_frame, textvariable=self.proxy_file_var, width=40, state=tk.DISABLED)
        self.proxy_file_entry.grid(row=0, column=0, sticky=(tk.W, tk.E))
        proxy_file_frame.columnconfigure(0, weight=1)

        self.browse_button = ttk.Button(proxy_file_frame, text="Browse...", command=self.browse_proxy_file, state=tk.DISABLED)
        self.browse_button.grid(row=0, column=1, padx=(5, 0))
        row += 1
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=row, column=0, columnspan=2, pady=10)
        
        self.start_button = ttk.Button(button_frame, text="Start", command=self.start_bot)
        self.start_button.grid(row=0, column=0, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="Stop", command=self.stop_bot, state=tk.DISABLED)
        self.stop_button.grid(row=0, column=1, padx=5)
        
        row += 1
        
        # Status
        self.status_var = tk.StringVar(value="Đã sẵn sàng")
        status_label = ttk.Label(main_frame, textvariable=self.status_var, foreground="green")
        status_label.grid(row=row, column=0, columnspan=2, pady=5)
        row += 1
        
        # Log display
        ttk.Label(main_frame, text="Log:").grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=5)
        row += 1
        
        self.log_text = scrolledtext.ScrolledText(main_frame, height=20, width=80, state=tk.DISABLED)
        self.log_text.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        main_frame.rowconfigure(row, weight=1)
    
    def on_proxy_source_change(self):
        """Handle proxy source change."""
        if self.proxy_source_var.get() == "api":
            # Enable interface, disable file
            self.interface_entry.config(state=tk.NORMAL)
            self.proxy_file_entry.config(state=tk.DISABLED)
            self.browse_button.config(state=tk.DISABLED)
        else:
            # Disable interface, enable file
            self.interface_entry.config(state=tk.DISABLED)
            self.proxy_file_entry.config(state=tk.NORMAL)
            self.browse_button.config(state=tk.NORMAL)

    def browse_proxy_file(self):
        """Open file dialog to select proxy file."""
        filename = filedialog.askopenfilename(
            title="Chọn file proxy",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            self.proxy_file_var.set(filename)
            # Try to load proxies
            try:
                self.proxy_list_manager = ProxyListManager(filename)
                count = self.proxy_list_manager.get_proxy_count()
                self.log(f"✅ Đã load {count} proxy từ file")
            except Exception as e:
                messagebox.showerror("Error", f"Lỗi khi load file proxy: {e}")
                self.proxy_file_var.set("")
                self.proxy_list_manager = None

    def log(self, message: str):
        """Add message to log queue."""
        self.log_queue.put(message)
    
    def check_log_queue(self):
        """Check log queue and update GUI."""
        try:
            while True:
                message = self.log_queue.get_nowait()
                self.log_text.config(state=tk.NORMAL)
                self.log_text.insert(tk.END, f"{message}\n")
                self.log_text.see(tk.END)
                self.log_text.config(state=tk.DISABLED)
        except queue.Empty:
            pass
        
        self.root.after(100, self.check_log_queue)
    
    def validate_inputs(self) -> bool:
        """Validate user inputs."""
        if not self.channel_url_var.get().strip():
            messagebox.showerror("Error", "Vui lòng nhập URL kênh YouTube")
            return False

        try:
            threads = int(self.threads_var.get())
            if threads < 1:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Số luồng phải >= 1")
            return False

        try:
            watch_time = int(self.watch_time_var.get())
            if watch_time < 10:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Thời gian xem tối thiểu 10 giây")
            return False

        try:
            view_count = int(self.view_count_var.get())
            if view_count < 1:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Số lượng view phải >= 1")
            return False

        # Validate proxy source
        if self.proxy_source_var.get() == "file":
            if not self.proxy_file_var.get().strip():
                messagebox.showerror("Error", "Vui lòng chọn file proxy")
                return False
            if not self.proxy_list_manager or self.proxy_list_manager.get_proxy_count() == 0:
                messagebox.showerror("Error", "File proxy không hợp lệ hoặc rỗng")
                return False

        return True
    
    def start_bot(self):
        """Start the bot."""
        if not self.validate_inputs():
            return
        
        # Check services
        if not self.hidemium_client.health():
            messagebox.showerror("Error", "Hidemium service không chạy tại http://127.0.0.1:2222")
            return
        
        self.is_running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_var.set("Đang chạy...")
        
        # Get inputs
        channel_url = self.channel_url_var.get().strip()
        num_threads = int(self.threads_var.get())
        watch_time = int(self.watch_time_var.get())
        view_count = int(self.view_count_var.get())
        interface = self.interface_var.get().strip()
        proxy_source = self.proxy_source_var.get()

        # Start worker thread
        worker_thread = threading.Thread(
            target=self.run_bot,
            args=(channel_url, num_threads, watch_time, view_count, interface, proxy_source),
            daemon=True
        )
        worker_thread.start()
    
    def stop_bot(self):
        """Stop the bot."""
        self.is_running = False
        self.status_var.set("Đang dừng...")
        self.log("Đang dừng bot...")
        
        # Stop all workers
        for worker in self.workers:
            worker.stop()
        
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_var.set("Đã dừng")
    
    def run_bot(self, channel_url: str, num_threads: int, watch_time: int, view_count: int, interface: str, proxy_source: str):
        """Main bot logic running in separate thread."""
        try:
            # Get latest video
            self.log(f"Đang lấy video mới nhất từ kênh: {channel_url}")
            video_url = get_latest_video_url(channel_url)

            if not video_url:
                self.log("❌ Không thể lấy video mới nhất")
                self.stop_bot()
                return

            self.log(f"✅ Video: {video_url}")

            # Log proxy source
            if proxy_source == "api":
                self.log(f"📡 Sử dụng API Server (Interface: {interface})")
            else:
                proxy_count = self.proxy_list_manager.get_proxy_count() if self.proxy_list_manager else 0
                self.log(f"📁 Sử dụng Proxy File ({proxy_count} proxies)")

            # Calculate views per thread
            views_completed = 0

            while self.is_running and views_completed < view_count:
                # Create workers batch
                batch_size = min(num_threads, view_count - views_completed)
                self.workers = []

                for i in range(batch_size):
                    if not self.is_running:
                        break

                    worker = ViewBotWorker(
                        worker_id=views_completed + i + 1,
                        video_url=video_url,
                        watch_time=watch_time,
                        proxy_manager=self.proxy_manager if proxy_source == "api" else None,
                        proxy_list_manager=self.proxy_list_manager if proxy_source == "file" else None,
                        hidemium_client=self.hidemium_client,
                        interface=interface,
                        log_callback=self.log
                    )
                    self.workers.append(worker)
                    worker.start()

                    # Delay 1s between workers to avoid overwhelming APIs
                    if i < batch_size - 1:  # Don't delay after last worker
                        time.sleep(1)
                
                # Wait for workers to complete
                for worker in self.workers:
                    worker.join()
                
                views_completed += batch_size
                self.log(f"Hoàn thành: {views_completed}/{view_count} views")
            
            if views_completed >= view_count:
                self.log("✅ Hoàn thành tất cả views!")
                self.status_var.set("Hoàn thành")
            
        except Exception as e:
            self.log(f"❌ Lỗi: {e}")
            import traceback
            self.log(traceback.format_exc())
        finally:
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            if self.is_running:
                self.is_running = False


def main():
    root = tk.Tk()
    app = YouTubeViewBotGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
