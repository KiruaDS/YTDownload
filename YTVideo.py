import customtkinter as ctk
import os
import sys
from PIL import Image
from pytubefix import YouTube
from pytubefix.cli import on_progress # Usaremos on_progress, mas precisamos de uma função de log que atualiza a GUI

# -----------------------------------------------------
# 1. FUNÇÕES DE LOG (LÓGICA DO log.py)
# -----------------------------------------------------
def exibir_log(textbox_widget, texto_log, tipo="INFO"):
    if tipo == "ERRO":
        cor = "red"
        prefixo = "[ERRO] "
    elif tipo == "SUCESSO":
        cor = "green"
        prefixo = "[OK] "
    else:
        cor = "#00FFFF" # Ciano para INFO
        prefixo = "[INFO] "

    # Permite a edição do texto
    textbox_widget.configure(state="normal")
    
    # Limpa o conteúdo anterior
    textbox_widget.delete("1.0", "end")

    # Insere a nova mensagem formatada
    mensagen_formatada = prefixo + texto_log
    textbox_widget.configure(text_color=cor)
    textbox_widget.insert("end", mensagen_formatada)

    # Bloqueia a edição novamente
    textbox_widget.configure(state="disabled")

    # Força a atualização da GUI para mostrar o log imediatamente
    textbox_widget.update()


# -----------------------------------------------------
# 2. FUNÇÃO DE CAMINHO (Para PyInstaller)
# -----------------------------------------------------
def resource_path(relative_path):
    try:
       # Se compilado, usa o caminho especial do PyInstaller
       base_path = sys._MEIPASS
    except Exception:
        # Se no modo dev, usa o caminho relativo normal
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


# -----------------------------------------------------
# 3. FUNÇÃO DE DOWNLOAD (LÓGICA DO main.py)
# -----------------------------------------------------

# Wrapper para usar o log da GUI com a função on_progress do pytubefix (opcional)
def progress_callback(stream, chunk, bytes_remaining):
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining
    percentage = (bytes_downloaded / total_size) * 100
    
    # Atualiza o log com a porcentagem
    status = f"Baixando: {percentage:.1f}% concluído."
    # Usaremos uma cor diferente para status de progresso
    log_textbox.configure(state="normal", text_color="yellow")
    log_textbox.delete("1.0", "end")
    log_textbox.insert("end", "[PROGRESSO] " + status)
    log_textbox.configure(state="disabled")
    log_textbox.update()


def baixar_video():
    link = slink.get()

    if not link:
        exibir_log(log_textbox, "Cade o link meu rei?", tipo="ERRO")
        return

    exibir_log(log_textbox, f"Iniciando download para: {link}", tipo="INFO")
    
    # Pasta de destino
    destino = resource_path("videos")
    os.makedirs(destino, exist_ok=True) # Garante que a pasta 'videos' exista ao lado do executável

    try:
        yt = YouTube(link, on_progress_callback=progress_callback)
        
        # Seleciona o stream (audio_only como no seu main.py original)
        ys = yt.streams.get_highest_resolution()

        if not ys:
             exibir_log(log_textbox, "Não foi possível encontrar o stream de áudio.", tipo="ERRO")
             return
             
        # Inicia o download
        ys.download(output_path=destino)
        
        # Limpa o campo de entrada e mostra sucesso
        exibir_log(log_textbox, f"Download concluído: {yt.title}\nSalvo em: {destino}", tipo="SUCESSO")
        slink.delete(0, 'end')

    except Exception as e:
        erro_msg = f"Erro no pytubefix/download: {e}"
        exibir_log(log_textbox, erro_msg, tipo="ERRO")


# -----------------------------------------------------
# 4. CONFIGURAÇÃO DA GUI (GUI PRINCIPAL)
# -----------------------------------------------------

# Variaveis globais
slink = None
log_textbox = None

# Configuração da janela
ctk.set_appearance_mode('dark')
app = ctk.CTk()
app.title('Baixar Vídeos do YouTube')
app.geometry('640x480')

# Carregamento da Imagem (usando resource_path)
caminho_imagen = "logo.png"
tamanho_imagen = (200, 100)
imagem_tk = None

try: 
    caminho_absoluto = resource_path(caminho_imagen)
    imagem_pil = Image.open(caminho_absoluto).resize(tamanho_imagen)
    imagem_tk = ctk.CTkImage(light_image=imagem_pil, dark_image=imagem_pil, size=tamanho_imagen)
except Exception:
   exibir_log(app, f"ERRO: Imagem '{caminho_imagen}' não encontrada.", tipo="ERRO") # Não podemos usar log_textbox aqui

# Layout da GUI
if imagem_tk:
   image_label = ctk.CTkLabel(app, image=imagem_tk, text="")
   image_label.pack(pady=(10, 10))

slink = ctk.CTkEntry(app, placeholder_text='coloque seu link aki!', width=350)
slink.pack(pady=(5, 10))

botao_baixar = ctk.CTkButton(app, text="Baixar", command=baixar_video)
botao_baixar.pack(pady=10)

# Inicialização do Log
log_textbox = ctk.CTkTextbox(app, width=500, height=180, wrap="word")
log_textbox.pack(pady=20, padx=20)
log_textbox.configure(text_color="lightgray")
log_textbox.insert("1.0", "Terminal de log. Aguardando link...")
log_textbox.configure(state="disabled")

# -----------------------------------------------------
# 5. INICIALIZAÇÃO
# -----------------------------------------------------
if __name__ == '__main__':
    # Garante que o diretório base para resource_path funcione corretamente no modo dev
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    app.mainloop()
