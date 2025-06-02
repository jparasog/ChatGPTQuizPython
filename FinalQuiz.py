#import serial
import openai
import tkinter as tk
from tkinter import ttk

#ser = serial.Serial('COM3', 115200)
openai.api_key = "YOUR API KEY"

questions = []
current_question_index = 0
score = 0
asked_questions = set()

def generate_question():
    for _ in range(10):
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Generate a simple yes/no question in English about technology, suitable for students up to 18 years old, with a clear correct answer. Return the format: 'Question: <question> | Answer: <yes/no>'. Ensure the question is unique and not in: " + ", ".join(asked_questions) + "."},
                {"role": "user", "content": "Generate a simple yes/no question."}
            ]
        )
        result = response.choices[0].message["content"].strip()
        question, answer = result.split(" | ")
        question = question.replace("Question: ", "")
        answer = answer.replace("Answer: ", "")
        if question not in asked_questions:
            asked_questions.add(question)
            return question, answer
    return "Is this a default question?", "yes"

for _ in range(5):
    questions.append(generate_question())

root=tk.Tk()
root.title("Micro:bit Yes/No Quiz")
root.geometry("500x250")
root.configure(bg="#A1B5D8")

style=ttk.Style()
style.configure("Custom.TLabel",background="#A1B5D8")

question_label_part1 = ttk.Label(root, text="Waiting for first question...",style="Custom.TLabel", font=("Arial", 14))
question_label_part1.pack(pady=5)

question_label_part2 = ttk.Label(root, text="",style="Custom.TLabel", font=("Arial", 14))
question_label_part2.pack(pady=5)

score_label = ttk.Label(root, text="Score: 0/0",style="Custom.TLabel", font=("Arial", 12))
score_label.pack(pady=10)

button_frame = ttk.Frame(root,style="Custom.TLabel")
button_frame.pack(pady=10)

restart_button = ttk.Button(root, text="Restart", command=lambda: restart_quiz())
restart_button.pack(pady=10)
restart_button.pack_forget()

def split_question(question, max_length=20):
    if len(question) <= max_length:
        return question, ""
    split_index = question.rfind(" ", 0, max_length) or max_length
    return question[:split_index], question[split_index:].strip()

def answer_question(user_answer):
    global current_question_index, score
    if current_question_index < len(questions):
        correct_answer = questions[current_question_index][1]
        # Convert both answers to lowercase for case-insensitive comparison
        user_answer_lower = user_answer.lower()
        correct_answer_lower = correct_answer.lower()
        # Ask ChatGPT to compare the answers (case-insensitive)
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Compare the user's answer to the correct answer and return 'Correct!' if they match, or 'Wrong!' if they don't."},
                {"role": "user", "content": f"Correct answer: {correct_answer_lower}, User answer: {user_answer_lower}"}
            ]
        )
        result = response.choices[0].message["content"].strip()
        # Print the question, user's answer, and correct answer to verify (using original case)
        print(f"Question: {questions[current_question_index][0]} | User's Answer: {user_answer} | Correct Answer: {correct_answer} | Result: {result}")
        result_to_send = "1" if result == "Correct!" else "2"
 #       ser.write(f"{result_to_send}#".encode())
        if result == "Correct!":
            score += 1
        current_question_index += 1
        update_question()

true_button = ttk.Button(button_frame, text="True", command=lambda: answer_question("yes"))
true_button.pack(side=tk.LEFT, padx=10)

false_button = ttk.Button(button_frame, text="False", command=lambda: answer_question("no"))
false_button.pack(side=tk.LEFT, padx=10)

def restart_quiz():
    global questions, current_question_index, score
    questions = []
    current_question_index = 0
    score = 0
    for _ in range(5):
        questions.append(generate_question())
    true_button.pack(side=tk.LEFT, padx=10)
    false_button.pack(side=tk.LEFT, padx=10)
    restart_button.pack_forget()
    update_question()

def update_question():
    global current_question_index, score
    if current_question_index < len(questions):
        question = questions[current_question_index][0]
        part1, part2 = split_question(question)
        question_label_part1.config(text=f"Question: {part1}")
        question_label_part2.config(text=part2)
        score_label.config(text=f"Score: {score}/{current_question_index}")
    else:
        question_label_part1.config(text="Quiz Over!")
        question_label_part2.config(text="")
        score_label.config(text=f"Final Score: {score}/5")
        true_button.pack_forget()
        false_button.pack_forget()
        restart_button.pack()
    root.update()

update_question()
root.mainloop()