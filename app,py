import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import re
import math

st.set_page_config(page_title="Прогноз на мероприятие", layout="wide", initial_sidebar_state="collapsed")

def get_next_version(base_name, existing_events, versions):
    if base_name in existing_events and base_name != 'Hardline I':
        version = 2
        while f"{base_name} V{version}" in versions:
            version += 1
        return f"{base_name} V{version}"
    return base_name

def generate_color(base_name):
    color_map = {'Neuropunk': '#ffcc00', 'Bass Vibration IV': '#00ffcc'}
    base_color = color_map.get(base_name, '#ff005e')
    if base_name == 'Hardline I':
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

def calculate_guests_and_price(stage1_price, stage1_limit, stage2_price, stage2_limit, stage3_price, stage3_limit,
                                door_price, door_limit, marketing_guests, free_tickets, fame_factor, max_iterations=2):
    total_tickets_available = stage1_limit + stage2_limit + stage3_limit + door_limit
    if total_tickets_available == 0:
        return 0, {'stage1': 0, 'stage2': 0, 'stage3': 0, 'door': 0}, 0, 0

    w1 = stage1_limit / total_tickets_available if total_tickets_available > 0 else 0
    w2 = stage2_limit / total_tickets_available if total_tickets_available > 0 else 0
    w3 = stage3_limit / total_tickets_available if total_tickets_available > 0 else 0
    w4 = door_limit / total_tickets_available if total_tickets_available > 0 else 0

    k = 0.0038
    estimated_guests = 0
    avg_ticket_price = 0
    for _ in range(max_iterations):
        weighted_price = w1 * stage1_price + w2 * stage2_price + w3 * stage3_price + w4 * door_price
        price_factor = math.exp(-k * weighted_price)
        estimated_guests = min(total_tickets_available, max(0, round(marketing_guests * price_factor)))

        ticket_sales = {
            'stage1': min(estimated_guests, stage1_limit) if estimated_guests > 0 else 0,
            'stage2': min(max(0, estimated_guests - stage1_limit), stage2_limit) if estimated_guests > stage1_limit else 0,
            'stage3': min(max(0, estimated_guests - stage1_limit - stage2_limit), stage3_limit) if estimated_guests > stage1_limit + stage2_limit else 0,
            'door': min(max(0, estimated_guests - stage1_limit - stage2_limit - stage3_limit), door_limit) if door_limit > 0 else max(0, estimated_guests - stage1_limit - stage2_limit - stage3_limit)
        }
        sold_tickets = sum(ticket_sales.values())
        ticket_revenue = (ticket_sales['stage1'] * stage1_price +
                          ticket_sales['stage2'] * stage2_price +
                          ticket_sales['stage3'] * stage3_price +
                          ticket_sales['door'] * door_price)
        avg_ticket_price = ticket_revenue / sold_tickets if sold_tickets > 0 else weighted_price

    return estimated_guests, ticket_sales, avg_ticket_price, ticket_revenue

