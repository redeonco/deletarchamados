import tkinter as tk
from tkinter import messagebox
import paramiko

# Variável global para armazenar a conexão SSH ativa
ssh_client = None

def attempt_login():
    """Tenta estabelecer conexão SSH com o host remoto usando as credenciais fornecidas."""
    global ssh_client
    user = login_user_entry.get().strip()
    pwd = login_password_entry.get().strip()
    host = "*********"  # Host fixo conforme a especificação

    if not user or not pwd:
        messagebox.showerror("Erro", "Por favor, informe usuário e senha.")
        return

    try:
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(hostname=host, username=user, password=pwd)
        
        messagebox.showinfo("Login", "Conexão SSH estabelecida com sucesso!")
        
        # Esconde a tela de login e mostra a tela principal para deleção de chamados
        login_frame.pack_forget()
        main_frame.pack(padx=10, pady=10, fill="both", expand=True)
    except Exception as e:
        messagebox.showerror("Erro no Login", f"Falha ao conectar via SSH:\n{e}")

def delete_ticket():
    """Executa o comando remoto para deletar o chamado informado."""
    if ssh_client is None:
        messagebox.showerror("Erro", "Conexão SSH não estabelecida.")
        return

    ticket_number = ticket_entry.get().strip()
    if not ticket_number:
        messagebox.showerror("Erro", "Por favor, informe o número do chamado.")
        return

    # Monta o comando remoto a ser executado
    command = (
        "docker exec -u otrs rede_onco-otrs_otrs_1 "
        "/opt/otrs/bin/otrs.Console.pl Maint::Ticket::Delete --ticket-number " + ticket_number
    )

    try:
        stdin, stdout, stderr = ssh_client.exec_command(command)
        out = stdout.read().decode("utf-8").strip()
        err = stderr.read().decode("utf-8").strip()

        if err:
            messagebox.showerror("Erro", f"Erro ao deletar o chamado:\n{err}")
        else:
            messagebox.showinfo("Sucesso", f"Chamado {ticket_number} deletado com sucesso!\n\nSaída:\n{out}")
    except Exception as e:
        messagebox.showerror("Erro", f"Falha na execução do comando:\n{e}")

def on_closing():
    """Fecha a conexão SSH ao fechar a aplicação."""
    global ssh_client
    if ssh_client:
        ssh_client.close()
    root.destroy()

# Configuração da janela principal
root = tk.Tk()
root.title("EXCLUIR CHAMADOS OTRS")
# Configura a cor de fundo da janela principal
root.configure(bg="#012e01")
# Define uma geometria para a janela principal (ajuste conforme necessário)
root.geometry("400x170")

# --- Frame de Login ---
# O frame de login herda o fundo da janela principal
login_frame = tk.Frame(root, padx=10, pady=10, bg=root["bg"])
login_frame.pack()

login_title = tk.Label(login_frame, text="Login SSH", font=("Helvetica", 14, "bold"), bg=root["bg"], fg="gray")
login_title.grid(row=0, column=0, columnspan=2, pady=(0, 10))

tk.Label(login_frame, text="Usuário:", font=("Helvetica", 10, "bold"),  bg=root["bg"], fg="gray").grid(row=1, column=0, sticky="e", pady=5)
login_user_entry = tk.Entry(login_frame, width=15)
login_user_entry.grid(row=1, column=1, pady=5)

tk.Label(login_frame, text="Senha:", font=("Helvetica", 10, "bold"), bg=root["bg"], fg="gray").grid(row=2, column=0, sticky="e", pady=5)
login_password_entry = tk.Entry(login_frame, show="*", width=15)
login_password_entry.grid(row=2, column=1, pady=5)

login_button = tk.Button(login_frame, text="Conectar", width=10, command=attempt_login)
login_button.grid(row=3, column=0, columnspan=2, pady=(10, 0))

# --- Frame Principal para Deleção de Chamados (inicialmente oculto) ---
# Define o fundo deste frame para a cor desejada (equivalente a rgba(36, 35, 35, 0.623))

main_frame = tk.Frame(root, padx=10, pady=10, bg="#242323")

main_title = tk.Label(main_frame, text="Deletar Chamado", font=("Helvetica", 14, "bold"), bg="#242323", fg="gray")
main_title.grid(row=0, column=0, columnspan=2, pady=(0, 10))

tk.Label(main_frame, text="Número do Chamado:" , font=("Helvetica", 10, "bold") , bg="#242323", fg="gray").grid(row=1, column=0, sticky="e", pady=5)
ticket_entry = tk.Entry(main_frame, width=30)
ticket_entry.grid(row=1, column=1, pady=5)

delete_button = tk.Button(main_frame, text="Deletar Chamado" , font=("Helvetica", 10, "bold"), width=20, command=delete_ticket)
delete_button.grid(row=2, column=0, columnspan=2, pady=(10, 0))

# Configura o fechamento da janela para garantir que a conexão SSH seja encerrada
root.protocol("WM_DELETE_WINDOW", on_closing)

root.mainloop()
