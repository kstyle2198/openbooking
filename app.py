import streamlit as st
import sqlite3
from datetime import datetime, date, timedelta
import pandas as pd
import numpy as np

def create_table():
    conn = sqlite3.connect('bookings.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS bookings
                (예약번호 INTEGER PRIMARY KEY AUTOINCREMENT,
                company TEXT,
                사번 TEXT,
                name TEXT,
                table_number INTEGER,
                booking_date TEXT,
                status TEXT)''')
    conn.commit()
    conn.close()


def date_range(start, end):
    start = datetime.strptime(start, "%Y-%m-%d")
    end = datetime.strptime(end, "%Y-%m-%d")
    dates = [date.strftime("%Y-%m-%d") for date in pd.date_range(start, periods=(end-start).days+1)]
    return dates

def download_df(name1):
    cnx = sqlite3.connect('bookings.db')
    df = pd.read_sql_query("SELECT * FROM bookings", cnx)
    if name1 != "":
        df = df[df["name"]==name1]
    return df

def display_df(name1):
    cnx = sqlite3.connect('bookings.db')
    df = pd.read_sql_query("SELECT * FROM bookings ORDER BY booking_date DESC", cnx)
    df = df.drop("사번", axis=1)
    if name1 != "":
        df = df[df["name"]==name1]
    return df

def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8-sig')

# Function to handle new booking submission
def check_duplicate(사번, booking_date, table_number):
    conn = sqlite3.connect('bookings.db')
    c = conn.cursor()
    c.execute("SELECT * FROM bookings")
    bookings = c.fetchall()
    cnt = 0
    for booking in bookings:
        if 사번 == booking[2] and booking_date.strftime('%Y-%m-%d') == booking[5]:  # 동일일자 중복 사번
            cnt += 1
        elif table_number == booking[4] and booking_date.strftime('%Y-%m-%d') == booking[5]:  # 동일일자 좌석번호 중복
            cnt += 1
        else:
            pass
    if cnt == 0:
        return True

def add_booking(company, 사번, name, table_number, booking_date):
    if 사번 == "" or name =="":
        return False
    else:
        if check_duplicate(사번, booking_date, table_number):
            
            conn = sqlite3.connect('bookings.db')
            c = conn.cursor()
            c.execute("INSERT INTO bookings (company, 사번, name, table_number, booking_date, status) VALUES (?, ?, ?, ?, ?, ?)",
                    (company, 사번, name, table_number, booking_date, 'Booked'))
            conn.commit()
            conn.close()
            return True
        
        else:
            False

# Function to handle booking deletion
def delete_booking(booking_id, 사번, booking_date):
    try:
        conn = sqlite3.connect('bookings.db')
        c = conn.cursor()
        c.execute("SELECT * FROM bookings WHERE 예약번호 = ?", (booking_id,))
        booking = c.fetchall()

        if 사번 == booking[0][2] and booking_date.strftime('%Y-%m-%d') == booking[0][5]:
            c.execute("DELETE FROM bookings WHERE 예약번호 = ?", (booking_id,))
            conn.commit()
            conn.close()
            return True
        else:
            return False
    except:
        return False
        
# Main function
def main():
    st.set_page_config(page_title="🎈OpenBooking", page_icon="11", layout="wide")

    st.markdown("#### :green[서울 계동 ]")
    st.markdown('### 🎉 :blue[리모트 오피스 예약 프로그램]')
    st.write('---')

    # Menu selection
    menu_options = ['Add Booking', 'Delete Booking']
    with st.sidebar:
        st.header("🔅 **예약/취소는 사이드바에서!**")
        st.markdown("##### ***:green[   📒 노션 안내 자료]*** : [link](https://www.notion.so/hyundaigenuine/3c5b039fe44f4eb0a303dc25dcb14cab?pvs=4)")
        menu_choice = st.sidebar.selectbox('🚀 **:blue[Select Menu]**', menu_options)
    
    # 예약 날짜 구간
    min_date = date.today()
    interval = timedelta(hours=720)  #예약가능구간 15일 부여
    max_date = min_date + interval
    

    # 본문
    with st.expander("📢 ***주요 사항 안내***"):
        st.markdown("""
                    - 건설기계부문은 :blue[**10석**]을 배정받아 운영합니다. (사용 실적에 따라 조정)
                    - 날짜별 미예약 테이블 넘버 현황에서 숫자가 table_number 입니다. ("예약" 글자 아닌 숫자가 기재된 부분이 예약 가능한 곳임)
                    - 좌석번호(table_number)는 :red[***날짜별 예약가능번호***]를 의미하며, 실제 이용은 빈책상 임의 지정하여 사용하면 됩니다.
                    - Booking시 사번, 성명 정확히 입력 바랍니다. (HDX는 근태계도 상신 / 근태코드 : 리모트오피스)
                    - 동일 날짜에 1인이(동일 사번) 중복 예약 안됩니다.
                    - 리모트오피스 이용 관련 안내사항은 사이드바 상단의 :green[노션 안내자료] 참고 바랍니다.
                    - 이용상 문의사항은 메일로 연락 바랍니다.(jongbae.kim@hyundai-genuine.com)
                    """)
    
    tab1, tab2 = st.tabs(["🍉:red[**날짜별 미예약 테이블 넘버 현황**]", "🌻:blue[**예약자 리스트**]"])
    
    with tab1:       
        columns = date_range(min_date.strftime('%Y-%m-%d'), max_date.strftime('%Y-%m-%d')) ############################# Hard coding

        data = []
        for _ in columns:
            data.append(np.arange(1, 11))
        
        table_df = pd.DataFrame(data).T
        table_df.columns = columns    
        

        # 예약 좌석 체킹
        cnx = sqlite3.connect('bookings.db')
        df = pd.read_sql_query("SELECT * FROM bookings", cnx)
        df2 = df[["table_number", "booking_date", "name"]]
        
        for t_num, b_date in zip(df2["table_number"], df2["booking_date"]):
            for k in table_df.columns:
                # print(k, table_df[k])
                if b_date == k:
                    for val in table_df[k]:
                        if t_num == val:
                            num = int(val)-1
                            # print(k, val, table_df[k][num])
                            # print(table_df[k])
                            table_df[k].replace(table_df[k][num],"예약", inplace=True)  #table_df[k].replace(table_df[k][num],"예약", inplace=True)
                        else:
                            pass
                else:
                    pass
        st.dataframe(table_df)
    
    with tab2:
    
        search_name = st.text_input("🔎 **이름으로 조회하기 (이름 입력후 엔터)**")
        st.dataframe(display_df(search_name), use_container_width=True)
        
        st.markdown("---")
        with st.expander(""): 
            csv = convert_df(download_df(search_name))
            뭘까 = st.text_input("🕵️‍♂️ 다운로드", type="password")
            if 뭘까 == "A422525":
                val = False
            else: 
                val = True
            st.download_button(
            label="Download data as CSV",
            data=csv,
            file_name='download_df.csv',
            mime='text/csv', disabled=val
            )

    if menu_choice == 'Add Booking':
        with st.sidebar:
            st.subheader('🐬 Add New Booking')
            company = st.selectbox('☘️ 소속 회사를 선택해주세요', ["HDX", "HDI", "HCE"])
            사번 = st.text_input('☘️ 사번을 입력해주세요')
            name = st.text_input('☘️ 성명을 입력해주세요(name)')
            table_number = st.selectbox("☘️ table_number를 입력해주세요", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
            booking_date = st.date_input('📆 Booking Date', min_value=min_date, max_value=max_date)        
            if st.button('🖍️ Submit Booking'):
                if add_booking(company, 사번, name, table_number, booking_date):
                    st.experimental_rerun()
                else:
                    st.error("🚫 동일일자 중복 사번이거나, 사번/성명을 입력하지 않았습니다.")

    elif menu_choice == 'Delete Booking':
        with st.sidebar:
            st.subheader('🐼 Delete Booking')
            booking_id = st.number_input('☘️ 예약번호 :red[ (예약번호 입력해주세요! No table_number!)]', min_value=1)
            사번 = st.text_input("☘️ 사번")
            booking_date = st.date_input('📆 취소할 예약 날짜', min_value=min_date, max_value=max_date) #
            if st.button('🗑️ Delete Booking'):
                if delete_booking(booking_id, 사번, booking_date):
                    st.experimental_rerun()

                else:
                    st.error('🚫 예약번호, 사번, 날짜가 일치하는 대상이 없습니다.')          


if __name__ == "__main__":
    
    create_table()
    main()