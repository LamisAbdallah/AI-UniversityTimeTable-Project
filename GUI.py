import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import json
import main  # Import the main scheduling logic (genetic_algorithm)


class UniversitySchedulerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("University Timetable Scheduler")
        self.root.geometry("800x800")  # Increased window size
        self.root.configure(bg="#e6f3ff")  # Light blue background

        # Colors
        self.bg_color = "#e6f3ff"
        self.header_color = "#4a6baf"
        self.lecture_color = "#e6f3ff"  # Light blue for lectures
        self.lab_color = "#ffe6e6"  # Light red for labs
        self.text_color = "#333333"
        self.accent_color = "#ff5733"  # Orange for plot

        # Styling
        self.style = ttk.Style()
        self.style.configure("TButton", font=("Arial", 12), padding=10)
        self.style.configure("TLabel", font=("Arial", 12), background=self.bg_color)
        self.style.configure("TEntry", font=("Arial", 12))

        # Data from main.py
        self.days = main.days
        self.time_slots = main.time_slots

        # Initialize data
        self.schedule_data = None
        self.fitness_history = None
        self.student_info = None
        self.best_fitness = None
        self.course_entries = []

        self.setup_ui()

    def setup_ui(self):
        # Main frame
        self.main_frame = ttk.Frame(self.root, padding=20)
        self.main_frame.pack(fill="both", expand=True)

        # Welcome question
        self.question_label = ttk.Label(
            self.main_frame,
            text="Do you want to enter your own courses?",
            font=("Arial", 16, "bold"),
            foreground="#003087"
        )
        self.question_label.pack(pady=10)

        # Yes/No buttons
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.pack(pady=10)
        ttk.Button(
            self.button_frame,
            text="Yes",
            command=self.show_course_count_form,
            style="TButton"
        ).pack(side="left", padx=10)
        ttk.Button(
            self.button_frame,
            text="No",
            command=self.show_student_form,
            style="TButton"
        ).pack(side="left", padx=10)

        # Course count form
        self.course_count_frame = ttk.Frame(self.main_frame)
        self.num_courses = tk.StringVar()
        ttk.Label(
            self.course_count_frame,
            text="How many courses do you want to enter?",
            foreground="#003087"
        ).grid(row=0, column=0, padx=5, pady=5, sticky="e")
        ttk.Entry(self.course_count_frame, textvariable=self.num_courses).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(
            self.course_count_frame,
            text="Next",
            command=self.show_course_input_form,
            style="TButton"
        ).grid(row=1, column=0, columnspan=2, pady=10)

        # Course input form
        self.course_input_frame = ttk.Frame(self.main_frame)

        # Student input form
        self.student_frame = ttk.Frame(self.main_frame)
        self.student_name = tk.StringVar()
        self.student_id = tk.StringVar()
        ttk.Label(
            self.student_frame,
            text="Student Name:",
            foreground="#003087"
        ).grid(row=0, column=0, padx=5, pady=5, sticky="e")
        ttk.Entry(self.student_frame, textvariable=self.student_name).grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(
            self.student_frame,
            text="Student ID:",
            foreground="#003087"
        ).grid(row=1, column=0, padx=5, pady=5, sticky="e")
        ttk.Entry(self.student_frame, textvariable=self.student_id).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(
            self.student_frame,
            text="Generate Schedule",
            command=self.generate_schedule,
            style="TButton"
        ).grid(row=2, column=0, columnspan=2, pady=20)

        # Result frame
        self.result_frame = ttk.Frame(self.main_frame)
        self.result_button_frame = ttk.Frame(self.result_frame)
        self.result_button_frame.pack(pady=10)
        ttk.Button(
            self.result_button_frame,
            text="Show Timetable",
            command=self.show_timetable,
            style="TButton"
        ).pack(side="left", padx=10)
        ttk.Button(
            self.result_button_frame,
            text="Show Fitness Plot",
            command=self.show_plot,
            style="TButton"
        ).pack(side="left", padx=10)

        # Timetable frame with scrollbars
        self.timetable_frame = ttk.Frame(self.result_frame)

        # Create a canvas and scrollbars
        self.table_canvas = tk.Canvas(self.timetable_frame, bg=self.bg_color)
        self.h_scroll = ttk.Scrollbar(self.timetable_frame, orient="horizontal", command=self.table_canvas.xview)
        self.v_scroll = ttk.Scrollbar(self.timetable_frame, orient="vertical", command=self.table_canvas.yview)

        # Configure the canvas
        self.table_canvas.configure(xscrollcommand=self.h_scroll.set, yscrollcommand=self.v_scroll.set)

        # Create a frame inside the canvas
        self.table_inner_frame = ttk.Frame(self.table_canvas, padding=5)
        self.table_inner_frame.bind(
            "<Configure>",
            lambda e: self.table_canvas.configure(
                scrollregion=self.table_canvas.bbox("all")
            )
        )

        # Add the inner frame to the canvas
        self.table_canvas.create_window((0, 0), window=self.table_inner_frame, anchor="nw")

        # Grid layout for the canvas and scrollbars
        self.table_canvas.grid(row=0, column=0, sticky="nsew")
        self.v_scroll.grid(row=0, column=1, sticky="ns")
        self.h_scroll.grid(row=1, column=0, sticky="ew")

        # Configure grid weights
        self.timetable_frame.grid_rowconfigure(0, weight=1)
        self.timetable_frame.grid_columnconfigure(0, weight=1)

        # Plot frame
        self.plot_frame = ttk.Frame(self.result_frame)
        self.figure = plt.Figure(figsize=(8, 5), dpi=100)  # Adjusted figure size
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.plot_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    def show_course_count_form(self):
        self.question_label.pack_forget()
        self.button_frame.pack_forget()
        self.course_count_frame.pack(pady=20)

    def show_course_input_form(self):
        try:
            num_courses = int(self.num_courses.get())
            if num_courses <= 0:
                raise ValueError("Number of courses must be positive.")
        except ValueError:
            messagebox.showwarning("Input Error", "Please enter a valid positive number of courses.")
            return

        self.course_count_frame.pack_forget()
        self.course_input_frame.pack(pady=20)

        for widget in self.course_input_frame.winfo_children():
            widget.destroy()
        self.course_entries = []

        for i in range(num_courses):
            ttk.Label(
                self.course_input_frame,
                text=f"Course {i + 1}",
                font=("Arial", 14, "bold"),
                foreground="#003087"
            ).grid(row=i * 4, column=0, columnspan=2, pady=10)
            ttk.Label(
                self.course_input_frame,
                text="Course Name:",
                foreground="#003087"
            ).grid(row=i * 4 + 1, column=0, padx=5, pady=5, sticky="e")
            course_name = tk.StringVar()
            ttk.Entry(self.course_input_frame, textvariable=course_name).grid(row=i * 4 + 1, column=1, padx=5, pady=5)
            ttk.Label(
                self.course_input_frame,
                text="Lecturer Name:",
                foreground="#003087"
            ).grid(row=i * 4 + 2, column=0, padx=5, pady=5, sticky="e")
            lecturer = tk.StringVar()
            ttk.Entry(self.course_input_frame, textvariable=lecturer).grid(row=i * 4 + 2, column=1, padx=5, pady=5)
            ttk.Label(
                self.course_input_frame,
                text="TA Name:",
                foreground="#003087"
            ).grid(row=i * 4 + 3, column=0, padx=5, pady=5, sticky="e")
            ta = tk.StringVar()
            ttk.Entry(self.course_input_frame, textvariable=ta).grid(row=i * 4 + 3, column=1, padx=5, pady=5)
            self.course_entries.append((course_name, lecturer, ta))

        button_frame = ttk.Frame(self.course_input_frame)
        button_frame.grid(row=num_courses * 4, column=0, columnspan=2, pady=20)
        ttk.Button(
            button_frame,
            text="Back",
            command=self.back_to_course_count,
            style="TButton"
        ).pack(side="left", padx=10)
        ttk.Button(
            button_frame,
            text="Next",
            command=self.show_student_form,
            style="TButton"
        ).pack(side="left", padx=10)

    def back_to_course_count(self):
        self.course_input_frame.pack_forget()
        self.course_count_frame.pack(pady=20)

    def show_student_form(self):
        courses = {}
        for course_name, lecturer, ta in self.course_entries:
            if not all([course_name.get().strip(), lecturer.get().strip(), ta.get().strip()]):
                messagebox.showwarning("Input Error", "Please fill in all course details.")
                return
            courses[course_name.get().strip()] = {
                "lectures": {"hours": 2, "lecturer": lecturer.get().strip()},
                "labs": {"hours": 1, "ta": ta.get().strip()}
            }

        if courses:
            try:
                with open("data.json", "w") as f:
                    json.dump(courses, f, indent=4)
            except Exception as e:
                messagebox.showerror("File Error", f"Failed to save course data: {e}")
                return

        self.course_input_frame.pack_forget()
        self.student_frame.pack(pady=20)

    def generate_schedule(self):
        student_name = self.student_name.get().strip()
        student_id = self.student_id.get().strip()

        if not student_name or not student_id:
            messagebox.showwarning("Input Error", "Please enter both Student Name and ID.")
            return

        self.student_frame.pack_forget()
        # Ensure the question and button frames are hidden
        self.question_label.pack_forget()
        self.button_frame.pack_forget()
        self.result_frame.pack(fill="both", expand=True, pady=20)
        self.student_info = (student_name, student_id)

        try:
            result = main.genetic_algorithm()
            if isinstance(result, tuple):
                self.schedule_data, self.fitness_history = result
                self.best_fitness = self.fitness_history[-1] if self.fitness_history else 0
            else:
                self.schedule_data = result
                self.fitness_history = None
                self.best_fitness = None
            self.show_timetable()
        except Exception as e:
            messagebox.showerror("Scheduling Error", f"Failed to generate schedule: {e}")

    def show_timetable(self):
        if not self.schedule_data:
            messagebox.showwarning("No Data", "Please generate a schedule first.")
            return

        self.plot_frame.pack_forget()
        self.timetable_frame.pack(fill="both", expand=True, pady=10)

        # Clear previous widgets
        for widget in self.table_inner_frame.winfo_children():
            widget.destroy()

        # Title
        ttk.Label(
            self.table_inner_frame,
            text="University Timetable Scheduler",
            font=("Arial", 16, "bold"),
            foreground="#003087"
        ).grid(row=0, column=0, columnspan=len(self.time_slots) + 1, pady=10)

        # Table headers
        headers = ["Day"] + self.time_slots
        for col, header in enumerate(headers):
            cell = tk.Frame(
                self.table_inner_frame,
                bg=self.header_color,
                relief=tk.RAISED,
                borderwidth=1,
                width=120,
                height=40
            )
            cell.grid(row=1, column=col, sticky="nsew", padx=2, pady=2)
            cell.grid_propagate(False)

            tk.Label(
                cell,
                text=header,
                bg=self.header_color,
                fg="white",
                font=("Arial", 10, "bold"),
                wraplength=110
            ).pack(expand=True, fill="both")

        # Table content
        for row, day in enumerate(self.days, 2):
            # Day cell
            day_cell = tk.Frame(
                self.table_inner_frame,
                bg=self.bg_color,
                relief=tk.GROOVE,
                borderwidth=1,
                width=120,
                height=60
            )
            day_cell.grid(row=row, column=0, sticky="nsew", padx=2, pady=2)
            day_cell.grid_propagate(False)

            tk.Label(
                day_cell,
                text=day,
                bg=self.bg_color,
                fg=self.text_color,
                font=("Arial", 10, "bold"),
                wraplength=110
            ).pack(expand=True, fill="both")

            # Time slot cells
            for col, slot in enumerate(self.time_slots, 1):
                class_info = None
                for lec in self.schedule_data:
                    if lec["day"] == day and lec["slot"] == slot:
                        class_info = lec
                        break

                cell_bg = self.bg_color
                if class_info:
                    cell_bg = self.lecture_color if class_info["type"] == "lecture" else self.lab_color

                cell = tk.Frame(
                    self.table_inner_frame,
                    bg=cell_bg,
                    relief=tk.GROOVE,
                    borderwidth=1,
                    width=120,
                    height=60
                )
                cell.grid(row=row, column=col, sticky="nsew", padx=2, pady=2)
                cell.grid_propagate(False)

                if class_info:
                    type_label = "Lec" if class_info["type"] == "lecture" else "Lab"
                    tk.Label(
                        cell,
                        text=f"{class_info['course']} ({type_label})",
                        bg=cell_bg,
                        fg=self.text_color,
                        font=("Arial", 9, "bold"),
                        wraplength=110
                    ).pack(pady=(2, 0))
                    tk.Label(
                        cell,
                        text=class_info["instructor"],
                        bg=cell_bg,
                        fg="#555555",
                        font=("Arial", 8),
                        wraplength=110
                    ).pack()
                    tk.Label(
                        cell,
                        text=class_info["room"],
                        bg=cell_bg,
                        fg="#777777",
                        font=("Arial", 8, "italic"),
                        wraplength=110
                    ).pack(pady=(0, 2))

        # Student info
        if self.student_info[0] and self.student_info[1]:
            ttk.Label(
                self.table_inner_frame,
                text=f"Schedule for {self.student_info[0]} (ID: {self.student_info[1]})",
                font=("Arial", 12),
                foreground="#003087"
            ).grid(row=len(self.days) + 2, column=0, columnspan=len(self.time_slots) + 1, pady=5)

        # Fitness info
        if self.best_fitness is not None:
            ttk.Label(
                self.table_inner_frame,
                text=f"Generation {len(self.fitness_history)} - Best Fitness: {self.best_fitness:.4f}",
                font=("Arial", 10),
                foreground="#003087"
            ).grid(row=len(self.days) + 3, column=0, columnspan=len(self.time_slots) + 1, pady=5)

        # Configure grid weights and minimum sizes
        for col in range(len(headers)):
            self.table_inner_frame.columnconfigure(col, weight=1, minsize=120)

        for row in range(len(self.days) + 3):
            self.table_inner_frame.rowconfigure(row, weight=1, minsize=60)

        # Update the canvas scroll region
        self.table_canvas.configure(scrollregion=self.table_canvas.bbox("all"))

    def show_plot(self):
        if not self.fitness_history:
            messagebox.showwarning("No Data", "Fitness data not available.")
            return

        self.timetable_frame.pack_forget()
        self.plot_frame.pack(fill="both", expand=True, pady=10)

        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.plot(self.fitness_history, marker="o", linestyle="-", color=self.accent_color)
        ax.set_title("Fitness Score Over Generations", fontsize=14, color="#003087")
        ax.set_xlabel("Generation", fontsize=12, color="#003087")
        ax.set_ylabel("Best Fitness Score", fontsize=12, color="#003087")
        ax.grid(True)
        ax.set_facecolor("#f0f8ff")
        self.figure.set_facecolor(self.bg_color)
        self.canvas.draw()


if __name__ == "__main__":
    root = tk.Tk()
    app = UniversitySchedulerGUI(root)
    root.mainloop()
