import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import sys
from streamlit.web import bootstrap

st.set_page_config(page_title="Прогноз на мероприятие", layout="wide")

def main():
    st.title("Прогноз на мероприятие")

    events = {
        'Neuropunk': {'budget': 500000, 'guests': 500, 'ticket_price': 2000, 'marketing_percent': 0.3, 'fame_factor': 1.5},
        'Bass Vibration': {'budget': 120000, 'guests': 80, 'ticket_price': 1200, 'marketing_percent': 0.3, 'fame_factor': 1.0}
    }

    # Ввод данных
    col1, col2, col3, col4 = st.columns(4)
    new_budget = col1.number_input("Общий бюджет (₽):", min_value=0, value=150000, step=1000, key="budget")
    new_price = col2.number_input("Цена входа (₽):", min_value=1, value=600, step=100, key="price")
    risk_amount = col3.number_input("Финансовые риски (₽):", min_value=0, value=0, step=5000, key="risk")
    marketing_percentage = col4.slider("Маркетинг (%):", 0, 100, 30, 5, key="marketing") / 100

    # Расчет маркетингового бюджета как процент от общего бюджета
    marketing_cost = max(0, new_budget * marketing_percentage)
    available_budget = new_budget - risk_amount
    remaining_budget = available_budget - marketing_cost

    base_guests = 0
    base_marketing_effectiveness = 0.00144
    marketing_effectiveness_slope = 0.002

    if new_budget == 500000 and new_price == 2000 and marketing_percentage == 0.3:
        fame_factor = 1.5
    else:
        fame_factor = 1.0

    marketing_effectiveness = base_marketing_effectiveness + marketing_effectiveness_slope * (fame_factor - 1.0)
    marketing_guests = marketing_cost * marketing_effectiveness * fame_factor
    avg_ticket_price = (events['Neuropunk']['ticket_price'] + events['Bass Vibration']['ticket_price']) / 2
    price_factor = 1 - 2.2 * (new_price - avg_ticket_price) / avg_ticket_price

    estimated_guests = min(600, max(0, round((base_guests + marketing_guests) * price_factor)))

    total_profit = new_budget - (risk_amount + marketing_cost) + (new_price * estimated_guests)
    net_profit = total_profit - remaining_budget

    df = pd.DataFrame({
        'Бюджет': [events['Neuropunk']['budget'], events['Bass Vibration']['budget'], available_budget],
        'Количество гостей': [events['Neuropunk']['guests'], events['Bass Vibration']['guests'], estimated_guests],
        'Стоимость входа': [events['Neuropunk']['ticket_price'], events['Bass Vibration']['ticket_price'], new_price],
        'Мероприятие': ['Neuropunk', 'Bass Vibration', 'Hardline']
    })

    col_left, col_right = st.columns([3, 1])

    with col_left:
        fig = go.Figure()
        colors = {'Neuropunk': 'yellow', 'Bass Vibration': 'green', 'Hardline': '#ff005e'}
        for _, row in df.iterrows():
            if row['Мероприятие'] == 'Neuropunk' and not st.session_state.get('show_neuropunk', True):
                continue
            if row['Мероприятие'] == 'Bass Vibration' and not st.session_state.get('show_bass_vibration', True):
                continue
            if row['Мероприятие'] == 'Hardline' and not st.session_state.get('show_hardline', True):
                continue
            fig.add_shape(type="line", x0=row['Количество гостей'], y0=0, x1=row['Количество гостей'], y1=row['Стоимость входа'], 
                         line=dict(color='grey', dash="dot", width=1), layer='below')
            fig.add_shape(type="line", x0=0, y0=row['Стоимость входа'], x1=row['Количество гостей'], y1=row['Стоимость входа'], 
                         line=dict(color='grey', dash="dot", width=1), layer='below')
            fig.add_trace(go.Scatter(
                x=[row['Количество гостей']],
                y=[row['Стоимость входа']],
                mode='markers+text',
                name=row['Мероприятие'],
                marker=dict(size=15, color=colors[row['Мероприятие']], opacity=1),
                text=[row['Мероприятие']],
                textposition='top center',
                textfont=dict(color='white', size=12),
                showlegend=False
            ))
        fig.update_layout(
            xaxis_title="Количество гостей",
            yaxis_title="Стоимость входа (₽)",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white', size=12),
            height=600,
            width=None
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.markdown(
            """
            <style>
            .checkbox-container {
                display: flex;
                flex-direction: column;
                align-items: flex-start;
                margin-top: 0;
            }
            .checkbox-item {
                display: flex;
                flex-direction: row;
                align-items: center;
                margin-bottom: 10px;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
        with st.container():
            st.markdown('<div class="checkbox-container">', unsafe_allow_html=True)
            st.markdown('<div class="checkbox-item">', unsafe_allow_html=True)
            st.checkbox("", value=True, key="show_neuropunk", label_visibility="collapsed")
            st.markdown('<span style="color: yellow;">Neuropunk</span>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('<div class="checkbox-item">', unsafe_allow_html=True)
            st.checkbox("", value=True, key="show_bass_vibration", label_visibility="collapsed")
            st.markdown('<span style="color: green;">Bass Vibration</span>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('<div class="checkbox-item">', unsafe_allow_html=True)
            st.checkbox("", value=True, key="show_hardline", label_visibility="collapsed")
            st.markdown('<span style="color: #ff005e;">Hardline</span>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    st.subheader("Расчетные данные")
    st.markdown(
        """
        <style>
        .stMetric div[data-testid="stMetricValue"] {
            color: white !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    col_metrics1, col_metrics2, col_metrics3, col_metrics4, col_metrics5 = st.columns(5)

    with col_metrics1:
        st.metric(f"Маркетинг ({marketing_percentage:.0%})", f"{marketing_cost:,.0f}₽", 
                 delta=f"{marketing_cost / new_budget:.1%} от общего бюджета" if new_budget > 0 else None, 
                 delta_color="normal")

    with col_metrics2:
        if remaining_budget < 0:
            st.markdown(
                """
                <style>
                .stMetric div[data-testid="stMetricValue"] {
                    color: red !important;
                }
                </style>
                """,
                unsafe_allow_html=True
            )
        st.metric("Остаток бюджета", f"{remaining_budget:,.0f}₽", 
                 delta=f"{remaining_budget / available_budget:.1%}" if available_budget > 0 else None, 
                 delta_color="inverse")

    with col_metrics3:
        st.metric("Расчетное количество гостей", f"{estimated_guests:,d}", 
                 delta=f"+{int(marketing_guests)}", 
                 delta_color="normal")

    with col_metrics4:
        st.metric("Примерная прибыль", f"{total_profit:,.0f}₽")

    with col_metrics5:
        st.metric("Чистая прибыль", f"{net_profit:,.0f}₽")

if __name__ == "__main__":
    main()

# Добавляем WSGI-совместимый запуск для Render
def run_streamlit():
    # Запускаем Streamlit через его внутренний сервер
    bootstrap.run("app.py", "", [], [])

if __name__ == "__main__":
    # Для локального запуска через `python app.py` или Render
    run_streamlit()