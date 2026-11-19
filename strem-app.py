import html
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components
from pyvis.network import Network

st.set_page_config(
    page_title="HEIWA | Explorador de Argumentos",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------- Design & Nova Paleta ---------------------------------------
st.markdown("""
<style>
.block-container {padding-top: 1.5rem; padding-bottom: 2rem;}
.hero {
    padding: 1.35rem 1.6rem;
    border: 1px solid #CBD5E1;
    border-radius: 16px;
    background: linear-gradient(125deg, #0F172A 0%, #1E293B 60%, #0F766E 100%);
    margin-bottom: 1.2rem;
    box-shadow: 0 4px 12px rgba(15, 23, 42, 0.08);
}
.hero h1 {margin: 0; font-size: 1.95rem; color: #F8FAFC; letter-spacing: -0.02em;}
.hero p {margin: .4rem 0 0 0; color: #CBD5E1; font-size: 0.98rem;}
.small-note {color: #64748B; font-size: .88rem;}
div[data-testid="stMetric"] {
    border: 1px solid #E2E8F0;
    background-color: #F8FAFC;
    padding: 12px 16px;
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <h1>HEIWA — Explorador de Argumentos</h1>
  <p>Explore afirmações, dados e a arquitetura retórica de conversas públicas.</p>
</div>
""", unsafe_allow_html=True)

COLS = {
    "conversation": ["Conversation_id", "Conversation ID", "conversation_id"],
    "text": ["Texto", "text", "Texto original"],
    "claim": [
        "Trecho que contém a afirmação (claim) extraída",
        "Trecho que contém a afirmação (claim) extraída ",
        "Claim", "claim"
    ],
    "data": ["Trecho que contém dados extraídos", "Dado", "Data"],
    "warrant": [
        "Trecho que contém justificativa (warrant) extraído",
        "Trecho que contém justificativa (warrant) extraída",
        "Warrant", "Justificativa (Warrant)"
    ],
    "rebuttal": [
        "Trecho que contém refutação (rebuttal) extraído",
        "Trecho que contém refutação (rebuttal) extraída",
        "Rebuttal", "Refutação"
    ],
    "backing": [
        "Trecho que contém Apoio adicional (backing) extraído",
        "Trecho que contém apoio adicional (backing) extraído",
        "Backing", "Apoio adicional"
    ],
    "qualifier": [
        "Trecho que contém qualificador extraído",
        "Trecho que contém qualificador (qualifier) extraído",
        "Qualifier", "Qualificador"
    ],
    "id": ["ID", "Id", "id"],
    "claim_present": ["Afirmação (claim) presente? (Sim ou Não)", "Claim presente?", "claim_present"],
    "data_present": ["Dados presente? (Sim ou Não)", "Dados presentes? (Sim ou Não)", "Data presente?", "data_present"],
    "warrant_present": ["Justificativa (Warrant) presente? (Sim ou Não)", "Warrant presente?", "warrant_present"],
    "rebuttal_present": ["Refutação (rebuttal) presente? (Sim ou Não)", "Rebuttal presente?", "rebuttal_present"],
    "backing_present": ["Apoio adicional (backing) presente? (Sim ou Não)", "Backing presente?", "backing_present"],
    "qualifier_present": ["Qualificador presente? (Sim ou Não)", "Qualifier presente?", "qualifier_present"],
    "claim_reason": ["Justificativa do trecho ser uma afirmação (claim)", "Justificativa da afirmação"],
    "data_reason": ["Justificativa do trecho conter dados", "Justificativa dos dados"],
    "warrant_reason": ["Justificativa do trecho conter justificativa (warrant)", "Justificativa do warrant"],
    "rebuttal_reason": ["Justificativa do trecho conter refutação (rebuttal)", "Justificativa do rebuttal"],
    "backing_reason": ["Justificativa do trecho conter Apoio adicional (backing)", "Justificativa do backing"],
    "qualifier_reason": ["Justificativa do trecho conter qualificador", "Justificativa do qualifier"],
}

# Nova paleta: Coral, Azul Oceano, Verde Esmeralda, Terracota/Âmbar, Turquesa e Índigo Suave
ELEMENTS = [
    ("claim", "Afirmação (claim)", "#E11D48", "box"),          # Crimson / Rose vibrante
    ("data", "Dado", "#0284C7", "dot"),                         # Azul Oceano
    ("warrant", "Justificativa (warrant)", "#0D9488", "dot"),   # Teal / Esmeralda
    ("rebuttal", "Refutação (rebuttal)", "#EA580C", "triangle"),# Laranja Queimado
    ("backing", "Apoio adicional (backing)", "#7C3AED", "diamond"), # Violeta Profundo
    ("qualifier", "Qualificador", "#CA8A04", "ellipse"),        # Ocre / Dourado
]

COLOR_MAP = {label: color for _, label, color, _ in ELEMENTS}


def find_col(df, key):
    for candidate in COLS.get(key, []):
        if candidate in df.columns:
            return candidate
    return None


def clean_value(value):
    if pd.isna(value):
        return ""
    value = str(value).strip()
    if value.lower() in {"nan", "none", "null"}:
        return ""
    return value


def short(text, limit=42):
    text = clean_value(text).replace("\n", " ")
    if len(text) <= limit:
        return text
    return text[:limit - 1].rstrip() + "…"


def build_presence_df(df, type_cols):
    """Cria uma matriz booleana indicando quais elementos de Toulmin existem em cada linha."""
    presence = pd.DataFrame(index=df.index)
    for key, label, _, _ in ELEMENTS:
        col = type_cols.get(key)
        if col:
            presence[label] = df[col].apply(lambda v: bool(clean_value(v)))
        else:
            presence[label] = False
    return presence


def main():
    with st.sidebar:
        st.header("1. Carregar dados")
        uploaded = st.file_uploader("Envie sua planilha de anotações", type=["xlsx", "xls", "csv"])
        st.caption("A planilha deve ter uma linha por anotação e colunas que identifiquem os elementos de Toulmin.")
        st.divider()
        st.header("2. Explorar")
        st.caption("Os filtros aparecem depois que um arquivo válido é carregado.")

    if uploaded is None:
        st.info("Comece enviando uma planilha Excel (.xlsx/.xls) ou CSV.")
        st.markdown("### O que você poderá fazer")
        c1, c2, c3 = st.columns(3)
        c1.markdown("**Rede & Inspeção**\n\nExplore grafos interativos com a nova paleta visual e consulte justificativas.")
        c2.markdown("**Anatomia Argumentativa**\n\nAnalise a coocorrência de elementos e a densidade retórica por conversa.")
        c3.markdown("**Dados & Exportação**\n\nFiltre registros específicos e baixe o recorte em CSV.")
        return

    try:
        if uploaded.name.lower().endswith(".csv"):
            try:
                df = pd.read_csv(uploaded)
            except UnicodeDecodeError:
                uploaded.seek(0)
                df = pd.read_csv(uploaded, encoding="latin-1")
        else:
            df = pd.read_excel(uploaded)
    except Exception as exc:
        st.error(f"Não foi possível ler o arquivo: {exc}")
        return

    if df.empty:
        st.warning("O arquivo não contém linhas.")
        return

    conv_col = find_col(df, "conversation")
    claim_col = find_col(df, "claim")
    if claim_col is None:
        st.error("Não encontrei a coluna do trecho de afirmação (claim). Confira o cabeçalho da planilha.")
        with st.expander("Colunas detectadas"):
            st.write(list(df.columns))
        return

    # Sidebar filters
    with st.sidebar:
        st.header("Filtros de exploração")
        if conv_col:
            conv_values = sorted(df[conv_col].dropna().astype(str).unique().tolist())
            selected_convs = st.multiselect(
                "Conversas",
                options=conv_values,
                default=conv_values[:3] if len(conv_values) > 3 else conv_values,
                help="Deixe selecionadas apenas as conversas que deseja explorar."
            )
            if selected_convs:
                filtered = df[df[conv_col].astype(str).isin(selected_convs)].copy()
            else:
                filtered = df.iloc[0:0].copy()
        else:
            filtered = df.copy()
            st.warning("A coluna Conversation_id não foi encontrada; o filtro por conversa está desativado.")

        query = st.text_input("Buscar texto", placeholder="Digite uma palavra ou expressão…")
        if query:
            search_cols = [c for c in [claim_col, find_col(df, "text"), find_col(df, "data"),
                                       find_col(df, "warrant"), find_col(df, "rebuttal")] if c]
            mask = pd.Series(False, index=filtered.index)
            for col in search_cols:
                mask = mask | filtered[col].fillna("").astype(str).str.contains(query, case=False, regex=False)
            filtered = filtered[mask]

        with st.expander("Opções do grafo"):
            max_rows = st.slider("Máximo de anotações no grafo", min_value=10, max_value=500,
                                 value=120, step=10)
            show_labels = st.checkbox("Mostrar rótulos dos nós", value=True)
            physics = st.checkbox("Permitir estabilização automática", value=True)

    if filtered.empty:
        st.warning("Nenhuma anotação corresponde aos filtros. Tente selecionar outras conversas ou remover a busca.")
        return

    type_cols = {key: find_col(df, key) for key, *_ in ELEMENTS}
    presence_df = build_presence_df(filtered, type_cols)
    avg_complexity = presence_df.sum(axis=1).mean()

    # Metrics
    total_claims = filtered[claim_col].apply(clean_value).ne("").sum()
    metric1, metric2, metric3, metric4 = st.columns(4)
    metric1.metric("Linhas filtradas", f"{len(filtered):,}")
    metric2.metric("Afirmações (claims)", f"{total_claims:,}")
    metric3.metric("Conversas ativas", filtered[conv_col].nunique() if conv_col else "—")
    metric4.metric("Densidade média (Toulmin)", f"{avg_complexity:.2f} / 6")

    # ----------------------------- Abas Principais ---------------------------------------
    tab_grafo, tab_anatomia, tab_dados = st.tabs([
        "🕸️ Rede e Inspeção",
        "🧬 Anatomia Argumentativa",
        "📋 Dados Filtrados"
    ])

    # ================= ABA 1: REDE E INSPEÇÃO =================
    with tab_grafo:
        if len(filtered) > max_rows:
            st.warning(f"A seleção contém {len(filtered)} linhas. O grafo exibe as primeiras {max_rows} para manter a legibilidade.")
            graph_df = filtered.head(max_rows)
        else:
            graph_df = filtered

        st.markdown("### Rede argumentativa")
        st.caption("Passe o cursor sobre um nó para ver o trecho completo e a justificativa da anotação.")

        legend_items = [(label, color) for key, label, color, _ in ELEMENTS if find_col(df, key)]
        legend = st.columns(min(len(legend_items), 6) or 1)
        for i, (label, color) in enumerate(legend_items):
            with legend[i % len(legend)]:
                st.markdown(f"<span style='color:{color};font-size:1.15rem'>●</span> **{html.escape(label)}**", unsafe_allow_html=True)

        net = Network(height="590px", width="100%", bgcolor="#F8FAFC", font_color="#0F172A",
                      directed=True, cdn_resources="in_line")
        net.set_options("""
        {
          "nodes": {"font": {"size": 13, "face": "Inter, Arial"}, "borderWidth": 1.5,
                    "shadow": {"enabled": true, "size": 5, "x": 1, "y": 2}},
          "edges": {"arrows": {"to": {"enabled": true, "scaleFactor": 0.55}},
                    "color": {"color": "#94A3B8", "highlight": "#0F172A"},
                    "smooth": {"type": "dynamic"}, "font": {"size": 10, "align": "middle", "color": "#475569"}},
          "interaction": {"hover": true, "navigationButtons": true, "keyboard": true,
                          "multiselect": true},
          "physics": {"enabled": true, "stabilization": {"enabled": true, "iterations": 120},
                      "forceAtlas2Based": {"gravitationalConstant": -48, "centralGravity": 0.008,
                                           "springLength": 135, "springConstant": 0.08,
                                           "damping": 0.4},
                      "solver": "forceAtlas2Based"}
        }
        """)
        if not physics:
            net.toggle_physics(False)

        text_col = find_col(df, "text")
        id_col = find_col(df, "id")
        reason_keys = {
            "claim": "claim_reason", "data": "data_reason", "warrant": "warrant_reason",
            "rebuttal": "rebuttal_reason", "backing": "backing_reason", "qualifier": "qualifier_reason"
        }
        added_nodes = set()
        claim_options = []
        claim_rows = {}

        for row_index, row in graph_df.iterrows():
            row_label = clean_value(row[id_col]) if id_col else str(row_index + 1)
            row_label = row_label or str(row_index + 1)
            values = {key: clean_value(row[col]) if col else "" for key, col in type_cols.items()}
            claim_value = values["claim"]
            if not claim_value:
                continue

            claim_id = f"claim::{row_index}"
            claim_label = short(claim_value, 38) if show_labels else f"Afirmação {row_label}"
            claim_title = f"<b>Afirmação (claim)</b><br>{html.escape(claim_value)}"
            if text_col and clean_value(row[text_col]):
                claim_title += f"<br><br><b>Texto original</b><br>{html.escape(clean_value(row[text_col]))}"

            # Nó central da afirmação com destaque em Rose suave e borda forte
            net.add_node(
                claim_id,
                label=claim_label,
                title=claim_title,
                color={"background": "#FFE4E6", "border": "#E11D48"},
                font={"color": "#881337", "bold": True},
                shape="box",
                borderWidth=2,
                size=24
            )
            added_nodes.add(claim_id)

            for kind, label, color, shape in ELEMENTS[1:]:
                value = values[kind]
                if not value:
                    continue
                node_id = f"{kind}::{row_index}"
                node_label = short(value, 31) if show_labels else label
                reason_col = find_col(df, reason_keys[kind])
                reason = clean_value(row[reason_col]) if reason_col else ""
                title = f"<b>{html.escape(label)}</b><br>{html.escape(value)}"
                if reason:
                    title += f"<br><br><b>Justificativa da anotação</b><br>{html.escape(reason)}"
                net.add_node(node_id, label=node_label, title=title, color=color, shape=shape, size=18)
                added_nodes.add(node_id)

                relation = {
                    "data": "dá suporte a",
                    "warrant": "justifica",
                    "rebuttal": "contesta",
                    "backing": "dá apoio a",
                    "qualifier": "qualifica"
                }[kind]
                edge_color = "#EA580C" if kind == "rebuttal" else "#94A3B8"
                net.add_edge(node_id, claim_id, label=relation, title=relation, color=edge_color, arrows="to")

            claim_options.append(f"{row_label} — {short(claim_value, 90)}")
            claim_rows[claim_options[-1]] = (row_index, row)

        if len(added_nodes) == 0:
            st.info("Não há afirmações com texto nas linhas filtradas.")
        else:
            try:
                html_graph = net.generate_html()
                components.html(html_graph, height=620, scrolling=False)
            except Exception as exc:
                st.error(f"Não foi possível renderizar a rede: {exc}")

        st.divider()
        st.markdown("### Inspecionar uma afirmação")
        if claim_options:
            selected_claim = st.selectbox("Escolha uma afirmação para ver os detalhes", claim_options)
            row_index, row = claim_rows[selected_claim]
            a, b = st.columns([1.15, 1])
            with a:
                st.markdown("**Texto original da publicação**")
                original = clean_value(row[text_col]) if text_col else ""
                st.info(original or "Não preenchido na planilha.")
                st.markdown("**Afirmação (claim)**")
                st.write(clean_value(row[claim_col]) or "Não preenchida.")
                if conv_col:
                    st.caption(f"Conversation_id: `{clean_value(row[conv_col]) or 'não informado'}`")
                if id_col:
                    st.caption(f"ID da anotação: `{clean_value(row[id_col]) or 'não informado'}`")
            with b:
                for key, label, _, _ in ELEMENTS[1:]:
                    col = type_cols[key]
                    value = clean_value(row[col]) if col else ""
                    if value:
                        with st.expander(label, expanded=(key == "rebuttal")):
                            st.write(value)
                            reason_col = find_col(df, reason_keys[key])
                            reason = clean_value(row[reason_col]) if reason_col else ""
                            if reason:
                                st.caption("Justificativa da anotação")
                                st.write(reason)
                            present_col = find_col(df, f"{key}_present")
                            if present_col:
                                st.caption(f"Presente na anotação: {clean_value(row[present_col]) or 'não informado'}")

    # ================= ABA 2: NOVA VISUALIZAÇÃO (ANATOMIA ARGUMENTATIVA) =================
    with tab_anatomia:
        st.markdown("### Anatomia e Coocorrência dos Elementos de Toulmin")
        st.caption("Descubra como os argumentos são construídos: quais elementos aparecem juntos e como cada conversa estrutura suas defesas e refutações.")

        col_left, col_right = st.columns(2)

        # Gráfico 1: Matriz de Coocorrência (Heatmap)
        with col_left:
            st.markdown("#### Matriz de Coocorrência")
            st.caption("Quantas vezes dois elementos aparecem na mesma linha de anotação.")
            bool_mat = presence_df.astype(int)
            cooc = bool_mat.T.dot(bool_mat)

            fig_heat = px.imshow(
                cooc,
                text_auto=True,
                color_continuous_scale=["#F8FAFC", "#BAE6FD", "#0284C7", "#0F172A"],
                aspect="auto",
            )
            fig_heat.update_layout(
                margin=dict(l=10, r=10, t=20, b=10),
                coloraxis_showscale=False,
                xaxis_title="",
                yaxis_title="",
                height=420,
            )
            st.plotly_chart(fig_heat, use_container_width=True)

        # Gráfico 2: Perfil de Frequência / Radar
        with col_right:
            st.markdown("#### Assinatura Retórica do Recorte")
            st.caption("Proporção de anotações (%) que contêm cada componente argumentativo.")
            rates = (presence_df.mean() * 100).round(1)

            fig_radar = go.Figure()
            fig_radar.add_trace(go.Scatterpolar(
                r=rates.values.tolist() + [rates.values[0]],
                theta=rates.index.tolist() + [rates.index[0]],
                fill="toself",
                fillcolor="rgba(13, 148, 136, 0.22)",
                line=dict(color="#0D9488", width=2.5),
                marker=dict(size=7, color="#0F172A"),
                name="Frequência (%)"
            ))
            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, 100], ticksuffix="%", gridcolor="#E2E8F0"),
                    angularaxis=dict(gridcolor="#E2E8F0")
                ),
                showlegend=False,
                margin=dict(l=45, r=45, t=30, b=30),
                height=420,
            )
            st.plotly_chart(fig_radar, use_container_width=True)

        # Gráfico 3: Comparação por Conversa (Barras Empilhadas Horizontais)
        if conv_col and filtered[conv_col].nunique() > 0:
            st.divider()
            st.markdown("#### Composição Argumentativa por Conversa")
            st.caption("Distribuição absoluta dos elementos extraídos em cada `Conversation_id` selecionado.")

            conv_summary = presence_df.copy()
            conv_summary["Conversa"] = filtered[conv_col].astype(str)
            grouped = conv_summary.groupby("Conversa").sum().reset_index()
            melted = grouped.melt(id_vars="Conversa", var_name="Elemento", value_name="Ocorrências")

            fig_bar = px.bar(
                melted,
                y="Conversa",
                x="Ocorrências",
                color="Elemento",
                orientation="h",
                color_discrete_map=COLOR_MAP,
                barmode="stack",
            )
            fig_bar.update_layout(
                margin=dict(l=10, r=10, t=20, b=10),
                legend_title_text="",
                xaxis_title="Total de elementos identificados",
                yaxis_title="",
                height=max(260, min(600, 65 * len(grouped))),
            )
            st.plotly_chart(fig_bar, use_container_width=True)

    # ================= ABA 3: DADOS FILTRADOS =================
    with tab_dados:
        st.markdown("### Tabela de anotações filtradas")
        st.dataframe(filtered, use_container_width=True, hide_index=True)
        csv_bytes = filtered.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            "Baixar seleção filtrada em CSV",
            data=csv_bytes,
            file_name="heiwa_anotacoes_filtradas.csv",
            mime="text/csv"
        )

    with st.expander("Sobre a leitura do grafo e das métricas"):
        st.write(
            "Cada linha com claim gera um nó de afirmação. Elementos extraídos da mesma linha são ligados a essa afirmação. "
            "Na aba Anatomia Argumentativa, a densidade média indica quantos dos 6 componentes de Toulmin aparecem por linha."
        )


main()