import tkinter as tk
from tkinter import ttk, messagebox
from ttkbootstrap import Style
import sys
import os

# Global variables
word_sets = []
set_menu = None

selected_set_name = None
selected_set = []
flashcards_selected_set = []
quiz_selected_set = []

flashcards_original_selected_set = None
quiz_original_selected_set = None

current_flashcards_word = 0
current_quiz_word = 0

flashcards_remembered_words = []
flashcards_non_remembered_words = []

quiz_remembered_words = []
quiz_non_remembered_words = []

is_flipped = False


def main():
    global root
    root = tk.Tk()
    root.title("FLASHCARDS APP")
    center_window(root, 600, 600)

    style = Style(theme="superhero")

    global selected_set_name, selected_set, flashcards_selected_set, quiz_selected_set
    selected_set_name = tk.StringVar()

    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True)

    word_sets_frame = create_word_sets_frame(notebook, style)
    notebook.add(word_sets_frame, text="Word sets")

    flashcards_frame, flashcards_canvas, flashcards_text = create_flashcards_frame(notebook, style)
    notebook.add(flashcards_frame, text="Flashcards")

    quiz_frame, quiz_canvas, quiz_text = create_quiz_frame(notebook, style)
    notebook.add(quiz_frame, text="Quiz")

    root.mainloop()


def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    x_coordinate = int((screen_width - width) / 2)
    y_coordinate = int((screen_height - height) / 2)

    window.geometry(f"{width}x{height}+{x_coordinate}+{y_coordinate}")


def read_set_names():
    try:
        with open("word_set_names.csv", "r") as file:
            set_names = file.read().strip().split(',')
            set_names_without_extension = []
            for name in set_names:
                set_names_without_extension.append(name.replace('.csv', ''))
        return set_names_without_extension
    except FileNotFoundError:
        print("File with set names doesn't exist.")
        return []


def read_set(set_name):
    word_list = []
    try:
        with open(set_name + ".csv", "r") as file:
            for line in file:
                eng_word, pl_word = line.rstrip().split(",")
                word = {"ENG": eng_word, "PL": pl_word}
                word_list.append(word)
        return word_list
    except FileNotFoundError:
        sys.exit("File doesn't exist")


def add_word_set():
    custom_dialog = tk.Toplevel(root)
    custom_dialog.title("Add Set")
    center_window(custom_dialog, 400, 200)

    label = ttk.Label(custom_dialog, text="Enter the name for the new set:")
    label.pack(pady=10)

    new_set_name_var = tk.StringVar()
    entry = ttk.Entry(custom_dialog, textvariable=new_set_name_var)
    entry.pack(pady=10)

    def save_and_close():
        global word_sets
        new_set_name = new_set_name_var.get()
        if new_set_name:
            try:
                with open("word_set_names.csv", "a") as file:
                    if file.tell() == 0:
                        file.write(f"{new_set_name}.csv")
                    else:
                        file.write(f",{new_set_name}.csv")
                    word_sets.append(new_set_name)
                    update_word_sets_menu()
                with open(new_set_name + ".csv", "x"):
                    pass
                custom_dialog.destroy()
                ask_for_translations(new_set_name)
            except FileExistsError:
                messagebox.showwarning("Warning", f"Set '{new_set_name}' already exists.")

    button_frame = ttk.Frame(custom_dialog)
    button_frame.pack(pady=10)

    save_button = ttk.Button(button_frame, text="OK", command=save_and_close)
    save_button.pack(side="left", padx=10)

    cancel_button = ttk.Button(button_frame, text="Cancel", command=custom_dialog.destroy)
    cancel_button.pack(side="right", padx=10)

    entry.focus_set()
    root.wait_window(custom_dialog)


####################################################################################################################
####################################SHARED FUNCS####################################################################
####################################################################################################################

def display_canvas(selected_type, set, current_word):
    global flaschards_canvas, flashcards_canvas_text, is_flipped
    global quiz_canvas, quiz_canvas_text

    if set and 0 <= current_word < len(set):
        word_pair = set[current_word]
        if selected_type == "flashcards":
            if is_flipped:
                text_to_show = word_pair["PL"]
            else:
                text_to_show = word_pair["ENG"]
            flaschards_canvas.itemconfig(flashcards_canvas_text, text=text_to_show)
        elif selected_type == "quiz":
            quiz_canvas.itemconfig(quiz_canvas_text, text=word_pair["ENG"])


