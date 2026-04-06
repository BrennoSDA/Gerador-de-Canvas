import streamlit as st
from xhtml2pdf import pisa
import io
import ssl
import base64

ssl._create_default_https_context = ssl._create_unverified_context

# ==============================================================================
# 1. TEMPLATE HTML DO PDF
# ==============================================================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
    body {{ font-family: Helvetica, Arial, sans-serif; margin: 0; padding: 0; }}
    h1 {{ text-align: center; color: #333; margin-bottom: 25px; }}
    .canvas-table {{ width: 100%; border-collapse: collapse; }}
    .canvas-table td {{ border: 2px solid #BCBDBF; vertical-align: top; height: 120px; width: 20%; padding: 0; }}
    .canvas-table h3 {{ margin: 0; font-size: 11px; color: #fff; padding: 7px; text-align: center; text-transform: uppercase; font-weight: bold; letter-spacing: 0.5px; }}
    .canvas-table h3 img {{ vertical-align: middle; margin-right: 4px; margin-top: -2px; }}
    .canvas-table p {{ font-size: 11px; margin: 0; color: #000; padding: 8px; }}

    .bg-just h3 {{ background-color: #365063; }}  .bg-just {{ background-color: #E3EAF0; }}     
    .bg-smart h3 {{ background-color: #213A8F; }} .bg-smart {{ background-color: #DEE2F2; }}    
    .bg-bene h3 {{ background-color: #C49A2D; }}  .bg-bene {{ background-color: #FDF9E2; }}     
    .bg-prod h3 {{ background-color: #3A7F56; }}  .bg-prod {{ background-color: #EEF7EB; }}     
    .bg-reqs h3 {{ background-color: #832E91; }}  .bg-reqs {{ background-color: #F1E5F2; }}     
    .bg-stak h3 {{ background-color: #972728; }}  .bg-stak {{ background-color: #FAEBEA; }}     
    .bg-equi h3 {{ background-color: #E67E23; }}  .bg-equi {{ background-color: #FEEEDD; }}     
    .bg-prem h3 {{ background-color: #4995C6; }}  .bg-prem {{ background-color: #DDF0FA; }}     
    .bg-entr h3 {{ background-color: #3E8A42; }}  .bg-entr {{ background-color: #EDF7EC; }}     
    .bg-risc h3 {{ background-color: #2C2E33; }}  .bg-risc {{ background-color: #E5E5E6; }}     
    .bg-temp h3 {{ background-color: #8A2D8D; }}  .bg-temp {{ background-color: #F1E4F2; }}     
    .bg-cust h3 {{ background-color: #00A3A6; }}  .bg-cust {{ background-color: #D3EFEE; }}     
    .bg-rest h3 {{ background-color: #7A96A3; }}  .bg-rest {{ background-color: #E6EDF0; }}     
</style>
</head>
<body>
    <h1>Project Model Canvas: {nome_projeto}</h1>
    <table class="canvas-table">
        <tr>
            <td class="bg-just"><h3><img src="https://cdnjs.cloudflare.com/ajax/libs/twemoji/14.0.2/svg/1f4ac.svg" width="12" height="12"> JUSTIFICATIVAS Passado</h3><p>{justificativas}</p></td>
            <td class="bg-prod"><h3><img src="https://cdnjs.cloudflare.com/ajax/libs/twemoji/14.0.2/svg/1f4e6.svg" width="12" height="12"> PRODUTO</h3><p>{produto}</p></td>
            <td class="bg-stak"><h3><img src="https://cdnjs.cloudflare.com/ajax/libs/twemoji/14.0.2/svg/1f91d.svg" width="12" height="12"> STAKEHOLDERS Externos</h3><p>{stakeholders}</p></td>
            <td class="bg-prem"><h3><img src="https://cdnjs.cloudflare.com/ajax/libs/twemoji/14.0.2/svg/2601.svg" width="12" height="12"> PREMISSAS</h3><p>{premissas}</p></td>
            <td class="bg-risc"><h3><img src="https://cdnjs.cloudflare.com/ajax/libs/twemoji/14.0.2/svg/23f0.svg" width="12" height="12"> RISCOS</h3><p>{riscos}</p></td>
        </tr>
        <tr>
            <td class="bg-smart"><h3><img src="https://cdnjs.cloudflare.com/ajax/libs/twemoji/14.0.2/svg/1f3af.svg" width="12" height="12"> OBJ SMART</h3><p>{obj_smart}</p></td>
            <td class="bg-reqs" rowspan="2"><h3><img src="https://cdnjs.cloudflare.com/ajax/libs/twemoji/14.0.2/svg/1f4dd.svg" width="12" height="12"> REQUISITOS</h3><p>{requisitos}</p></td>
            <td class="bg-equi"><h3><img src="https://cdnjs.cloudflare.com/ajax/libs/twemoji/14.0.2/svg/1f465.svg" width="12" height="12"> EQUIPE</h3><p>{equipe}</p></td>
            <td class="bg-entr"><h3><img src="https://cdnjs.cloudflare.com/ajax/libs/twemoji/14.0.2/svg/1f5c3.svg" width="12" height="12"> GRUPO DE ENTREGAS</h3><p>{entregas}</p></td>
            <td class="bg-temp"><h3><img src="https://cdnjs.cloudflare.com/ajax/libs/twemoji/14.0.2/svg/23f3.svg" width="12" height="12"> LINHA DO TEMPO</h3><p>{tempo}</p></td>
        </tr>
        <tr>
            <td class="bg-bene"><h3><img src="https://cdnjs.cloudflare.com/ajax/libs/twemoji/14.0.2/svg/1f4c8.svg" width="12" height="12"> BENEFÍCIOS Futuro</h3><p>{beneficios}</p></td>
            <td class="bg-rest" colspan="2"><h3><img src="https://cdnjs.cloudflare.com/ajax/libs/twemoji/14.0.2/svg/1f6ab.svg" width="12" height="12"> RESTRIÇÕES</h3><p>{restricoes}</p></td>
            <td class="bg-cust"><h3><img src="https://cdnjs.cloudflare.com/ajax/libs/twemoji/14.0.2/svg/1f4b0.svg" width="12" height="12"> $$$ CUSTOS</h3><p>{custos}</p></td>
        </tr>
    </table>
</body>
</html>
"""

# ==============================================================================
# 2. FUNÇÕES AUXILIARES E CALLBACKS
# ==============================================================================
def gerar_pdf(html_content):
    result = io.BytesIO()
    pdf = pisa.CreatePDF(io.StringIO(html_content), dest=result)
    if not pdf.err:
        return result.getvalue()
    return None

def custom_css():
    st.markdown("""
        <style>
            .cabecalho-form { color: #fff; padding: 6px; border-radius: 4px; text-align: center; font-weight: bold; font-size: 13px; margin-bottom: 2px; text-transform: uppercase; box-shadow: 1px 1px 2px rgba(0,0,0,0.2); }
            [data-testid="stForm"] > div > div > div > div { border: none !important; padding: 0 !important; }
            textarea { border-radius: 4px !important; color: #000 !important; border: 1px solid #ddd !important; }
            #just_wrapper textarea { background-color: #E3EAF0 !important; }
            #smart_wrapper textarea { background-color: #DEE2F2 !important; }
            #bene_wrapper textarea { background-color: #FDF9E2 !important; }
            #prod_wrapper textarea { background-color: #EEF7EB !important; }
            #reqs_wrapper textarea { background-color: #F1E5F2 !important; }
            #stak_wrapper textarea { background-color: #FAEBEA !important; }
            #equi_wrapper textarea { background-color: #FEEEDD !important; }
            #entr_wrapper textarea { background-color: #EDF7EC !important; }
            #risc_wrapper textarea { background-color: #E5E5E6 !important; }
            #temp_wrapper textarea { background-color: #F1E4F2 !important; }
            #cust_wrapper textarea { background-color: #D3EFEE !important; }
            #prem_wrapper textarea { background-color: #DDF0FA !important; }
            #rest_wrapper textarea { background-color: #E6EDF0 !important; }
        </style>
    """, unsafe_allow_html=True)

def criar_bloco_form(titulo, cor_cabecalho, altura, key):
    st.markdown(f'<div id="{key}_wrapper">', unsafe_allow_html=True)
    st.markdown(f'<div class="cabecalho-form" style="background-color: {cor_cabecalho};">{titulo}</div>', unsafe_allow_html=True)
    # Removemos o value=... daqui, agora ele puxa direto da memória do sistema
    input_text = st.text_area(titulo, height=altura, label_visibility="collapsed", key=key)
    st.markdown('</div>', unsafe_allow_html=True)
    return input_text

# FUNÇÃO MÁGICA: Controla o estado da memória do Streamlit
def preencher_dados_exemplo():
    if st.session_state.toggle_exemplo:
        st.session_state.nome_proj = "App Delivery Saudável"
        st.session_state.just = "Aumento de 40% na demanda por alimentação saudável na região e dificuldade logística dos pequenos restaurantes de bairro."
        st.session_state.prod = "Aplicativo mobile para conectar clientes a restaurantes de comida fitness e saudável."
        st.session_state.stak = "Restaurantes parceiros\nEntregadores locais\nClientes finais\nInvestidor Anjo"
        st.session_state.prem = "1. Restaurantes possuem smartphones ou tablets\n2. Clientes aceitam pagar via PIX ou Cartão no app"
        st.session_state.risc = "1. Atraso no desenvolvimento\n2. Baixa adesão inicial de restaurantes\n3. Problemas no gateway de pagamento"
        st.session_state.smart = "Lançar o aplicativo na cidade em 4 meses e atingir 1.000 pedidos realizados no primeiro mês de operação."
        st.session_state.reqs = "1. App cliente (Android e iOS)\n2. App do entregador\n3. Painel Web do restaurante\n4. Sistema de rastreio GPS\n5. Pagamento integrado\n6. Avaliação de restaurantes"
        st.session_state.equi = "1 Gerente de Projeto\n2 Desenvolvedores Mobile\n1 Desenvolvedor Backend\n1 Designer UX/UI"
        st.session_state.entr = "Fase 1: Protótipos e Design\nFase 2: App Frontend\nFase 3: Integração Backend e PIX\nFase 4: Testes Beta"
        st.session_state.temp = "Mês 1: Protótipos\nMês 2: Dev Front\nMês 3: Dev Back\nMês 4: Testes e Lançamento"
        st.session_state.bene = "Aumento de faturamento para os restaurantes locais, acesso fácil a dieta para os clientes e geração de renda extra para motoboys."
        st.session_state.rest = "O orçamento não pode ultrapassar R$ 50.000,00 e o time não pode realizar horas extras (limite de 40h semanais)."
        st.session_state.cust = "Equipe Técnica: R$ 35.000\nMarketing Inicial: R$ 10.000\nServidores/Infra: R$ 5.000"
    else:
        # Se desligar a chavinha, limpa tudo
        st.session_state.nome_proj = ""
        st.session_state.just = ""
        st.session_state.prod = ""
        st.session_state.stak = ""
        st.session_state.prem = ""
        st.session_state.risc = ""
        st.session_state.smart = ""
        st.session_state.reqs = ""
        st.session_state.equi = ""
        st.session_state.entr = ""
        st.session_state.temp = ""
        st.session_state.bene = ""
        st.session_state.rest = ""
        st.session_state.cust = ""

# ==============================================================================
# 3. INTERFACE DO USUÁRIO NO STREAMLIT
# ==============================================================================
st.set_page_config(page_title="Project Model Canvas Gerador", layout="wide")

custom_css()

st.title("Gerador de Project Model Canvas (PMC) 📋")

# A chavinha chama a função automaticamente toda vez que for clicada (on_change)
st.toggle("💡 Preencher com dados de exemplo (Acelera a apresentação)", key="toggle_exemplo", on_change=preencher_dados_exemplo)

st.write("---")

with st.form("pmc_form"):
    # Agora o nome do projeto também recebe uma key oficial
    nome_projeto = st.text_input("Nome do Projeto", key="nome_proj")
    st.write("---")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        justificativas = criar_bloco_form("JUSTIFICATIVAS", "#365063", 100, key="just")
        obj_smart = criar_bloco_form("OBJ SMART", "#213A8F", 100, key="smart")
        beneficios = criar_bloco_form("BENEFÍCIOS Futuro", "#C49A2D", 100, key="bene")
        
    with col2:
        produto = criar_bloco_form("PRODUTO", "#3A7F56", 100, key="prod")
        requisitos = criar_bloco_form("REQUISITOS", "#832E91", 245, key="reqs")
        
    with col3:
        stakeholders = criar_bloco_form("STAKEHOLDERS", "#972728", 100, key="stak")
        equipe = criar_bloco_form("EQUIPE", "#E67E23", 100, key="equi")
        
    with col4:
        premissas = criar_bloco_form("PREMISSAS", "#4995C6", 100, key="prem")
        entregas = criar_bloco_form("GRUPO DE ENTREGAS", "#3E8A42", 100, key="entr")
        
    with col5:
        riscos = criar_bloco_form("RISCOS", "#2C2E33", 100, key="risc")
        tempo = criar_bloco_form("LINHA DO TEMPO", "#8A2D8D", 100, key="temp")
        custos = criar_bloco_form("CUSTOS", "#00A3A6", 100, key="cust")

    restricoes = criar_bloco_form("RESTRIÇÕES", "#7A96A3", 80, key="rest")
    
    st.write("---")
    submit_button = st.form_submit_button("Gerar PDF do Projeto")

# ==============================================================================
# 4. LÓGICA DE PROCESSAMENTO, DOWNLOAD E PRÉ-VISUALIZAÇÃO
# ==============================================================================
if submit_button:
    if not nome_projeto.strip():
        st.warning("⚠️ Por favor, preencha o Nome do Projeto antes de gerar o Canvas!")
    else:
        html_preenchido = HTML_TEMPLATE.format(
            nome_projeto=nome_projeto.replace('\n', '<br>'),
            justificativas=justificativas.replace('\n', '<br>'),
            obj_smart=obj_smart.replace('\n', '<br>'),
            beneficios=beneficios.replace('\n', '<br>'),
            produto=produto.replace('\n', '<br>'),
            requisitos=requisitos.replace('\n', '<br>'),
            stakeholders=stakeholders.replace('\n', '<br>'),
            equipe=equipe.replace('\n', '<br>'),
            premissas=premissas.replace('\n', '<br>'),
            entregas=entregas.replace('\n', '<br>'),
            riscos=riscos.replace('\n', '<br>'),
            tempo=tempo.replace('\n', '<br>'),
            custos=custos.replace('\n', '<br>'),
            restricoes=restricoes.replace('\n', '<br>')
        )
        
        pdf_bytes = gerar_pdf(html_preenchido)
        
        if pdf_bytes:
            st.success("✨ Project Model Canvas gerado com sucesso!")
            
            st.download_button(
                label="Baixar PMC em PDF 📄",
                data=pdf_bytes,
                file_name=f"PMC_{nome_projeto.replace(' ', '_')}.pdf",
                mime="application/pdf",
                type="primary" 
            )
            
            st.write("---")
            st.markdown("### Pré-visualização do Documento")
            
            # O GRANDE TRUQUE: Renderizamos o HTML diretamente na tela do Streamlit!
            # Isso cria uma "janela" segura que o Chrome aceita perfeitamente.
            import streamlit.components.v1 as components
            components.html(html_preenchido, height=650, scrolling=True)
            
        else:
            st.error("Houve um erro interno ao gerar o arquivo PDF.")
