import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import re

st.set_page_config(page_title="Прогноз на мероприятие", layout="wide", initial_sidebar_state="collapsed")

def get_next_version(base_name, existing_events, versions):
    if base_name in existing_events and base_name != 'Hardline':
        version = 2
        while f"{base_name} V{version}" in versions:
            version += 1
        return f"{base_name} V{version}"
    return base_name

def generate_color(base_name):
    color_map = {'Neuropunk': '#ffcc00', 'Bass Vibration': '#00ffcc'}
    base_color = color_map.get(base_name, '#ff005e')
    if base_name == 'Hardline':
        return '#ff005e'
    match = re.search(r'V(\d+)$', base_name)
    if match:
        version = int(match.group(1))
        r, g, b = tuple(int(base_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        if base_name.startswith('Neuropunk'):
            r = min(255, r + (version - 2) * 20)
            g = max(0, g - (version - 2) * 10)
        elif base_name.startswith('Bass Vibration'):
            g = min(255, g + (version - 2) * 20)
            b = max(0, b - (version - 2) * 10)
        return f'#{r:02x}{g:02x}{b:02x}'
    return base_color

def main():
    st.title("Прогноз на мероприятие")

    events = {
        'Neuropunk': {'budget': 500000, 'guests': 500, 'ticket_price': 2000, 'marketing_percent': 0.3, 'fame_factor': 1.5},
        'Bass Vibration': {'budget': 120000, 'guests': 80, 'ticket_price': 1200, 'marketing_percent': 0.3, 'fame_factor': 1.0},
        'Hardline': {'budget': 120000, 'ticket_price': 1200, 'marketing_percent': 0.3, 'fame_factor': 1.0}
    }

    default_budget, default_risk, default_marketing = 120000, 0, 30
    default_pre_sale = {
        'stage1_price': 500, 'stage1_limit': 50,
        'stage2_price': 600, 'stage2_limit': 50,
        'stage3_price': 700, 'stage3_limit': 50,
        'door_price': 1000, 'door_limit': 999
    }

    if 'event_versions' not in st.session_state:
        st.session_state.event_versions = {name: name for name in events.keys()}
    if 'budget_values' not in st.session_state:
        st.session_state.budget_values = {name: default_budget for name in events.keys()}
    if 'risk_values' not in st.session_state:
        st.session_state.risk_values = {name: default_risk for name in events.keys()}
    if 'marketing_values' not in st.session_state:
        st.session_state.marketing_values = {name: default_marketing for name in events.keys()}
    if 'pre_sale_values' not in st.session_state:
        st.session_state.pre_sale_values = {name: default_pre_sale.copy() for name in events.keys()}
    if 'checkbox_states' not in st.session_state:
        st.session_state.checkbox_states = {'show_neuropunk': True, 'show_bass_vibration': True, 'show_hardline': True}

    current_event_name = st.session_state.event_versions.get('event_name', 'Hardline')

    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.subheader("Настройки")
        col_settings_left, col_settings_right = st.columns([1, 1])

        current_event_name = col_settings_left.selectbox("Мероприятие:", options=list(events.keys()), 
                                                        index=2 if current_event_name == 'Hardline' else list(events.keys()).index(current_event_name), 
                                                        key="event_name")
        display_event_name = get_next_version(current_event_name, events, st.session_state.event_versions)

        if display_event_name != st.session_state.event_versions.get(current_event_name, current_event_name):
            st.session_state.event_versions[current_event_name] = display_event_name

        marketing_percentage = col_settings_left.slider("Маркетинг (%):", 0, 100, st.session_state.marketing_values.get(current_event_name, default_marketing), 5, key=f"marketing_{current_event_name}") / 100
        new_budget = col_settings_right.number_input("Бюджет (₽):", 0, value=st.session_state.budget_values.get(current_event_name, default_budget), step=1000, key=f"budget_{current_event_name}")
        risk_amount = col_settings_right.number_input("Расходы (₽):", 0, value=st.session_state.risk_values.get(current_event_name, default_risk), step=5000, key=f"risk_{current_event_name}")

        st.session_state.budget_values[current_event_name] = new_budget
        st.session_state.risk_values[current_event_name] = risk_amount
        st.session_state.marketing_values[current_event_name] = int(marketing_percentage * 100)

    with col_right:
        st.subheader("Продажа")
        col_stage1, col_stage2, col_stage3, col_door = st.columns(4)

        pre_sale = st.session_state.pre_sale_values[current_event_name]
        with col_stage1:
            stage1_price = st.number_input("Цена Этап 1", 1, value=pre_sale['stage1_price'], step=100, key=f"state1_price_{current_event_name}")
            stage1_limit = st.number_input("Количество", 0, value=pre_sale['stage1_limit'], step=1, key=f"state1_limit_{current_event_name}")
        with col_stage2:
            stage2_price = st.number_input("Цена Этап 2", 1, value=pre_sale['stage2_price'], step=100, key=f"state2_price_{current_event_name}")
            stage2_limit = st.number_input("Количество", 0, value=pre_sale['stage2_limit'], step=1, key=f"state2_limit_{current_event_name}")
        with col_stage3:
            stage3_price = st.number_input("Цена Этап 3", 1, value=pre_sale['stage3_price'], step=100, key=f"state3_price_{current_event_name}")
            stage3_limit = st.number_input("Количество", 0, value=pre_sale['stage3_limit'], step=1, key=f"state3_limit_{current_event_name}")
        with col_door:
            door_price = st.number_input("Цена На входе", 1, value=pre_sale['door_price'], step=100, key=f"door_price_{current_event_name}")
            door_limit = st.number_input("Количество", 0, value=pre_sale['door_limit'], step=1, key=f"door_limit_{current_event_name}")

        st.session_state.pre_sale_values[current_event_name] = {
            'stage1_price': stage1_price, 'stage1_limit': stage1_limit,
            'stage2_price': stage2_price, 'stage2_limit': stage2_limit,
            'stage3_price': stage3_price, 'stage3_limit': stage3_limit,
            'door_price': door_price, 'door_limit': door_limit
        }

    fame_factor = 1.5 if current_event_name == 'Neuropunk' else 1.0
    marketing_cost = max(0, new_budget * marketing_percentage)
    available_budget = new_budget - risk_amount

    base_guests, marketing_effectiveness = 0, 0.00222 + 0.002 * (fame_factor - 1.0)
    marketing_guests = marketing_cost * marketing_effectiveness * fame_factor

    stage1_price, stage2_price, stage3_price, door_price = pre_sale['stage1_price'], pre_sale['stage2_price'], pre_sale['stage3_price'], pre_sale['door_price']
    stage1_limit, stage2_limit, stage3_limit, door_limit = pre_sale['stage1_limit'], pre_sale['stage2_limit'], pre_sale['stage3_limit'], pre_sale['door_limit']

    price_factor = 1
    # Сначала рассчитываем количество гостей
    total_tickets_available = stage1_limit + stage2_limit + stage3_limit + door_limit
    # Предварительный расчет средней цены на основе доступных билетов для проверки условия
    prelim_avg_price = (stage1_price * stage1_limit + stage2_price * stage2_limit + 
                        stage3_price * stage3_limit + door_price * door_limit) / total_tickets_available if total_tickets_available > 0 else 0

    # Обновленный расчет количества гостей для Hardline: если предварительная средняя цена выше 500, увеличиваем гостей
    if current_event_name == 'Hardline' and prelim_avg_price > 500:
        estimated_guests = min(total_tickets_available, max(0, round((base_guests + marketing_guests * 1.5) * price_factor)))  # Увеличиваем на 50%
    else:
        estimated_guests = min(total_tickets_available, max(0, round((base_guests + marketing_guests) * price_factor)))
    total_guests = estimated_guests
    ticket_sales = {
        'stage1': min(total_guests, stage1_limit) if total_guests > 0 else 0,
        'stage2': min(max(0, total_guests - stage1_limit), stage2_limit) if total_guests > stage1_limit else 0,
        'stage3': min(max(0, total_guests - stage1_limit - stage2_limit), stage3_limit) if total_guests > stage1_limit + stage2_limit else 0,
        'door': min(max(0, total_guests - stage1_limit - stage2_limit - stage3_limit), door_limit) if door_limit > 0 else max(0, total_guests - stage1_limit - stage2_limit - stage3_limit)
    }

    # Корректный расчет средней цены билета на основе фактически проданных билетов
    sold_tickets = sum(ticket_sales.values())
    avg_ticket_price = (ticket_sales['stage1'] * stage1_price + ticket_sales['stage2'] * stage2_price +
                        ticket_sales['stage3'] * stage3_price + ticket_sales['door'] * door_price) / sold_tickets if sold_tickets > 0 else 0

    ticket_revenue = (ticket_sales['stage1'] * stage1_price + ticket_sales['stage2'] * stage2_price +
                      ticket_sales['stage3'] * stage3_price + ticket_sales['door'] * door_price)
    net_profit = new_budget - risk_amount - marketing_cost + ticket_revenue
    bar_revenue = estimated_guests * 1200

    df = pd.DataFrame({
        'Бюджет': [events['Neuropunk']['budget'], events['Bass Vibration']['budget'], available_budget],
        'Количество гостей': [events['Neuropunk']['guests'], events['Bass Vibration']['guests'], estimated_guests],
        'Стоимость входa': [events['Neuropunk']['ticket_price'], events['Bass Vibration']['ticket_price'], avg_ticket_price],
        'Мероприятие': ['Neuropunk', 'Bass Vibration', display_event_name]
    })

    # График
    fig = go.Figure()
    colors = {'Neuropunk': 'yellow', 'Bass Vibration': 'green', 'Hardline': '#ff005e'}

    max_guests = max(df['Количество гостей'])  # Ограничение графика по максимальному количеству гостей

    for _, row in df.iterrows():
        fig.add_shape(type="line", x0=row['Количество гостей'], y0=0, x1=row['Количество гостей'], y1=row['Стоимость входa'],
                      line=dict(color='#555555', dash="dash", width=1), layer='below')  # Пунктирные линии от точек
        fig.add_shape(type="line", x0=0, y0=row['Стоимость входa'], x1=row['Количество гостей'], y1=row['Стоимость входa'],
                      line=dict(color='#555555', dash="dash", width=1), layer='below')  # Пунктирные линии от точек

        # Цветные точки и текст
        fig.add_trace(go.Scatter(
            x=[row['Количество гостей']],
            y=[row['Стоимость входa']],
            mode='markers+text',
            name=row['Мероприятие'],
            marker=dict(size=15, color=colors[row['Мероприятие']], opacity=1),
            text=[row['Мероприятие']],
            textposition='top center',
            textfont=dict(color='white', size=12),
            showlegend=False
        ))

    # Сетка графика (темнее)
    for i in range(0, int(max_guests) + 1, 100):
        fig.add_shape(type="line", x0=i, y0=0, x1=i, y1=max(df['Стоимость входa']),
                      line=dict(color='#333333', width=1), layer='below')  # Темные вертикальные линии
    for i in range(0, int(max(df['Стоимость входa'])) + 1, 500):
        fig.add_shape(type="line", x0=0, y0=i, x1=max_guests, y1=i,
                      line=dict(color='#333333', width=1), layer='below')  # Темные горизонтальные линии

    fig.update_layout(
        xaxis_title="Количество гостей",
        yaxis_title="Усреднённая стоимость билета (₽)",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white', size=12),
        height=500,
        width=None,  # График во всю ширину экрана
        margin=dict(l=10, r=10, t=10, b=30)  # Минимальные отступы для графика
    )

    st.plotly_chart(fig, use_container_width=True)  # Включил растягивание на всю ширину

    # Убрана легенда под графиком (по вашему требованию)

    # Метрики
    st.subheader("Расчетные данные")
    col_metrics1, col_metrics2, col_metrics3, col_metrics4 = st.columns(4)
    with col_metrics1:
        st.metric("Маркетинг", f"{marketing_cost:,.0f}₽ ({marketing_percentage:.0%})")
    with col_metrics2:
        remaining_budget = available_budget - marketing_cost
        st.metric("Остаток бюджета", f"{remaining_budget:,.0f}₽")
    with col_metrics3:
        st.metric("Количество гостей", f"{estimated_guests:,d}")
    with col_metrics4:
        st.metric("Выручка от продажи билетов", f"{ticket_revenue:,.0f}₽")

    # Распределение билетов
    st.subheader("Распределение билетов")
    col_ts1, col_ts2, col_ts3, col_ts4 = st.columns([0.25, 0.25, 0.25, 0.25])  # Минимальная ширина колонок
    with col_ts1: st.metric("Этап 1", f"{ticket_sales['stage1']} шт. по {stage1_price}₽")
    with col_ts2: st.metric("Этап 2", f"{ticket_sales['stage2']} шт. по {stage2_price}₽")
    with col_ts3: st.metric("Этап 3", f"{ticket_sales['stage3']} шт. по {stage3_price}₽")
    with col_ts4: st.metric("На входе", f"{ticket_sales['door']} шт. по {door_price}₽")

    # Выручка
    st.subheader("Выручка")
    col_revenue1, col_revenue2 = st.columns([1, 1])  # Равные колонки для выравнивания
    with col_revenue1:
        st.metric("Выручка бара", f"{bar_revenue:,.0f}₽")
    with col_revenue2:
        st.metric("Чистая прибыль", f"{net_profit:,.0f}₽")

if __name__ == "__main__":
    main()
