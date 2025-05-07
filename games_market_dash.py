'''
Приветствую! Если вы читаете эти комменты, то скорее всего всё работает и вы хотите посмотреть на код, или ничего не работает и вы хотите
посмотреть, что здесь намудрили. В любом случае, спасибо за внимание и уделенное моему тестовому заданию время!

Пара пояснительных комментариев к заданию:
1. В задании не указаны разрешенные библиотеки, кроме plotly. Я исхожу из того, что pandas и различные модули plotly разрешены как 
стандартный инструментарий в тулбоксе аналитика.
2. В задании не уточнено, как именно конвертить рейтинг в числовой вид. Я выбрал метод присвоения минимального рекомендованного 
возраста по версии ERSB.
3. Обычно я пишу комментарии на английском, но так как само задание на русском - то и комментарии здесь на русском.
4. Неясна среда и метод запуска приложения. Поэтому мы не используем CSS, dash_bootstrtap и прочие украшательства. На всякий случай к
файлу прикладывается requirements.txt.

Задать любые вопросы вы можете через dmitry.gaidai@gmail.com, в ТГ https://t.me/dmitry_helios или через вашего эйчара.
'''

# Начнем с импорта плотли, дэш, панды и глушилки для FutureWarning 
import warnings
warnings.filterwarnings('ignore', category=FutureWarning)
import pandas as pd
import dash
from dash import dcc, html, Output, Input
import plotly.express as px
import plotly.graph_objs as go

# Шаг 1: Причесываем данные.
df = pd.read_csv('games.csv') # Считаем csv в панду, с которой будем работать
df = df.dropna() # Очистим данные от пропусков
df = df[~df.apply(lambda x: x.astype(str).str.contains('tbd|nan', case=False)).any(axis=1)] # Удалим строки с 'tbd' или 'nan'
df = df[(df['Year_of_Release'] >= 1990) & (df['Year_of_Release'] <= 2010)] # Сохраним только 1990-2010

# Форсим числовые значения в рейтингах, чтобы избежать косяков с передачей str в плотли
df['User_Score'] = pd.to_numeric(df['User_Score'])
df['Critic_Score'] = pd.to_numeric(df['Critic_Score'])

# Теперь сконвертим рейтинги. Мы видим следующие значения в панде:
# ['E', 'M', 'T', 'E10+', 'AO', 'K-A']
# Рейтинг K-A - устаревший, до 98 года так называли рейтинг Е, 
# поэтому для начала заменим все 'K-A' на 'E':
df['Rating'] = df['Rating'].replace('K-A', 'E')

# Теперь перегоняем рейтинги в числовой вид. В задании не указано как именно конвертировать рейтинг, поэтому займемся самодурством и
# возьмем минимальный возраст для каждого рейтинга аккординг ту https://en.wikipedia.org/wiki/Entertainment_Software_Rating_Board#Ratings
# E - 0, E10+ - 10, T - 13, M - 17, AO - 18.
df['Rating'] = df['Rating'].replace({'E': 0, 'E10+': 10, 'T': 13, 'M': 17, 'AO': 18})
df['Rating'] = pd.to_numeric(df['Rating']) # Убедимся что рейтинг - числовой тип
df['Year_of_Release'] = pd.to_numeric(df['Year_of_Release'], downcast='integer') # И конвертируем Year_of_Release в INT64 

# На этом этапе у нас есть причесанная, аккуратная панда с корректными типами. Переходим к созданию дэшборда.


# Шаг 2: Дэшборд на dash
app = dash.Dash()

# Списки для фильтров, отсортируем по общему количеству игр для красоты
platform_counts = df['Platform'].value_counts()
platform_options = [{'label': f"{platform}", 'value': platform} 
                    for platform, count in platform_counts.items()]

genre_counts = df['Genre'].value_counts()
genre_options = [{'label': f"{genre}", 'value': genre} 
                 for genre, count in genre_counts.items()]

year_options = list(range(df['Year_of_Release'].min(), 
                           df['Year_of_Release'].max() + 1))