def refresh_canvas(selected_type):
    global flashcards_selected_set, current_flashcards_word, flashcards_remembered_words, flashcards_non_remembered_words, is_flipped
    global quiz_selected_set, current_quiz_word, quiz_remembered_words, quiz_non_remembered_words
    if selected_type == "flashcards" and flashcards_selected_set:
        current_flashcards_word = 0
        flashcards_remembered_words = []
        flashcards_non_remembered_words = []
        is_flipped = False
        display_canvas("flashcards", flashcards_selected_set, current_flashcards_word)
    elif selected_type == "quiz" and quiz_selected_set:
        current_quiz_word = 0
        quiz_remembered_words = []
        quiz_non_remembered_words = []
        display_canvas("quiz", quiz_selected_set, current_quiz_word)


def reset_canvas(selected_type):
    global flashcards_selected_set, flashcards_original_selected_set
    global quiz_selected_set, quiz_original_selected_set
    if selected_type == "flashcards" and flashcards_original_selected_set:
        flashcards_selected_set = list(flashcards_original_selected_set)
        refresh_canvas("flashcards")
    elif selected_type == "quiz" and quiz_original_selected_set:
        quiz_selected_set = list(quiz_original_selected_set)
        refresh_canvas("quiz")


def remember_word(selected_type, current_word, set, rememberd_words):
    global current_flashcards_word, flashcards_selected_set, flashcards_remembered_words, flashcards_non_remembered_words
    global current_quiz_word, quiz_selected_set, quiz_remembered_words, quiz_non_remembered_words
    if set and 0 <= current_word < len(set):
        word_pair = set[current_word]
        rememberd_words.append(word_pair)
        current_word += 1
        if current_word < len(set):
            if selected_type == "flashcards":
                current_flashcards_word += 1
            elif selected_type == "quiz":
                current_quiz_word += 1
            display_canvas(selected_type, set, current_word)
        else:
            if selected_type == "flashcards":
                end_of_set_popup(selected_type, flashcards_non_remembered_words)
            elif selected_type == "quiz":
                end_of_set_popup(selected_type, quiz_non_remembered_words)


def not_remember_word(selected_type, current_word, set, non_rememberd_words):
    global current_flashcards_word, flashcards_selected_set
    global current_quiz_word, quiz_selected_set

    if set and 0 <= current_word < len(set):
        word_pair = set[current_word]
        non_rememberd_words.append(word_pair)
        current_word += 1
        if current_word < len(set):
            if selected_type == "flashcards":
                current_flashcards_word += 1
                display_canvas("flashcards", flashcards_selected_set, current_flashcards_word)
            elif selected_type == "quiz":
                current_quiz_word += 1
                display_canvas("quiz", quiz_selected_set, current_quiz_word)
        else:
            end_of_set_popup(selected_type, non_rememberd_words)


def end_of_set_popup(selected_type, non_remembered_words):
    def close_popup():
        end_popup.destroy()

    def on_change_set_click():
        if selected_type == "flashcards":
            change_set_to_non_remembered("flashcards")
        elif selected_type == "quiz":
            change_set_to_non_remembered("quiz")
        close_popup()

    end_popup = tk.Toplevel(root)
    end_popup.title("End of Set")
    center_window(end_popup, 350, 150)

    if non_remembered_words:
        end_label = ttk.Label(end_popup, text="You have reached the end of the set.")
        end_label.pack(pady=10)
        change_set_button = ttk.Button(end_popup, text="Change set to non-remembered words",
                                       command=on_change_set_click)
        change_set_button.pack(pady=5)

        reset_button = ttk.Button(end_popup, text="No thanks", command=close_popup)
        reset_button.pack(pady=5)
    else:
        congrats_label = ttk.Label(end_popup, text="Congratulations!")
        congrats_label.pack(pady=10)
        congrats_label = ttk.Label(end_popup, text="You got through the whole set with a knowledge of 100%!")
        congrats_label.pack(pady=10)
        close_button = ttk.Button(end_popup, text="Close", command=close_popup)
        close_button.pack(pady=5)

    end_popup.protocol("WM_DELETE_WINDOW", close_popup)


