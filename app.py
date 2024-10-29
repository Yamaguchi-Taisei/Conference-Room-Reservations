import streamlit as st
import random
import requests
import json
import datetime
import pandas as pd

page = st.sidebar.selectbox('Choose your page', ['users', 'rooms', 'bookings'])

# ユーザー登録ページ
if page == 'users':
    st.title('ユーザー登録画面')

    with st.form(key='user'):
        # user_id: int = random.randint(10, 99)
        user_name: str = st.text_input('ユーザー名', max_chars=12)
        data = {
            # 'user_id': user_id,
            'user_name': user_name
        }
        submit_button = st.form_submit_button(label='ユーザー登録')

    if submit_button:
        url = 'http://127.0.0.1:8000/users'
        res = requests.post(
            url,
            data=json.dumps(data)
        )
        if res.status_code == 200:
            st.success('ユーザー登録完了')
        st.json(res.json())

    # ユーザー一覧の取得
    url_users = 'http://127.0.0.1:8000/users'
    res = requests.get(url_users)
    users = res.json()
    users_name = {}
    for user in users:
        users_name[user['user_name']] = user['user_id']

    st.write('### 登録者一覧')
    df_users = pd.DataFrame(users)
    df_users.columns = ['登録者名', '登録者ID']
    st.table(df_users)


# 会議室登録ページ
elif page == 'rooms':
    st.title('会議室登録画面')

    with st.form(key='room'):
        # room_id: int = random.randint(10, 99)
        room_name: str = st.text_input('会議室名', max_chars=12)
        capacity: int = st.number_input('定員', step=1)
        data = {
            # 'room_id': room_id,
            'room_name': room_name,
            'capacity': capacity,
        }
        submit_button = st.form_submit_button(label='会議室登録')

    if submit_button:
        url = 'http://127.0.0.1:8000/rooms'
        res = requests.post(
            url,
            data=json.dumps(data)
        )
        if res.status_code == 200:
            st.success('会議室登録完了')
        st.json(res.json())

    # 会議室一覧の取得
    url_rooms = 'http://127.0.0.1:8000/rooms'
    res = requests.get(url_rooms)
    rooms = res.json()
    rooms_name = {}
    for room in rooms:
        rooms_name[room['room_name']] = {
            'room_id': room['room_id'],
            'capacity': room['capacity'],
        }

    st.write('### 会議室一覧')
    df_rooms = pd.DataFrame(rooms)
    df_rooms.columns = ['会議室名', '定員', '会議室ID']
    st.table(df_rooms)


# 予約ページ
elif page == 'bookings':
    st.title('会議室予約画面')

    # ユーザー一覧の取得
    url_users = 'http://127.0.0.1:8000/users'
    res = requests.get(url_users)
    users = res.json()
    users_name = {}
    for user in users:
        users_name[user['user_name']] = user['user_id']

    # 会議室一覧の取得
    url_rooms = 'http://127.0.0.1:8000/rooms'
    res = requests.get(url_rooms)
    rooms = res.json()
    rooms_name = {}
    for room in rooms:
        rooms_name[room['room_name']] = {
            'room_id': room['room_id'],
            'capacity': room['capacity'],
        }

    st.write('### 会議室一覧')
    df_rooms = pd.DataFrame(rooms)
    df_rooms.columns = ['会議室名', '定員', '会議室ID']
    st.table(df_rooms)

    # 予約一覧
    url_bookings = 'http://127.0.0.1:8000/bookings'
    res = requests.get(url_bookings)
    bookings = res.json()
    df_bookings = pd.DataFrame(bookings)

    users_id = {}
    for user in users:
        users_id[user['user_id']] = user['user_name']

    rooms_id = {}
    for room in rooms:
        rooms_id[room['room_id']] = {
            'room_name': room['room_name'],
            'capacity': room['capacity']
        }

    # IDを各値に変更
    def to_user_name(x): return users_id[x]
    def to_room_name(x): return rooms_id[x]['room_name']

    def to_datetime(x): return datetime.datetime.fromisoformat(
        x).strftime('%Y/%m/%d %H:%M')

    # 特定の列に適応
    df_bookings['user_id'] = df_bookings['user_id'].map(to_user_name)
    df_bookings['room_id'] = df_bookings['room_id'].map(to_room_name)
    df_bookings['start_datetime'] = df_bookings['start_datetime'].map(
        to_datetime)
    df_bookings['end_datetime'] = df_bookings['end_datetime'].map(to_datetime)

    st.write('### 予約一覧')
    df_bookings = df_bookings.rename(columns={
        'user_id': '予約者名',
        'room_id': '会議室名',
        'booked_num': '予約人数',
        'start_datetime': '開始時刻',
        'end_datetime': '終了時刻',
        'booking_id': '予約ID',
    })
    st.table(df_bookings)

    # 予約フォーム
    with st.form(key='booking'):
        # booking_id: int = random.randint(10, 99)
        user_name: str = st.selectbox('予約者名', users_name.keys())
        room_name: str = st.selectbox('会議室名', rooms_name.keys())
        booked_num: int = st.number_input('予約人数', step=1)
        date = st.date_input('日付: ', min_value=datetime.date.today())
        start_time = st.time_input(
            '開始時刻: ', value=datetime.time(hour=9, minute=0))
        end_time = st.time_input(
            '終了時刻: ', value=datetime.time(hour=20, minute=0))
        submit_button = st.form_submit_button(label='予約登録')

    if submit_button:
        user_id: int = users_name[user_name]
        room_id: int = rooms_name[room_name]['room_id']
        room_capacity: int = rooms_name[room_name]['capacity']

        data = {
            # 'booking_id': booking_id,
            'user_id': user_id,
            'room_id': room_id,
            'booked_num': booked_num,
            'start_datetime': datetime.datetime(
                year=date.year,
                month=date.month,
                day=date.day,
                hour=start_time.hour,
                minute=start_time.minute
            ).isoformat(),
            'end_datetime': datetime.datetime(
                year=date.year,
                month=date.month,
                day=date.day,
                hour=end_time.hour,
                minute=end_time.minute
            ).isoformat(),
        }

        # 定員以上の予約人数の場合
        if booked_num > room_capacity:
            st.error(f'{room_name}の定員は、{room_capacity}名です。\n'
                     f'{room_capacity}名以下の予約人数のみ受け付けております。')

        # 開始時刻　>= 終了時刻
        elif start_time >= end_time:
            st.error('開始時刻が終了時刻を超えています。')

        # 9:00~20:00ではない場合
        elif start_time < datetime.time(hour=9, minute=0, second=0) or end_time > datetime.time(hour=20, minute=0, second=0):
            st.error('利用可能時間は9:00~20:00になります。')

        # APIをたたく
        else:
            url = 'http://127.0.0.1:8000/bookings'
            res = requests.post(
                url,
                data=json.dumps(data)
            )

            if res.status_code == 200:
                st.success('予約完了しました')
            elif res.status_code == 404 and res.json()['detail'] == 'Already booked':
                st.error('指定の時間にはすでに予約が入っています。')
            st.json(res.json())