# Строим layout
app.layout = html.Div([
    html.H1('История игровой индустрии'),
    html.P('Включает в себя информацию о различных платформах, жанрах, годах выпуска, рейтингах и оценках пользователей с 1990 по 2010. Используйте фильтры по платформам, жанрам и годам выпуска, чтобы уточнить данные.'),

    # Строим фильтры
    html.Div([
        html.Div([
            html.Label('Платформы:'),
            dcc.Dropdown(
                id='platform-dropdown',
                options=platform_options,
                multi=True,
                value=[]
            )
        ], style={'width': '30%', 'display': 'inline-block'}),
        
        html.Div([
            html.Label('Жанры:'),
            dcc.Dropdown(
                id='genre-dropdown',
                options=genre_options,
                multi=True,
                value=[]
            )
        ], style={'width': '30%', 'display': 'inline-block'}),
        
        html.Div([
            html.Label('Годы выпуска:'),
            dcc.RangeSlider(
                id='year-slider',
                min=1990,
                max=2010,
                value=[1990, 2010],
                marks={str(year): str(year) for year in range(1990, 2011, 5)}, # Проставляем числа вручную, не через min и max, чтобы интуитивно понимать интервалы и чтобы было consistent вне зависимости от активных фильтров
                step=1
            )
        ], style={'width': '40%', 'display': 'inline-block'})
    ]),

    # Строим графики
    html.Div([  # Первые 3 в своем враппере
        html.Div([
            dcc.Graph(id='total-games-graph', style={'height': '100%'}),
        ], style={'width': '33%', 'display': 'inline-block', 'vertical-align': 'top'}),

        html.Div([
            dcc.Graph(id='avg-user-score-graph', style={'height': '100%'}),
        ], style={'width': '33%', 'display': 'inline-block', 'vertical-align': 'top'}),

        html.Div([
            dcc.Graph(id='avg-critic-score-graph', style={'height': '100%'}),
        ], style={'width': '33%', 'display': 'inline-block', 'vertical-align': 'top'}),
    ], style={'width': '100%', 'height': '10vh', 'display': 'flex', 'justify-content': 'space-between', 'margin-bottom': '20px', 'margin-top': '20px'}),

    html.Div([  # Остальные 3 в своем враппере
        html.Div([
            dcc.Graph(id='avg-age-rating-graph'),
        ], style={'width': '30%', 'display': 'inline-block'}),

        html.Div([
            dcc.Graph(id='scatter-plot-graph'),
        ], style={'width': '40%', 'display': 'inline-block'}),

        html.Div([
            dcc.Graph(id='games-by-platform-year'),
        ], style={'width': '30%', 'display': 'inline-block'})
    ], style={'width': '100%', 'height': '40vh', 'display': 'flex', 'justify-content': 'space-between', 'margin-bottom': '20px'})
])

# На этом этапе у нас готова базовый лейаут, пора отрисовывать графики
# Шаг 3: callbacks

# Callback для графика 1 - общее количество игр
@app.callback(
    Output('total-games-graph', 'figure'),
    [Input('platform-dropdown', 'value'),
     Input('genre-dropdown', 'value'),
     Input('year-slider', 'value')]
)
def update_total_games(platforms, genres, year_range):
    # Используем .copy() чтобы не намудрить с исходной пандой
    filtered_df = df.copy()
    
    # Если фильтры пустые - используем всю панду целиком
    if platforms:
        filtered_df = filtered_df[filtered_df['Platform'].isin(platforms)]
    if genres:
        filtered_df = filtered_df[filtered_df['Genre'].isin(genres)]
    if year_range:
        filtered_df = filtered_df[filtered_df['Year_of_Release'].between(year_range[0], year_range[1])]
    
    total_games = len(filtered_df)
    
    return {
        'data': [go.Indicator(
            mode = "number",
            value = total_games,
            number = {'valueformat': '.0f', 'font': {'size': 48}},  # indicator пытается украсить наши цифры и округляет, поэтом дадим ему по шапке  
            )],
        'layout': go.Layout(title='Общее Количество Игр', margin=dict(t=30, b=0, l=0, r=0))
    }


# Callback для График 2: Число, Общая средняя оценка игроков
@app.callback(
    Output('avg-user-score-graph', 'figure'),
    [Input('platform-dropdown', 'value'),
     Input('genre-dropdown', 'value'),
     Input('year-slider', 'value')]
)
def update_avg_user_score(platforms, genres, year_range):
    # Используем .copy() чтобы не намудрить с исходной пандой
    filtered_df = df.copy()
    
    # Если фильтры пустые - используем всю панду целиком
    if platforms:
        filtered_df = filtered_df[filtered_df['Platform'].isin(platforms)]
    if genres:
        filtered_df = filtered_df[filtered_df['Genre'].isin(genres)]
    if year_range:
        filtered_df = filtered_df[filtered_df['Year_of_Release'].between(year_range[0], year_range[1])]
    
    avg_user_score = filtered_df['User_Score'].mean()
    
    return {
        'data': [go.Indicator(
            mode = "number",
            value = avg_user_score,
            number = {'valueformat': '.2f', 'font': {'size': 48}},
            )],
        'layout': go.Layout(title='Средняя Оценка Игроков', margin=dict(t=30, b=0, l=0, r=0))
    }   

