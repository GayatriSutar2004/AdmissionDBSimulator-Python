import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# ==========================================================
#                  DATA HANDLER FUNCTIONS
# ==========================================================
def load_data(file_path):
    if file_path.endswith(".csv"):
        df = pd.read_csv(file_path)
    else:
        df = pd.read_excel(file_path)

    required = ["Name", "Course", "Year", "Admission Status"]
    for col in required:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    df.dropna(subset=required, inplace=True)
    return df


def get_unique_options(df):
    options = {}
    for col in ["Course", "Admission Status"]:
        if col in df.columns:
            options[col] = df[col].dropna().unique().tolist()
        else:
            options[col] = []
    return options


def apply_filters(df, course, status):
    filtered = df.copy()
    if course:
        filtered = filtered[filtered["Course"] == course]
    if status:
        filtered = filtered[filtered["Admission Status"] == status]
    return filtered


# ==========================================================
#                  VISUALIZATION FUNCTION
# ==========================================================
def clear_frame(frame):
    for widget in frame.winfo_children():
        widget.destroy()


def plot_chart(df, frame, chart_type):
    clear_frame(frame)
    if df.empty:
        return

    fig, ax = plt.subplots(figsize=(5, 4))

    if chart_type == "Bar Chart":
        df["Course"].value_counts().plot(kind="bar", color="#3b82f6", ax=ax)
        ax.set_title("Admissions by Course")
        ax.set_xlabel("Course")
        ax.set_ylabel("Count")

    elif chart_type == "Pie Chart":
        df["Admission Status"].value_counts().plot(kind="pie", autopct="%1.1f%%", ax=ax)
        ax.set_ylabel("")

    elif chart_type == "Line Chart":
        if "Year" in df.columns:
            df.groupby("Year").size().plot(kind="line", marker="o", color="#10b981", ax=ax)
            ax.set_title("Admissions Over Years")
            ax.set_xlabel("Year")
            ax.set_ylabel("Count")

    plt.tight_layout()
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)