def change_set_to_non_remembered(selected_type):
    global selected_set_name, flashcards_non_remembered_words, flashcards_selected_set
    global quiz_non_remembered_words, quiz_selected_set

    if selected_type == "flashcards" and flashcards_non_remembered_words:
        helper_set = list(flashcards_non_remembered_words)
        flashcards_selected_set = helper_set
        refresh_canvas("flashcards")
    elif selected_type == "quiz" and quiz_non_remembered_words:
        helper_set = list(quiz_non_remembered_words)
        quiz_selected_set = helper_set
        refresh_canvas("quiz")
    else:
        messagebox.showinfo("No Non-Remembered Words", "There are no non-remembered words to set as a new set.")


def end_section(selected_type):
    global current_flashcards_word, flashcards_selected_set, flashcards_non_remembered_words, flashcards_remembered_words, flaschards_canvas
    global current_quiz_word, quiz_selected_set, quiz_non_remembered_words, quiz_remembered_words

    if selected_type == "flashcards":
        flaschards_canvas.itemconfig(flashcards_canvas_text, text="CHOOSE SET")
        flashcards_remembered_words = []
        flashcards_non_remembered_words = []
        flashcards_selected_set = None
        current_flashcards_word = None
    elif selected_type == "quiz":
        quiz_canvas.itemconfig(quiz_canvas_text, text="CHOOSE SET")
        quiz_remembered_words = []
        quiz_non_remembered_words = []
        quiz_selected_set = None
        current_quiz_word = None
    else:
        messagebox.showinfo("Invalid Type", "The selected type is not valid. Please choose 'quiz' or 'flashcards'.")


####################################################################################################################
####################################################################################################################
####################################################################################################################

def create_word_sets_frame(notebook, style):
    global selected_set_name, word_sets, set_menu

    word_sets_frame = ttk.Frame(notebook)

    set_label = ttk.Label(word_sets_frame, text="CHOOSE SET", font=("Arial", 20)).pack(pady=50)

    style.configure("TMenubutton", width=30, height=20)

    default_title = "AVAILABLE SETS"
    selected_set_name.set(default_title)
    set_menu = ttk.OptionMenu(word_sets_frame, selected_set_name, default_title, *word_sets, command=on_set_selected)
    set_menu.pack(pady=10)

    update_word_sets_menu()

    center_set_menu_frame = ttk.Frame(word_sets_frame)
    center_set_menu_frame.pack(pady=50)

    add_set_button = ttk.Button(center_set_menu_frame, text="ADD", command=add_word_set)
    add_set_button.pack(side="left", padx=5)
    delete_set_button = ttk.Button(center_set_menu_frame, text="DELETE", command=delete_selected_set)

    delete_set_button.pack(side="left", padx=5)

    return word_sets_frame


def on_set_selected(set_name):
    global selected_set_name, selected_set, flashcards_selected_set, flashcards_original_selected_set
    global quiz_selected_set, quiz_original_selected_set

    selected_set_name.set(set_name)
    selected_set = read_set(set_name)
    flashcards_selected_set = selected_set
    quiz_selected_set = selected_set
    flashcards_original_selected_set = list(selected_set)
    quiz_original_selected_set = list(selected_set)
    refresh_canvas("flashcards")
    refresh_canvas("quiz")


def update_word_sets_menu():
    global word_sets
    menu = set_menu['menu']
    menu.delete(0, 'end')
    for set_name in word_sets:
        if set_name.strip():
            menu.add_command(label=set_name, command=lambda s=set_name: on_set_selected(s))


