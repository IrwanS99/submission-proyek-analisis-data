import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
 
sns.set(style='whitegrid')

# Fungsi Pendukung
def get_total_count_by_hour_df(hour_df):
    return hour_df.groupby(by="hours").agg({"count_cr": ["sum"]}).reset_index()

def count_by_day_df(day_df):
    return day_df.query('dteday >= "2011-01-01" and dteday < "2012-12-31"')

def total_registered_df(day_df):
    reg_df = day_df.groupby(by="dteday").agg({"registered": "sum"}).reset_index()
    reg_df.rename(columns={"registered": "register_sum"}, inplace=True)
    return reg_df

def total_casual_df(day_df):
    cas_df = day_df.groupby(by="dteday").agg({"casual": "sum"}).reset_index()
    cas_df.rename(columns={"casual": "casual_sum"}, inplace=True)
    return cas_df

def sum_order(hour_df):
    return hour_df.groupby("hours").count_cr.sum().sort_values(ascending=False).reset_index()

def macem_season(day_df):
    return day_df.groupby(by="season").count_cr.sum().reset_index()

# Membaca Dataset
days_df = pd.read_csv("dashboard/day1.csv")
hours_df = pd.read_csv("dashboard/hour1.csv")

# Mengolah Data
datetime_columns = ["dteday"]
days_df["dteday"] = pd.to_datetime(days_df["dteday"])
hours_df["dteday"] = pd.to_datetime(hours_df["dteday"])

min_date_days = days_df["dteday"].min()
max_date_days = days_df["dteday"].max()

# Sidebar
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/8/87/00_2141_Bicycle-sharing_systems_-_Sweden.jpg/1599px-00_2141_Bicycle-sharing_systems_-_Sweden.jpg", caption="Bike Sharing Insights")
    st.write("""
    ## 📅 Filter Data Berdasarkan Rentang Waktu
    Pilih rentang waktu untuk menganalisis data penyewaan sepeda.
    """)
    start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value=min_date_days,
        max_value=max_date_days,
        value=[min_date_days, max_date_days]
    )

# Filter Data
main_df_days = days_df[(days_df["dteday"] >= str(start_date)) & 
                       (days_df["dteday"] <= str(end_date))]
main_df_hour = hours_df[(hours_df["dteday"] >= str(start_date)) & 
                        (hours_df["dteday"] <= str(end_date))]

# Analisis Data
hour_count_df = get_total_count_by_hour_df(main_df_hour)
reg_df = total_registered_df(main_df_days)
cas_df = total_casual_df(main_df_days)
sum_order_items_df = sum_order(main_df_hour)
season_df = macem_season(main_df_days)

# Dashboard Header
st.header('📊 **Dashboard Bike Sharing Insights**')

# Statistik Harian
st.subheader('🚴‍♂️ **Statistik Harian**')
col1, col2, col3 = st.columns(3)

with col1:
    total_orders = main_df_days["count_cr"].sum()
    st.metric("🚲 Total Penyewaan", f"{total_orders:,}")

with col2:
    total_registered = reg_df["register_sum"].sum()
    st.metric("👥 Pengguna Terdaftar", f"{total_registered:,}")

with col3:
    total_casual = cas_df["casual_sum"].sum()
    st.metric("👤 Pengguna Kasual", f"{total_casual:,}")

# Tren Penyewaan
st.subheader("📈 **Tren Penyewaan Sepeda**")
fig, ax = plt.subplots(figsize=(16, 6))
ax.plot(main_df_days["dteday"], main_df_days["count_cr"], marker='o', color="#4CAF50", label="Penyewaan Harian")
ax.set_title("Tren Penyewaan Sepeda", fontsize=16)
ax.set_xlabel("Tanggal", fontsize=12)
ax.set_ylabel("Jumlah Penyewaan", fontsize=12)
ax.legend()
st.pyplot(fig)

# Jam Sibuk dan Sepi
st.subheader("⏰ **Jam Sibuk dan Sepi Penyewaan Sepeda**")
fig, axes = plt.subplots(1, 2, figsize=(20, 6))

# Jam Tersibuk
sns.barplot(x="hours", y="count_cr", data=sum_order_items_df.head(5), ax=axes[0], palette="viridis")
axes[0].set_title("Jam Tersibuk", fontsize=14)

# Jam Tersepi
sns.barplot(x="hours", y="count_cr", data=sum_order_items_df.tail(5), ax=axes[1], palette="magma")
axes[1].set_title("Jam Tersepi", fontsize=14)

st.pyplot(fig)

# Musim Penyewaan
st.subheader("🌦️ **Penyewaan Berdasarkan Musim**")
fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(x="season", y="count_cr", data=season_df, palette="coolwarm", ax=ax)
ax.set_title("Penyewaan Berdasarkan Musim", fontsize=16)
st.pyplot(fig)

# Proporsi Pengguna
st.subheader("🧑‍🤝‍🧑 **Proporsi Pengguna**")
fig1, ax1 = plt.subplots()
ax1.pie([cas_df["casual_sum"].sum(), reg_df["register_sum"].sum()],
        labels=["Pengguna Kasual", "Pengguna Terdaftar"],
        autopct='%1.1f%%', startangle=90, colors=["#FF9800", "#4CAF50"])
ax1.axis('equal')
st.pyplot(fig1)
