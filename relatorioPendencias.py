import os
import pandas as pd
from fpdf import FPDF
import matplotlib.pyplot as plt
from datetime import date

# Variáveis
data_atual = date.today().strftime('(%m/%Y)')
texto_top = f"Lojas com pendências excedentes - {data_atual}"
max_pendencia = 1
meses_excedidos = 1

print(f"Diretório atual: {os.getcwd()}")

class CustomPDF(FPDF):
    def header(self):
        self.image('logo.png', 10, 8, 33)
        self.set_font('Times', 'B', 12)
        self.cell(0, 10, 'Relatório de Pendências', ln=True, align='C')
        self.ln(5)
        self.set_line_width(0.2)
        self.line(10, 25, 200, 25)
        self.ln(2)

    def footer(self):
        self.set_y(-15)
        self.set_font('Times', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')

    def chapter_title(self, title):
        self.set_font('Times', 'B', 12)
        self.cell(0, 10, title, ln=True, align='L')
        self.ln(3)

    def chapter_body(self, body):
        self.set_font('Times', '', 12)
        self.multi_cell(0, 8, body)
        self.ln(1)

    def add_image(self, img_path):
        self.image(img_path, x=10, y=None, w=self.w - 20, h=150)
        self.ln(10)

def verificar_lojas_com_pendencias(df, max_pendencia, meses_excedidos):
    status_pendentes = {'pendente', '1° AGUARDANDO', '2° AGUARDANDO', '3° AGUARDANDO'}
    df['COMPETENCIA_DT'] = pd.to_datetime(df['COMPETENCIA'], format='%d/%m/%Y')
    pendencias_por_loja = df[df['STATUS_DO_EPI'].isin(status_pendentes)].groupby(['UF', 'LOJA', 'COMPETENCIA'])['STATUS_DO_EPI'].count().reset_index(name='COUNT')
    total_pendencias_por_loja = pendencias_por_loja.groupby(['UF', 'LOJA'])['COUNT'].sum().reset_index()
    lojas_com_pendencias = pendencias_por_loja.groupby(['UF', 'LOJA']).filter(lambda x: len(x) >= meses_excedidos)
    total_pendencias = total_pendencias_por_loja[total_pendencias_por_loja['COUNT'] >= max_pendencia]
    return total_pendencias, lojas_com_pendencias

def gerar_grafico(total_pendencias, max_pendencia):
       if total_pendencias.empty:
           print("Não há dados para gerar o gráfico.")
           return
       plt.figure(figsize=(18, 16))
       total_pendencias_sorted = total_pendencias.sort_values(by='COUNT', ascending=True)
       plt.barh(total_pendencias_sorted['LOJA'], total_pendencias_sorted['COUNT'], color='orange', height=0.7)
       plt.xlabel('Total de pendências', fontsize=14)
       plt.title('Total de pendências por loja', fontsize=18)
       plt.xticks(fontsize=12)
       plt.yticks(fontsize=10)
       plt.tight_layout()
       plt.subplots_adjust(left=0.3, right=0.95, bottom=0.05)
       plt.axvline(x=max_pendencia, color='red', linestyle='--', linewidth='2', label=f'Máximo de pendências ({max_pendencia})')
       plt.legend(loc='upper right')
       try:
           plt.savefig('grafico_pendencias.png', bbox_inches='tight', dpi=300)
           print("Gráfico gerado com sucesso: grafico_pendencias.png")
       except Exception as e:
           print(f"Erro ao salvar gráfico: {e}")
       plt.close()

def gerar_relatorio_pdf(total_pendencias):
       print("Iniciando a geração do PDF...")

       pdf = CustomPDF()
       pdf.add_page()
       pdf.chapter_title(texto_top)

       total_pendencias_sorted = total_pendencias.sort_values(by=['UF', 'COUNT'], ascending=[True, False])
       uf_atual = None
       for _, row in total_pendencias_sorted.iterrows():
           if row['UF'] != uf_atual:
               if uf_atual is not None:
                   pdf.ln(5)
               uf_atual = row['UF']
               pdf.chapter_title(f'UF: {uf_atual}')
           pdf.set_font('Times', '', 12)
           pdf.cell(0, 10, f'{row["LOJA"]} - Total de pendências: {row["COUNT"]}', ln=True)

       print("Adicionando o gráfico no PDF...")
       pdf.add_page()
       pdf.chapter_title('Gráfico de pendências por loja')
       
       try:
           pdf.add_image('grafico_pendencias.png')
           print("Imagem adicionada com sucesso!")
       except Exception as e:
           print(f"Erro ao adicionar imagem: {e}")

       pdf.output('relatorioLojasComPendencias.pdf')
       print("PDF gerado com sucesso!")

# Main execution
df = pd.read_csv('controleEpiGeral.csv', delimiter=';', encoding='utf-8', on_bad_lines='skip')
df.columns = ['RE', 'NOME', 'COMPETENCIA', 'LOJA', 'STATUS_DO_EPI', 'UF']

total_pendencias, lojas_com_pendencias = verificar_lojas_com_pendencias(df, max_pendencia, meses_excedidos)
gerar_grafico(total_pendencias, max_pendencia)
gerar_relatorio_pdf(total_pendencias)

print('Relatório gerado com sucesso para lojas com pendências excedentes!')