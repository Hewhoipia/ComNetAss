import customtkinter
import sys
import os
import threading
import client

customtkinter.set_appearance_mode("Light")
customtkinter.set_default_color_theme("green")

client_run=client.Client()

class client_GUI():
    def __init__(self):
        self.root = customtkinter.CTk()
        self.root.title("ThongQuan Ass1 ComNet")
        self.root.geometry("500x400")
        self.frame=customtkinter.CTkFrame(master=self.root, fg_color="transparent")
        self.frame.pack(pady=0, padx=0, fill="both", expand=True)
        self.frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        self.output = customtkinter.CTkTextbox(master=self.frame, width=400, height=150, state="disabled", scrollbar_button_color="#000")
        self.output.grid(row=3, column=0, pady=12, padx=10, columnspan=3)
        
    def start(self):
        self.thread = threading.Thread(target=client_run.start)
        self.thread.start()
        self.body()
        self.root.mainloop()
            
    def exit_sys(self):
        client_run.stop()
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
            
    def handle_fetch(self, index):
        client_run.choose_file_to_fetch=self.fetch_entry2.get()
        client_run.fetch(self.fetch_entry1.get())
    
    def body(self):
        
        self.title = customtkinter.CTkLabel(master=self.frame, text="Client UI", font=("Roboto",26), justify="center", text_color=["#2CC985", "#2FA572"])
        self.title.grid(row=0, column=0, pady=12, padx=10, columnspan=3)

        self.publish_entry1 = customtkinter.CTkEntry(master=self.frame, placeholder_text="Please enter lname", width=150)
        self.publish_entry1.grid(row=1, column=0, pady=12, padx=10)
        
        self.publish_entry2 = customtkinter.CTkEntry(master=self.frame, placeholder_text="Please enter fname", width=150)
        self.publish_entry2.grid(row=1, column=1, pady=12, padx=10)

        self.publish_button = customtkinter.CTkButton(master=self.frame, text="PUBLISH", command=lambda: client_run.publish(self.publish_entry1.get(),self.publish_entry2.get()), width=100)
        self.publish_button.grid(row=1, column=2, pady=12, padx=10)

        self.fetch_entry1=customtkinter.CTkEntry(master=self.frame, placeholder_text="Please enter fname", width=150)
        self.fetch_entry1.grid(row=2, column=0, pady=12, padx=10)
        
        self.fetch_entry2=customtkinter.CTkEntry(master=self.frame, placeholder_text="Please enter host number", width=150)
        self.fetch_entry2.grid(row=2, column=1, pady=12, padx=10)

        self.fetch_button=customtkinter.CTkButton(master=self.frame, text="FETCH", command=self.handle_fetch(self.fetch_entry2.get()), width=100)
        self.fetch_button.grid(row=2, column=2, pady=12, padx=10)
        
        self.exit_button = customtkinter.CTkButton(master=self.frame, text="EXIT", command=lambda: self.exit_sys(), width=80, fg_color="red")
        self.exit_button.grid(row=4, column=0, pady=12, padx=10, columnspan=3)

class PrintRedirector:
    def __init__(self):
        pass

    def write(self, message):
        GUI_run.output.configure(state="normal")
        GUI_run.output.insert("end", message)
        GUI_run.output.see("end")
        #self.text_content.see(tk.END)  # Auto-scroll to the end
        GUI_run.output.configure(state="disabled")
        
    def flush(self):
        pass
    
sys.stdout = PrintRedirector()
GUI_run=client_GUI()
GUI_run.start()
    