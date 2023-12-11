import customtkinter
import sys
import os
import threading
import server

customtkinter.set_appearance_mode("Light")
customtkinter.set_default_color_theme("dark-blue")

server_run=server.Server()

class server_GUI():
    def __init__(self):
        self.root = customtkinter.CTk()
        self.root.title("ThongQuan Ass1 ComNet")
        self.root.geometry("500x400")
        self.frame=customtkinter.CTkFrame(master=self.root, fg_color="transparent")
        self.frame.pack(pady=0, padx=0, fill="both", expand=True)
        self.frame.grid_columnconfigure((0, 1), weight=1)
        
        self.output = customtkinter.CTkTextbox(master=self.frame, width=450, height=150, state="disabled", scrollbar_button_color="#000")
        self.output.grid(row=3, column=0, pady=12, padx=10, columnspan=2)
        
    def start(self):
        self.thread = threading.Thread(target=server_run.start)
        self.thread.start()
        self.body()
        self.root.mainloop()
            
    def exit_sys(self):
        server_run.stop()
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
    
    def body(self):
        
        self.title = customtkinter.CTkLabel(master=self.frame, text="Server UI", font=("Roboto",26), justify="center", text_color=["#3a7ebf", "#1f538d"])
        self.title.grid(row=0, column=0, pady=12, padx=10, columnspan=2)

        self.discover_entry = customtkinter.CTkEntry(master=self.frame, placeholder_text="Please enter hostname", width=300)
        self.discover_entry.grid(row=1, column=0, pady=12, padx=10)

        self.discover_button = customtkinter.CTkButton(master=self.frame, text="DISCOVER", command=lambda: getattr(server_run, '_Server__discover')(self.discover_entry.get()), width=100)
        self.discover_button.grid(row=1, column=1, pady=12, padx=10)

        self.ping_entry=customtkinter.CTkEntry(master=self.frame, placeholder_text="Please enter hostname", width=300)
        self.ping_entry.grid(row=2, column=0, pady=12, padx=10)

        self.ping_button=customtkinter.CTkButton(master=self.frame, text="PING", command=lambda: getattr(server_run, '_Server__ping')(self.ping_entry.get()), width=100)
        self.ping_button.grid(row=2, column=1, pady=12, padx=10)
        
        self.exit_button = customtkinter.CTkButton(master=self.frame, text="EXIT", command=lambda: self.exit_sys(), width=80, fg_color="red")
        self.exit_button.grid(row=4, column=0, pady=12, padx=10, columnspan=2)
        

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
GUI_run=server_GUI()
GUI_run.start()

# def discover():
#     value=discover_entry.get()
#     print("DICOVER: ", value)
#     # output.configure(state="normal")
#     # value=discover_entry.get()
#     # output.insert("end","DISCOVER: %s\n"%value)
#     # output.configure(state="disabled")
    
# def ping():
#     output.configure(state="normal")
#     value=ping_entry.get()
#     output.insert("end","PING: %s\n"%value)
#     output.configure(state="disabled")