# Callback для График 3: Число, Общая средняя оценка критиков
@app.callback(
    Output('avg-critic-score-graph', 'figure'),
    [Input('platform-dropdown', 'value'),
     Input('genre-dropdown', 'value'),
     Input('year-slider', 'value')]
)
def update_avg_critic_score(platforms, genres, year_range):
    # Используем .copy() чтобы не намудрить с исходной пандой
    filtered_df = df.copy()
    
    # Если фильтры пустые - используем всю панду целиком
    if platforms:
        filtered_df = filtered_df[filtered_df['Platform'].isin(platforms)]
    if genres:
        filtered_df = filtered_df[filtered_df['Genre'].isin(genres)]
    if year_range:
        filtered_df = filtered_df[filtered_df['Year_of_Release'].between(year_range[0], year_range[1])]
    
    avg_critic_score = filtered_df['Critic_Score'].mean()
    
    return {
        'data': [go.Indicator(
            mode = "number",
            value = avg_critic_score,
            number = {'valueformat': '.2f', 'font': {'size': 48}},   
            )],
        'layout': go.Layout(title='Средняя Оценка Критиков', margin=dict(t=30, b=0, l=0, r=0))
    }   

# Callback для График 4: Bar chart, средний возрастной рейтинг по жанрам
@app.callback(
    Output('avg-age-rating-graph', 'figure'),
    [Input('platform-dropdown', 'value'),
     Input('genre-dropdown', 'value'),
     Input('year-slider', 'value')]
)
def update_avg_age_rating(platforms, genres, year_range):
    # Используем .copy() чтобы не намудрить с исходной пандой
    filtered_df = df.copy()
    
    # Если фильтры пустые - используем всю панду целиком
    if platforms:
        filtered_df = filtered_df[filtered_df['Platform'].isin(platforms)]
    if genres:
        filtered_df = filtered_df[filtered_df['Genre'].isin(genres)]
    if year_range:
        filtered_df = filtered_df[filtered_df['Year_of_Release'].between(year_range[0], year_range[1])]
    
    # группируем по жанру
    avg_age_rating = filtered_df.groupby('Genre')['Rating'].mean().reset_index()
    
    return {
        'data': [go.Bar(
            x = avg_age_rating['Genre'],
            y = avg_age_rating['Rating'],
            )],
        'layout': go.Layout(
            title='Средний Возрастной Рейтинг по Жанрам',
            xaxis={'categoryorder': 'total descending'}
        )
    }

# Callback для График 5: Scatter plot с разбивкой по жанрам
@app.callback(
    Output('scatter-plot-graph', 'figure'),
    [Input('platform-dropdown', 'value'),
     Input('genre-dropdown', 'value'),
     Input('year-slider', 'value')]
)
def update_scatter_plot(platforms, genres, year_range):
    # Используем .copy() чтобы не намудрить с исходной пандой
    filtered_df = df.copy()
    
    # Если фильтры пустые - используем всю панду целиком
    if platforms:
        filtered_df = filtered_df[filtered_df['Platform'].isin(platforms)]
    if genres:
        filtered_df = filtered_df[filtered_df['Genre'].isin(genres)]
    if year_range:
        filtered_df = filtered_df[filtered_df['Year_of_Release'].between(year_range[0], year_range[1])]
    
    # рисуем scatter plot
    scatter_plot = px.scatter(filtered_df, x='Critic_Score', y='User_Score', color='Genre',
                             title='Оценки Критиков vs. Оценки Игроков по Жанрам')
    
    return scatter_plot

# Callback для Stacked area plot
@app.callback(
    Output('games-by-platform-year', 'figure'),
    [Input('platform-dropdown', 'value'),
     Input('genre-dropdown', 'value'),
     Input('year-slider', 'value')]
)

def update_games_by_platform_year(platforms, genres, year_range):
    # Используем .copy() чтобы не намудрить с исходной пандой
    filtered_df = df.copy()
    
    # Если фильтры пустые - используем всю панду целиком
    if platforms:
        filtered_df = filtered_df[filtered_df['Platform'].isin(platforms)]
    if genres:
        filtered_df = filtered_df[filtered_df['Genre'].isin(genres)]
    if year_range:
        filtered_df = filtered_df[filtered_df['Year_of_Release'].between(year_range[0], year_range[1])]
    
    # группируем по году и платформе
    games_count = filtered_df.groupby(['Year_of_Release', 'Platform']).size().reset_index(name='Count')
    
    fig = go.Figure()
    
    for platform in games_count['Platform'].unique():
        platform_data = games_count[games_count['Platform'] == platform]
        fig.add_trace(
            go.Scatter(
                x=platform_data['Year_of_Release'],
                y=platform_data['Count'],
                name=platform,
                mode='lines',
                stackgroup='one',
                hovertemplate="Year: %{x}<br>Games: %{y}<extra></extra>"
            )
        )
    
    fig.update_layout(
        title='Количество Игр по Платформам и Годам',
        xaxis_title='Год Выпуска',
        yaxis_title='Количество Игр',
        hovermode='x unified'
    )
    
    return fig

# Запустим дэш и сходим посмотреть на него на http://127.0.0.1:8050/
if __name__ == '__main__':
    app.run(debug=False)