def ask_for_translations(set_name):
    new_word_dialog = tk.Toplevel(root)
    new_word_dialog.title("Add Word to Set")
    center_window(new_word_dialog, 300, 300)

    eng_var = tk.StringVar()
    pl_var = tk.StringVar()

    eng_label = ttk.Label(new_word_dialog, text="Enter English word:")
    eng_label.pack(pady=10)
    eng_entry = ttk.Entry(new_word_dialog, textvariable=eng_var)
    eng_entry.pack(pady=10)

    pl_label = ttk.Label(new_word_dialog, text="Enter Polish translation:")
    pl_label.pack(pady=10)
    pl_entry = ttk.Entry(new_word_dialog, textvariable=pl_var)
    pl_entry.pack(pady=10)

    def save_and_next():
        nonlocal set_name
        eng_word = eng_var.get()
        pl_word = pl_var.get()
        if eng_word and pl_word:
            try:
                with open(f"{set_name}.csv", "a") as file:
                    file.write(f"{eng_word},{pl_word}\n")
                eng_var.set("")
                pl_var.set("")
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {str(e)}")
        else:
            messagebox.showwarning("Warning", "This pair wasn't saved.")

    def save_and_close():
        save_and_next()
        new_word_dialog.destroy()

    next_button = ttk.Button(new_word_dialog, text="Next Word", command=save_and_next)
    next_button.pack(side="right", padx=10)

    save_button = ttk.Button(new_word_dialog, text="Save Set", command=save_and_close)
    save_button.pack(side="left", padx=10)

    new_word_dialog.protocol("WM_DELETE_WINDOW", save_and_close)


def delete_selected_set():
    global selected_set_name
    set_name = selected_set_name.get()
    if set_name:
        try:
            os.remove(f"{set_name}.csv")
            word_sets.remove(set_name)
            update_word_sets_menu()
            with open("word_set_names.csv", "w") as file:
                file.write(','.join(word_sets))
            selected_set_name.set("")
            end_section("flashcards")
            end_section("quiz")
        except FileNotFoundError:
            messagebox.showerror("Error", f"Set '{set_name}' not found.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")


####################################################################################################################
####################################################################################################################
####################################################################################################################

def create_flashcards_frame(notebook, style):
    global flaschards_canvas, flashcards_canvas_text, flashcards_selected_set, current_flashcards_word, flashcards_non_remembered_words, is_flipped
    flashcards_frame = ttk.Frame(notebook)

    center_flashcards_frame_upper_buttons = ttk.Frame(flashcards_frame)
    center_flashcards_frame_upper_buttons.pack(pady=25)

    reset_flashcards_button = ttk.Button(center_flashcards_frame_upper_buttons, text="RESET",
                                         command=lambda: reset_canvas("flashcards"))
    reset_flashcards_button.pack(side="left", padx=70)

    flip_flashcards_button = ttk.Button(center_flashcards_frame_upper_buttons, text="FLIP", command=flip_flashcards)
    flip_flashcards_button.pack(side="left", padx=70)

    end_flashcards_button = ttk.Button(center_flashcards_frame_upper_buttons, text="END",
                                       command=lambda: end_section("flashcards"))
    end_flashcards_button.pack(side="left", padx=70)

    flaschards_canvas = tk.Canvas(flashcards_frame, width=600, height=350)
    flaschards_canvas.create_rectangle(50, 0, 550, 350, fill="#4d99e7")
    flashcards_canvas_text = flaschards_canvas.create_text(300, 175, text="CHOOSE SET", tags="square_text",
                                                           font=("Arial", 24), fill="white")
    flaschards_canvas.pack(pady=5)

    center_flashcards_frame_lower_buttons = ttk.Frame(flashcards_frame)
    center_flashcards_frame_lower_buttons.pack(pady=25)

    remember_flashcards_button = ttk.Button(center_flashcards_frame_lower_buttons, text="REMEMBER",
                                            command=lambda: remember_word("flashcards", current_flashcards_word,
                                                                          flashcards_selected_set,
                                                                          flashcards_remembered_words))
    remember_flashcards_button.pack(side="left", padx=5)

    still_not_flashcards_button = ttk.Button(center_flashcards_frame_lower_buttons, text="STILL NOT",
                                             command=lambda: not_remember_word("flashcards", current_flashcards_word,
                                                                               flashcards_selected_set,
                                                                               flashcards_non_remembered_words))
    still_not_flashcards_button.pack(side="left", padx=5)

    refresh_canvas("flashcards")
    refresh_canvas("quiz")

    return flashcards_frame, flaschards_canvas, flashcards_canvas_text