def main():
    st.title("Прогноз на мероприятие")

    events = {
        'Neuropunk': {'budget': 500000, 'guests': 500, 'ticket_price': 2000, 'marketing_percent': 0.2, 'fame_factor': 10.15, 'risk_amount': 0},
        'Bass Vibration IV': {'budget': 113500, 'guests': 110, 'ticket_price': 1200, 'marketing_percent': 0.2, 'fame_factor': 1.0, 'risk_amount': 96000},
        'Hardline I': {'budget': 120000, 'guests': 140, 'ticket_price': 940, 'marketing_percent': 0.2, 'fame_factor': 1.0, 'risk_amount': 25000}
    }

    default_budget, default_risk, default_marketing = 120000, 0, 20
    default_pre_sale = {
        'stage1_price': 500, 'stage1_limit': 50,
        'stage2_price': 600, 'stage2_limit': 50,
        'stage3_price': 700, 'stage3_limit': 50,
        'door_price': 1000, 'door_limit': 999
    }

    hardline_pre_sale = {
        'stage1_price': 400, 'stage1_limit': 100,
        'stage2_price': 400, 'stage2_limit': 100,
        'stage3_price': 700, 'stage3_limit': 50,
        'door_price': 1000, 'door_limit': 849
    }
    bass_vibration_pre_sale = {
        'stage1_price': 900, 'stage1_limit': 21,
        'stage2_price': 1100, 'stage2_limit': 31,
        'stage3_price': 1500, 'stage3_limit': 21,
        'door_price': 1000, 'door_limit': 0
    }
    neuropunk_pre_sale = {
        'stage1_price': 1000, 'stage1_limit': 100,
        'stage2_price': 1200, 'stage2_limit': 100,
        'stage3_price': 1400, 'stage3_limit': 100,
        'door_price': 1800, 'door_limit': 999
    }

    if 'event_versions' not in st.session_state:
        st.session_state.event_versions = {name: name for name in events.keys()}
    if 'budget_values' not in st.session_state:
        st.session_state.budget_values = {name: events[name]['budget'] for name in events.keys()}
        st.session_state.budget_values['New'] = default_budget
    if 'risk_values' not in st.session_state:
        st.session_state.risk_values = {name: events[name]['risk_amount'] for name in events.keys()}
        # Установлено значение расходов для New на 60,000 по умолчанию
        st.session_state.risk_values['New'] = 60000
    if 'marketing_values' not in st.session_state:
        st.session_state.marketing_values = {name: int(events[name]['marketing_percent'] * 100) for name in events.keys()}
        st.session_state.marketing_values['New'] = default_marketing
    if 'pre_sale_values' not in st.session_state:
        st.session_state.pre_sale_values = {name: default_pre_sale.copy() for name in events.keys()}
        st.session_state.pre_sale_values['New'] = default_pre_sale.copy()
        st.session_state.pre_sale_values['Hardline I'] = hardline_pre_sale.copy()
        st.session_state.pre_sale_values['Bass Vibration IV'] = bass_vibration_pre_sale.copy()
        st.session_state.pre_sale_values['Neuropunk'] = neuropunk_pre_sale.copy()
    if 'checkbox_states' not in st.session_state:
        st.session_state.checkbox_states = {'Neuropunk': True, 'Bass Vibration IV': True, 'Hardline I': True, 'New': True}
    if 'free_tickets' not in st.session_state:
        st.session_state.free_tickets = {'Neuropunk': 20, 'Bass Vibration IV': 35, 'Hardline I': 21, 'New': 0}
    if 'current_event' not in st.session_state:
        st.session_state.current_event = 'New'

    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.subheader("Настройки")
        col_settings_left, col_settings_middle, col_settings_right = st.columns([1, 0.25, 1])

        event_options = list(events.keys()) + ['New']
        current_event_name = col_settings_left.selectbox(
            "Мероприятие:", options=event_options,
            index=event_options.index(st.session_state.current_event),
            key="event_name"
        )
        st.session_state.current_event = current_event_name
        display_event_name = get_next_version(current_event_name, events, st.session_state.event_versions)

        if current_event_name != 'New' and display_event_name != st.session_state.event_versions.get(current_event_name, current_event_name):
            st.session_state.event_versions[current_event_name] = display_event_name

        marketing_percentage = col_settings_left.slider(
            "Маркетинг (%):", 0, 100, st.session_state.marketing_values.get(current_event_name, default_marketing), 5,
            key=f"marketing_{current_event_name}"
        ) / 100
        # Заменил "Проходки:" на "Free:"
        free_tickets = col_settings_middle.number_input(
            "Free:", 0, value=st.session_state.free_tickets.get(current_event_name, 0), step=1,
            key=f"free_{current_event_name}"
        )
        new_budget = col_settings_right.number_input(
            "Бюджет (₽):", 0, value=st.session_state.budget_values.get(current_event_name, default_budget), step=1000,
            key=f"budget_{current_event_name}"
        )
        risk_amount = col_settings_right.number_input(
            "Расходы (₽):", 0, value=st.session_state.risk_values.get(current_event_name, default_risk), step=5000,
            key=f"risk_{current_event_name}"
        )

        st.session_state.budget_values[current_event_name] = new_budget
        st.session_state.risk_values[current_event_name] = risk_amount
        st.session_state.marketing_values[current_event_name] = int(marketing_percentage * 100)
        st.session_state.free_tickets[current_event_name] = free_tickets

    with col_right:
        st.subheader("Продажа")
        col_stage1, col_stage2, col_stage3, col_door = st.columns(4)

        pre_sale = st.session_state.pre_sale_values[current_event_name]
        with col_stage1:
            stage1_price = st.number_input("Цена Этап 1", 1, value=pre_sale['stage1_price'], step=100, key=f"stage1_price_{current_event_name}")
            stage1_limit = st.number_input("Количество", 0, value=pre_sale['stage1_limit'], step=1, key=f"stage1_limit_{current_event_name}")
        with col_stage2:
            stage2_price = st.number_input("Цена Этап 2", 1, value=pre_sale['stage2_price'], step=100, key=f"stage2_price_{current_event_name}")
            stage2_limit = st.number_input("Количество", 0, value=pre_sale['stage2_limit'], step=1, key=f"stage2_limit_{current_event_name}")
        with col_stage3:
            stage3_price = st.number_input("Цена Этап 3", 1, value=pre_sale['stage3_price'], step=100, key=f"stage3_price_{current_event_name}")
            stage3_limit = st.number_input("Количество", 0, value=pre_sale['stage3_limit'], step=1, key=f"stage3_limit_{current_event_name}")
        with col_door:
            door_price = st.number_input("Цена На входе", 1, value=pre_sale['door_price'], step=100, key=f"door_price_{current_event_name}")
            door_limit = st.number_input("Количество", 0, value=pre_sale['door_limit'], step=1, key=f"door_limit_{current_event_name}")

        st.session_state.pre_sale_values[current_event_name] = {
            'stage1_price': stage1_price, 'stage1_limit': stage1_limit,
            'stage2_price': stage2_price, 'stage2_limit': stage2_limit,
            'stage3_price': stage3_price, 'stage3_limit': stage3_limit,
            'door_price': door_price, 'door_limit': door_limit
        }

    marketing_cost = new_budget * marketing_percentage
    min_fame, max_fame = 1.0, 10.15
    min_marketing, max_marketing = 22700, 100000
    fame_factor = min_fame + (max_fame - min_fame) * min(1.0, max(0.0, (marketing_cost - min_marketing) / (max_marketing - min_marketing))))
    if current_event_name in events:
        fame_factor = events[current_event_name]['fame_factor']

    marketing_effectiveness = 0.2685
    marketing_guests = marketing_cost * marketing_effectiveness * fame_factor

    estimated_guests, ticket_sales, avg_ticket_price, ticket_revenue = calculate_guests_and_price(
        stage1_price, stage1_limit, stage2_price, stage2_limit, stage3_price, stage3_limit,
        door_price, door_limit, marketing_guests, free_tickets, fame_factor
    )

    total_attendance = estimated_guests + free_tickets
    profit = new_budget - risk_amount - marketing_cost + ticket_revenue
    bar_revenue = total_attendance * 1300
    remaining_budget = new_budget - risk_amount - marketing_cost
    net_profit = profit - risk_amount

    df_data = {
        'Бюджет': [],
        'Количество гостей': [],
        'Стоимость входa': [],
        'Мероприятие': []
    }
    for event in events.keys():
        if event == current_event_name:
            df_data['Бюджет'].append(new_budget - risk_amount)
            df_data['Количество гостей'].append(total_attendance)
            df_data['Стоимость входa'].append(avg_ticket_price)
        else:
            df_data['Бюджет'].append(events[event]['budget'] - events[event]['risk_amount'])
            df_data['Количество гостей'].append(events[event]['guests'] + st.session_state.free_tickets.get(event, 0))
            df_data['Стоимость входa'].append(events[event]['ticket_price'])
        df_data['Мероприятие'].append(event)

    if current_event_name == 'New':
        df_data['Бюджет'].append(new_budget - risk_amount)
        df_data['Количество гостей'].append(total_attendance)
        df_data['Стоимость входa'].append(avg_ticket_price)
        df_data['Мероприятие'].append(display_event_name)

    df = pd.DataFrame(df_data)

    fig = go.Figure()
    colors = {'Neuropunk': 'yellow', 'Bass Vibration IV': 'green', 'Hardline I': '#ff005e', 'New': '#ff00ff'}
    visibility = {
        'Neuropunk': st.session_state.checkbox_states['Neuropunk'],
        'Bass Vibration IV': st.session_state.checkbox_states['Bass Vibration IV'],
        'Hardline I': st.session_state.checkbox_states['Hardline I'],
        'New': st.session_state.checkbox_states.get('New', True) and current_event_name == 'New'
    }

    max_guests = max(df['Количество гостей'])

    for _, row in df.iterrows():
        event_name = row['Мероприятие']
        base_event_name = 'New' if event_name.startswith('New') else event_name
        if base_event_name in events:
            base_event_name = event_name
        if visibility.get(base_event_name, False):
            fig.add_shape(type="line", x0=row['Количество гостей'], y0=0, x1=row['Количество гостей'], y1=row['Стоимость входa'],
                          line=dict(color='#555555', dash="dash", width=1), layer='below')
            fig.add_shape(type="line", x0=0, y0=row['Стоимость входa'], x1=row['Количество гостей'], y1=row['Стоимость входa'],
                          line=dict(color='#555555', dash="dash", width=1), layer='below')

            fig.add_trace(go.Scatter(
                x=[row['Количество гостей']],
                y=[row['Стоимость входa']],
                mode='markers+text',
                name=event_name,
                marker=dict(size=15, color=colors.get(base_event_name, '#ff00ff'), opacity=1),
                text=[event_name],
                textposition='top center',
                textfont=dict(color='white', size=12),
                showlegend=False
            ))

    for i in range(0, int(max_guests) + 1, 100):
        fig.add_shape(type="line", x0=i, y0=0, x1=i, y1=max(df['Стоимость входa']),
                      line=dict(color='#333333', width=1), layer='below')
    for i in range(0, int(max(df['Стоимость входa'])) + 1, 500):
        fig.add_shape(type="line", x0=0, y0=i, x1=max_guests, y1=i,
                      line=dict(color='#333333', width=1), layer='below')

    fig.update_layout(
        xaxis_title="Количество гостей",
        yaxis_title="Усреднённая стоимость билета (₽)",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white', size=12),
        height=500,
        width=None,
        margin=dict(l=10, r=10, t=10, b=30)
    )

    st.plotly_chart(fig, use_container_width=True)

    col_check1, col_check2, col_check3, col_check4 = st.columns(4)
    with col_check1:
        show_neuropunk = st.checkbox("Neuropunk", value=st.session_state.checkbox_states['Neuropunk'], key="show_neuropunk")
        st.session_state.checkbox_states['Neuropunk'] = show_neuropunk
    with col_check2:
        show_bass_vibration = st.checkbox("Bass Vibration IV", value=st.session_state.checkbox_states['Bass Vibration IV'], key="show_bass_vibration")
        st.session_state.checkbox_states['Bass Vibration IV'] = show_bass_vibration
    with col_check3:
        show_hardline = st.checkbox("Hardline I", value=st.session_state.checkbox_states['Hardline I'], key="show_hardline")
        st.session_state.checkbox_states['Hardline I'] = show_hardline
    with col_check4:
        show_new = st.checkbox("New", value=st.session_state.checkbox_states.get('New', True), key="show_new")
        st.session_state.checkbox_states['New'] = show_new

    st.subheader("Расчетные данные")
    col_metrics1, col_metrics2, col_metrics3, col_metrics4 = st.columns(4)
    with col_metrics1:
        st.metric("Маркетинг", f"{marketing_cost:,.0f}₽ ({marketing_percentage:.0%})")
    with col_metrics2:
        st.metric("Остаток бюджета", f"{remaining_budget:,.0f}₽")
    # Убраны скобочки и информация о проходках в метрике "Количество гостей"
    with col_metrics3:
        st.metric("Количество гостей", f"{total_attendance:,d}")
    with col_metrics4:
        st.metric("Выручка от продажи билетов", f"{ticket_revenue:,.0f}₽")

    st.subheader("Распределение билетов")
    col_ts1, col_ts2, col_ts3, col_ts4 = st.columns([0.25, 0.25, 0.25, 0.25])
    with col_ts1: st.metric("Этап 1", f"{ticket_sales['stage1']} шт. по {stage1_price}₽")
    with col_ts2: st.metric("Этап 2", f"{ticket_sales['stage2']} шт. по {stage2_price}₽")
    with col_ts3: st.metric("Этап 3", f"{ticket_sales['stage3']} шт. по {stage3_price}₽")
    with col_ts4: st.metric("На входе", f"{ticket_sales['door']} шт. по {door_price}₽")

    st.subheader("Выручка")
    col_revenue1, col_revenue2, col_revenue3 = st.columns([1, 1, 1])
    with col_revenue1:
        st.metric("Выручка бара", f"{bar_revenue:,.0f}₽")
    with col_revenue2:
        st.metric("Прибыль", f"{profit:,.0f}₽")
    with col_revenue3:
        st.metric("Чистая прибыль", f"{net_profit:,.0f}₽")

if __name__ == "__main__":
    main()
