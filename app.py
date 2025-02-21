import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import re

st.set_page_config(page_title="Прогноз на мероприятие", layout="wide")

def get_next_version(base_name, existing_events, versions):
    # Суффикс V# добавляется только для новых версий прошлых событий (Neuropunk, Bass Vibration), но не для Hardline
    if base_name in existing_events and base_name != 'Hardline':
        version = 2
        while f"{base_name} V{version}" in versions:
            version += 1
        return f"{base_name} V{version}"
    return base_name  # Для Hardline возвращаем оригинальное имя без изменений

def generate_color(base_name):
    # Генерируем уникальные цвета для новых версий событий на основе базового имени
    color_map = {
        'Neuropunk': '#ffcc00',  # Базовый цвет для Neuropunk V2 и далее
        'Bass Vibration': '#00ffcc'  # Базовый цвет для Bass Vibration V2 и далее
    }
    base_color = color_map.get(base_name, '#ff005e')  # Для Hardline используем оригинальный цвет
    if base_name == 'Hardline':
        return '#ff005e'  # Оригинальный цвет для Hardline
    # Если это новая версия, добавляем вариацию цвета (например, меняем яркость или оттенок)
    match = re.search(r'V(\d+)$', base_name)
    if match:
        version = int(match.group(1))
        # Генерируем уникальный оттенок на основе версии (например, увеличиваем насыщенность)
        r, g, b = tuple(int(base_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        if base_name.startswith('Neuropunk'):
            r = min(255, r + (version - 2) * 20)  # Увеличиваем красный для Neuropunk
            g = max(0, g - (version - 2) * 10)  # Уменьшаем зелёный
        elif base_name.startswith('Bass Vibration'):
            g = min(255, g + (version - 2) * 20)  # Увеличиваем зелёный для Bass Vibration
            b = max(0, b - (version - 2) * 10)  # Уменьшаем синий
        return f'#{r:02x}{g:02x}{b:02x}'
    return base_color  # Для базовых версий или Hardline

def main():
    st.title("Прогноз на мероприятие")

    # Словарь с предустановленными мероприятиями (только для расчётов, не для полей ввода)
    events = {
        'Neuropunk': {'budget': 500000, 'guests': 500, 'ticket_price': 2000, 'marketing_percent': 0.3, 'fame_factor': 1.5},
        'Bass Vibration': {'budget': 120000, 'guests': 80, 'ticket_price': 1200, 'marketing_percent': 0.3, 'fame_factor': 1.0},
        'Hardline': {'budget': 150000, 'ticket_price': 600, 'marketing_percent': 0.3, 'fame_factor': 1.0}
    }

    # Определение дефолтных значений для полей
    default_budget = 120000  # Фиксированное начальное значение для всех
    default_price = {
        'Neuropunk': 1200,  # Начальное значение по умолчанию
        'Bass Vibration': 1200,  # Начальное значение по умолчанию
        'Hardline': 600  # Начальное значение для Hardline: 600₽
    }
    default_risk = 0  # Начальное значение для всех: 0
    default_marketing = 30  # Начальное значение для всех: 30 (как int)

    # Инициализация session_state для отслеживания версий событий и значений полей
    if 'event_versions' not in st.session_state:
        st.session_state.event_versions = {name: name for name in events.keys()}  # Базовые имена как начальные версии
    if 'budget_values' not in st.session_state:
        st.session_state.budget_values = {name: default_budget for name in events.keys()}  # Начальное значение 120,000₽ для всех
    if 'price_values' not in st.session_state:
        st.session_state.price_values = {name: default_price[name] for name in events.keys()}  # Начальные значения цен
    if 'risk_values' not in st.session_state:
        st.session_state.risk_values = {name: default_risk for name in events.keys()}  # Начальное значение 0 для всех
    if 'marketing_values' not in st.session_state:
        st.session_state.marketing_values = {name: default_marketing for name in events.keys()}  # Начальное значение 30% для всех (как int)

    # Ввод данных
    col1, col2, col3, col4 = st.columns(4)

    # Выбор названия мероприятия — оригинальные имена, с суффиксом V# для новых версий прошлых событий
    base_event_names = list(events.keys())
    current_event_name = col1.selectbox("Название мероприятия:", options=base_event_names, index=2, key="event_name")
    display_event_name = get_next_version(current_event_name, events, st.session_state.event_versions)  # Генерируем имя с приставкой V# только для новых версий

    # Обновляем версию события в session_state, если выбрано новое
    if display_event_name != st.session_state.event_versions.get(current_event_name, current_event_name):
        st.session_state.event_versions[current_event_name] = display_event_name

    # Поля ввода с начальными значениями, сохраняющими пользовательские изменения
    # Убеждаемся, что значения не сбрасываются на дефолтные или из events
    new_budget = col1.number_input("Общий бюджет (₽):", min_value=0, value=st.session_state.budget_values.get(current_event_name, default_budget), step=1000, key=f"budget_{current_event_name}")
    new_price = col2.number_input("Цена входа (₽):", min_value=1, value=st.session_state.price_values.get(current_event_name, default_price[current_event_name]), step=100, key=f"price_{current_event_name}")
    risk_amount = col3.number_input("Финансовые риски (₽):", min_value=0, value=st.session_state.risk_values.get(current_event_name, default_risk), step=5000, key=f"risk_{current_event_name}")
    # Исправляем slider, чтобы гарантировать, что value — это int, а не список или другой тип
    marketing_value = st.session_state.marketing_values.get(current_event_name, default_marketing)
    if not isinstance(marketing_value, int):
        marketing_value = default_marketing  # Убедимся, что значение — int
    marketing_percentage = col4.slider("Маркетинг (%):", min_value=0, max_value=100, value=marketing_value, step=5, key=f"marketing_{current_event_name}") / 100

    # Сохраняем пользовательские значения в session_state перед расчётами
    st.session_state.budget_values[current_event_name] = new_budget
    st.session_state.price_values[current_event_name] = new_price
    st.session_state.risk_values[current_event_name] = risk_amount
    st.session_state.marketing_values[current_event_name] = int(marketing_percentage * 100)  # Сохраняем как int

    # Фактор известности: 1.5 только для "Neuropunk", иначе 1.0
    fame_factor = 1.5 if current_event_name == 'Neuropunk' else 1.0

    # Расчет маркетингового бюджета как процент от общего бюджета
    marketing_cost = max(0, new_budget * marketing_percentage)
    available_budget = new_budget - risk_amount
    remaining_budget = available_budget - marketing_cost

    base_guests = 0
    base_marketing_effectiveness = 0.00223  # Настроен для 80 гостей при 120,000₽, 1,200₽, 30%
    marketing_effectiveness_slope = 0.004

    # Обновляем marketing_effectiveness с учётом fame_factor
    marketing_effectiveness = base_marketing_effectiveness + marketing_effectiveness_slope * (fame_factor - 1.0)

    # Рассчитываем гостей для всех мероприятий по формуле (без предустановленных значений для Hardline)
    marketing_guests = marketing_cost * marketing_effectiveness * fame_factor
    # Общий avg_ticket_price
    avg_ticket_price = (events['Neuropunk']['ticket_price'] + events['Bass Vibration']['ticket_price'] + events['Hardline']['ticket_price']) / 3  # 1,600₽
    # Исправляем price_factor без ограничения до [0, 1], но с учётом цены Bass Vibration для Hardline
    price_diff = (new_price - avg_ticket_price) / avg_ticket_price
    if current_event_name == 'Hardline' and new_price == events['Bass Vibration']['ticket_price']:  # Если цена = 1,200 для Hardline
        price_factor = 1  # Устанавливаем price_factor = 1 для равенства с Bass Vibration
    elif current_event_name in ['Bass Vibration', 'Neuropunk'] and new_price == events[current_event_name]['ticket_price']:  # Если цена не изменена для других
        price_factor = 1
    else:
        price_factor = 1 - 0.3 * price_diff  # Корректируем только при изменении цены
    estimated_guests = max(0, round((base_guests + marketing_guests) * price_factor))

    # Для "Neuropunk" и "Bass Vibration" при точном совпадении параметров используем предустановленные guests
    if current_event_name in ['Neuropunk', 'Bass Vibration']:
        if (abs(new_budget - events[current_event_name]['budget']) < 1000 and  # Допуск в 1000₽ для бюджета
            new_price == events[current_event_name]['ticket_price'] and 
            abs(marketing_percentage - events[current_event_name]['marketing_percent']) < 0.01):  # Допуск 1% для маркетинга
            estimated_guests = events[current_event_name]['guests']

    total_profit = new_budget - (risk_amount + marketing_cost) + (new_price * estimated_guests)
    net_profit = total_profit - remaining_budget

    # Обновляем данные для графика с выбранным названием (без суффиксов для прошлых событий, с V# для текущего нового события)
    df = pd.DataFrame({
        'Бюджет': [events['Neuropunk']['budget'], events['Bass Vibration']['budget'], available_budget],
        'Количество гостей': [events['Neuropunk']['guests'], events['Bass Vibration']['guests'], estimated_guests],
        'Стоимость входа': [events['Neuropunk']['ticket_price'], events['Bass Vibration']['ticket_price'], new_price],
        'Мероприятие': ['Neuropunk', 'Bass Vibration', display_event_name if current_event_name in ['Neuropunk', 'Bass Vibration'] else current_event_name]  # Оригинальные имена для прошлых, V# только для текущих новых версий
    })

    # График и чекбоксы в двух колонках
    col_left, col_right = st.columns([3, 1])

    with col_left:
        fig = go.Figure()
        colors = {
            'Neuropunk': 'yellow',  # Оригинальный цвет для прошлых Neuropunk
            'Bass Vibration': 'green',  # Оригинальный цвет для прошлых Bass Vibration
            'Hardline': '#ff005e',  # Оригинальный цвет для Hardline (без V#)
        }
        # Динамически добавляем цвета для всех возможных версий событий до использования
        for base_name in ['Neuropunk', 'Bass Vibration']:
            version = 2
            while True:
                version_name = f"{base_name} V{version}"
                if version_name not in colors:
                    colors[version_name] = generate_color(version_name)
                version += 1
                if version > 10:  # Ограничиваем количество версий для производительности
                    break

        for _, row in df.iterrows():
            display_name = row['Мероприятие']
            if display_name in ['Neuropunk', 'Bass Vibration'] and display_name == current_event_name:
                display_name = get_next_version(display_name, events, st.session_state.event_versions)  # Добавляем V# только для текущего нового события
            if display_name == 'Neuropunk' and not st.session_state.get('show_neuropunk', True):
                continue
            if display_name == 'Bass Vibration' and not st.session_state.get('show_bass_vibration', True):
                continue
            if display_name == 'Hardline' and not st.session_state.get('show_hardline', True):
                continue
            fig.add_shape(type="line", x0=row['Количество гостей'], y0=0, x1=row['Количество гостей'], y1=row['Стоимость входа'], 
                         line=dict(color='grey', dash="dot", width=1), layer='below')
            fig.add_shape(type="line", x0=0, y0=row['Стоимость входа'], x1=row['Количество гостей'], y1=row['Стоимость входа'], 
                         line=dict(color='grey', dash="dot", width=1), layer='below')
            marker_color = colors[display_name]  # Используем оригинальные или новые цвета
            fig.add_trace(go.Scatter(
                x=[row['Количество гостей']],
                y=[row['Стоимость входа']],
                mode='markers+text',
                name=display_name,
                marker=dict(size=15, color=marker_color, opacity=1),
                text=[display_name],
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
            st.markdown('<span style="color: yellow;">Neuropunk</span>', unsafe_allow_html=True)  # Оригинальный цвет для прошлых событий
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('<div class="checkbox-item">', unsafe_allow_html=True)
            st.checkbox("", value=True, key="show_bass_vibration", label_visibility="collapsed")
            st.markdown('<span style="color: green;">Bass Vibration</span>', unsafe_allow_html=True)  # Оригинальный цвет для прошлых событий
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('<div class="checkbox-item">', unsafe_allow_html=True)
            st.checkbox("", value=True, key="show_hardline", label_visibility="collapsed")
            st.markdown(f'<span style="color: #ff005e;">{current_event_name}</span>', unsafe_allow_html=True)  # Оригинальный цвет для Hardline (без V#)
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # Метрики во всей ширине страницы под графиком
    st.subheader("Расчетные данные")
    col_metrics1, col_metrics2, col_metrics3, col_metrics4, col_metrics5 = st.columns(5)

    with col_metrics1:
        st.metric(f"Маркетинг ({marketing_percentage:.0%})", f"{marketing_cost:,.0f}₽")

    with col_metrics2:
        st.metric("Остаток бюджета", f"{remaining_budget:,.0f}₽")

    with col_metrics3:
        st.metric("Расчетное количество гостей", f"{estimated_guests:,d}")

    with col_metrics4:
        st.metric("Примерная прибыль", f"{total_profit:,.0f}₽")

    with col_metrics5:
        st.metric("Чистая прибыль", f"{net_profit:,.0f}₽")

if __name__ == "__main__":
    main()