def flip_flashcards():
    global is_flipped, flashcards_selected_set, current_flashcards_word
    if flashcards_selected_set and 0 <= current_flashcards_word < len(flashcards_selected_set):
        is_flipped = not is_flipped
        display_canvas("flashcards", flashcards_selected_set, current_flashcards_word)


#################################################################################################
######################################QUIZ#######################################################
#################################################################################################

def create_quiz_frame(notebook, style):
    global quiz_canvas, quiz_canvas_text, quiz_selected_set, current_quiz_word, quiz_non_remembered_words
    quiz_frame = ttk.Frame(notebook)

    center_quiz_frame_upper_buttons = ttk.Frame(quiz_frame)
    center_quiz_frame_upper_buttons.pack(pady=25)

    reset_quiz_button = ttk.Button(center_quiz_frame_upper_buttons, text="RESET", command=lambda: reset_canvas("quiz"))
    reset_quiz_button.pack(side="left", padx=110)

    end_quiz_button = ttk.Button(center_quiz_frame_upper_buttons, text="END", command=lambda: end_section("quiz"))
    end_quiz_button.pack(side="left", padx=110)

    canvas_frame = ttk.Frame(quiz_frame)
    canvas_frame.pack()

    quiz_canvas = tk.Canvas(canvas_frame, width=600, height=350)
    quiz_canvas.create_rectangle(50, 0, 550, 350, fill="#4d99e7")
    quiz_canvas_text = quiz_canvas.create_text(300, 175, text="CHOOSE SET", tags="square_text", font=("Arial", 24),
                                               fill="white")
    quiz_canvas.pack(pady=5)

    eng_var = tk.StringVar()
    translation_var = tk.StringVar()

    def wrong_translation_popup():
        wrong_popup = tk.Toplevel()
        wrong_popup.title("Wrong Translation")
        center_window(wrong_popup, 350, 150)

        congrats_label = ttk.Label(wrong_popup, text="Translation is incorrect.")
        congrats_label.pack(pady=30)
        close_button = ttk.Button(wrong_popup, text="Close", command=wrong_popup.destroy)
        close_button.pack(pady=10)

    def submit_translation():
        global current_quiz_word, quiz_selected_set, quiz_non_remembered_words

        translated_text = translation_var.get()
        if quiz_selected_set and 0 <= current_quiz_word < len(quiz_selected_set):
            word_pair = quiz_selected_set[current_quiz_word]
            if translated_text.lower() == word_pair["PL"].lower():
                remember_word("quiz", current_quiz_word, quiz_selected_set, quiz_remembered_words)
            else:
                wrong_translation_popup()
                end_of_set_popup("quiz", quiz_non_remembered_words)
        else:
            pass

    center_quiz_frame_lower_buttons = ttk.Frame(quiz_frame)
    center_quiz_frame_lower_buttons.pack()

    remember_quiz_button = ttk.Button(center_quiz_frame_lower_buttons, text="DONT KNOW",
                                      command=lambda: not_remember_word("quiz", current_quiz_word, quiz_selected_set,
                                                                        quiz_non_remembered_words))
    remember_quiz_button.pack(side="left", padx=5)

    translation_label = ttk.Label(center_quiz_frame_lower_buttons)
    translation_label.pack(side="left", pady=10)
    translation_entry = ttk.Entry(center_quiz_frame_lower_buttons, width=40, textvariable=translation_var)
    translation_entry.pack(side="left", pady=10)

    still_not_quiz_button = ttk.Button(center_quiz_frame_lower_buttons, text="SUBMIT", command=submit_translation)
    still_not_quiz_button.pack(side="left", padx=5)

    return quiz_frame, quiz_canvas, quiz_canvas_text


#################################################################################################
#################################################################################################
#################################################################################################


if __name__ == "__main__":
    word_sets.extend(read_set_names())
    main()
    print(selected_set)
