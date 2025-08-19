import subprocess
import sys
import re

def executar_comando_udata(subcomando=None):
    """
    Executa o comando 'udata' e captura a sua saída.
    """
    cmd = ['udata']
    if subcomando:
        cmd.append(subcomando)
    cmd.append('--help')

    try:
        resultado = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return resultado.stdout
    except (FileNotFoundError, subprocess.CalledProcessError) as e:
        print(f"Erro ao executar 'udata {subcomando if subcomando else ''}': {e}")
        return None

def formatar_para_markdown(texto):
    """
    Formata o texto de ajuda do udata em uma string Markdown.
    """
    markdown_output = []
    linhas = texto.split('\n')
    
    is_options = False
    is_commands = False
    
    for linha in linhas:
        linha_strip = linha.strip()
        
        if not linha_strip:
            continue

        if linha_strip.startswith('Usage:'):
            markdown_output.append(f'**`{linha_strip}`**\n')
            is_options = False
            is_commands = False
        elif linha_strip.startswith('Options:'):
            markdown_output.append(f'\n**`{linha_strip}`**\n')
            is_options = True
            is_commands = False
        elif linha_strip.startswith('Commands:'):
            markdown_output.append(f'\n**`{linha_strip}`**\n')
            is_options = False
            is_commands = True
        elif is_options or is_commands:
            # Formata as secções de opções e comandos como listas
            partes = linha.split(maxsplit=1)
            if len(partes) > 1:
                comando = partes[0].strip()
                descricao = partes[1].strip()
                markdown_output.append(f'* **`{comando}`** - {descricao}\n')
            else:
                markdown_output.append(f'* {linha_strip}\n')
        else:
            # Adiciona outras linhas como texto normal
            markdown_output.append(f'{linha}\n')
            
    return "".join(markdown_output)

def gerar_documentacao_completa():
    """
    Gera um ficheiro Markdown completo com a documentação do udata.
    """
    print("A gerar documentação para os comandos do udata...")
    
    saida_udata_geral = executar_comando_udata()
    if not saida_udata_geral:
        return
    
    subcomandos_encontrados = re.findall(r'^  (\w+)\s+.*', saida_udata_geral, re.MULTILINE)
    
    markdown_final = "# Documentação dos Comandos uData\n\n"
    markdown_final += "---" + "\n\n"
    
    markdown_final += "## udata\n"
    markdown_final += formatar_para_markdown(saida_udata_geral)
    
    for subcomando in subcomandos_encontrados:
        print(f"A processar subcomando: '{subcomando}'")
        saida_subcomando = executar_comando_udata(subcomando)
        if saida_subcomando:
            markdown_final += "\n" + "---" + "\n\n"
            markdown_final += f"## udata {subcomando}\n"
            markdown_final += formatar_para_markdown(saida_subcomando)
    
    # Usa o modo 'w' para criar ou sobrescrever o ficheiro
    try:
        with open('udata_comandos.md', 'w', encoding='utf-8') as f:
            f.write(markdown_final)
        print("\nSucesso! Documentação completa gerada em 'udata_comandos.md'.")
    except IOError as e:
        print(f"Erro: Não foi possível escrever no ficheiro. Verifique as permissões da pasta. Detalhes: {e}")

# --- Execução do script ---
if __name__ == "__main__":
    gerar_documentacao_completa()