# ==========================================================
#                  MAIN APPLICATION CLASS
# ==========================================================
class AdmissionDbSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("AdmissionDbSimulator")
        self.root.geometry("1200x750")
        self.root.configure(bg="#f8fafc")

        self.df = None
        self.filtered_df = None
        self.bg_photo = None

        # Sidebar
        self.sidebar = tk.Frame(self.root, bg="#1e293b", width=220)
        self.sidebar.pack(side="left", fill="y")

        # Main area (Header + Content)
        main_area = tk.Frame(self.root, bg="#f8fafc")
        main_area.pack(side="right", fill="both", expand=True)

        # Header (title bar)
        self.header = tk.Frame(main_area, bg="#1e3a8a", height=70)
        self.header.pack(fill="x")

        tk.Label(
            self.header, text="🎓 Admission Database Simulator",
            font=("Helvetica", 22, "bold"), fg="white", bg="#1e3a8a"
        ).pack(pady=15)

        # Content area (below header)
        self.content = tk.Frame(main_area, bg="#f8fafc")
        self.content.pack(fill="both", expand=True)

        # Load background image
        self.load_common_background()

        # Sidebar buttons
        self.create_sidebar()
        self.show_home()

    # ---------------- Load Common Background ----------------
    def load_common_background(self):
        try:
            bg_image = Image.open("background.png").resize((1000, 750))
            self.bg_photo = ImageTk.PhotoImage(bg_image)
        except FileNotFoundError:
            self.bg_photo = None

    def set_page_background(self):
        for widget in self.content.winfo_children():
            if isinstance(widget, tk.Label) and getattr(widget, "is_bg", False):
                widget.destroy()

        if self.bg_photo:
            bg_label = tk.Label(self.content, image=self.bg_photo)
            bg_label.is_bg = True
            bg_label.place(relx=0, rely=0, relwidth=1, relheight=1)
            bg_label.lower()
        else:
            self.content.configure(bg="#f1f5f9")

    # ---------------- Sidebar ----------------
    def create_sidebar(self):
        tk.Label(
            self.sidebar, text="Admission\nSimulator", fg="white", bg="#1e293b",
            font=("Helvetica", 18, "bold"), pady=20
        ).pack()

        buttons = [
            ("🏠 Home", self.show_home),
            ("🧩 Filters", self.show_filters),
            ("📊 Visualizations", self.show_visualizations),
            ("📋 Data Table", self.show_table)
        ]
        for text, cmd in buttons:
            tk.Button(
                self.sidebar, text=text, command=cmd,
                bg="#334155", fg="white", font=("Helvetica", 14),
                bd=0, relief="flat", pady=10
            ).pack(fill="x", padx=10, pady=5)

    # ---------------- Home Page ----------------
    def show_home(self):
        self.clear_content()
        self.set_page_background()

        overlay = tk.Frame(self.content, bg="#ffffff", bd=0)
        overlay.place(relx=0.3, rely=0.3, relwidth=0.4, relheight=0.3)

        tk.Label(
            overlay, text="🎓 Admission Database Simulator", bg="#ffffff",
            font=("Helvetica", 18, "bold"), fg="#1e293b"
        ).pack(pady=20)

        tk.Button(
            overlay, text="Upload CSV / Excel", command=self.upload_file,
            bg="#3b82f6", fg="white", font=("Helvetica", 14, "bold"),
            relief="flat", padx=20, pady=10
        ).pack(pady=10)

    # ---------------- Filters Page ----------------
    def show_filters(self):
        self.clear_content()
        self.set_page_background()

        tk.Label(
            self.content, text="Filter Applicants",
            font=("Helvetica", 20, "bold"), bg="#f1f5f9"
        ).pack(pady=30)

        frame = tk.Frame(self.content, bg="#f1f5f9")
        frame.pack(pady=20)

        tk.Label(frame, text="Course:", font=("Helvetica", 14), bg="#f1f5f9").grid(row=0, column=0, padx=10, pady=10)
        tk.Label(frame, text="Admission Status:", font=("Helvetica", 14), bg="#f1f5f9").grid(row=0, column=2, padx=10, pady=10)

        self.course_var = tk.StringVar()
        self.status_var = tk.StringVar()

        self.course_dropdown = ttk.Combobox(frame, textvariable=self.course_var, state="readonly", width=20, font=("Helvetica", 12))
        self.status_dropdown = ttk.Combobox(frame, textvariable=self.status_var, state="readonly", width=20, font=("Helvetica", 12))

        self.course_dropdown.grid(row=0, column=1, padx=10)
        self.status_dropdown.grid(row=0, column=3, padx=10)

        tk.Button(
            self.content, text="Apply Filters", command=self.apply_filters_and_show,
            bg="#3b82f6", fg="white", font=("Helvetica", 14, "bold"),
            relief="flat", padx=20, pady=10
        ).pack(pady=20)

        if self.df is not None:
            self.populate_filters()

    # ---------------- Visualization Page ----------------
    def show_visualizations(self):
        self.clear_content()
        self.set_page_background()

        if self.filtered_df is None or self.filtered_df.empty:
            tk.Label(
                self.content, text="No data loaded!",
                font=("Helvetica", 16), bg="#f1f5f9", fg="#ef4444"
            ).pack(pady=30)
            return

        tk.Label(
            self.content, text="📊 Data Visualizations",
            font=("Helvetica", 20, "bold"), bg="#f1f5f9"
        ).pack(pady=20)

        chart_frame = tk.Frame(self.content, bg="#f1f5f9")
        chart_frame.pack(expand=True, fill="both")

        bar_frame = tk.LabelFrame(chart_frame, text="Bar Chart", bg="white")
        pie_frame = tk.LabelFrame(chart_frame, text="Pie Chart", bg="white")
        line_frame = tk.LabelFrame(chart_frame, text="Line Chart", bg="white")

        bar_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        pie_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        line_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        chart_frame.grid_rowconfigure(0, weight=1)
        chart_frame.grid_rowconfigure(1, weight=1)
        chart_frame.grid_columnconfigure(0, weight=1)
        chart_frame.grid_columnconfigure(1, weight=1)

        plot_chart(self.filtered_df, bar_frame, "Bar Chart")
        plot_chart(self.filtered_df, pie_frame, "Pie Chart")
        plot_chart(self.filtered_df, line_frame, "Line Chart")

    # ---------------- Table Page ----------------
    def show_table(self):
        self.clear_content()
        self.set_page_background()

        if self.filtered_df is None or self.filtered_df.empty:
            tk.Label(
                self.content, text="No data to display!",
                font=("Helvetica", 16), bg="#f1f5f9", fg="#ef4444"
            ).pack(pady=30)
            return

        tree = ttk.Treeview(self.content)
        tree.pack(fill="both", expand=True, padx=20, pady=20)

        tree["columns"] = list(self.filtered_df.columns)
        tree["show"] = "headings"

        for col in self.filtered_df.columns:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=120)

        for _, row in self.filtered_df.iterrows():
            tree.insert("", "end", values=list(row))

    # ---------------- Actions ----------------
    def upload_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xls *.xlsx")])
        if not file_path:
            return
        try:
            self.df = load_data(file_path)
            self.filtered_df = self.df.copy()

            # ✅ Auto-update filters if already visible
            if hasattr(self, "course_dropdown") and hasattr(self, "status_dropdown"):
                self.populate_filters()

            messagebox.showinfo("Success", "File loaded successfully!")
            self.show_visualizations()
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def populate_filters(self):
        options = get_unique_options(self.df)
        self.course_dropdown["values"] = [""] + options.get("Course", [])
        self.status_dropdown["values"] = [""] + options.get("Admission Status", [])
        self.course_dropdown.current(0)
        self.status_dropdown.current(0)

    def apply_filters_and_show(self):
        course = self.course_var.get()
        status = self.status_var.get()
        self.filtered_df = apply_filters(self.df, course, status)
        self.show_visualizations()

    def clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()


# ==========================================================
#                      RUN APPLICATION
# ==========================================================
if __name__ == "__main__":
    root = tk.Tk()
    app = AdmissionDbSimulator(root)
    root.mainloop()
