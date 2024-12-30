import streamlit as st
import pandas as pd
import random
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import date, time

@dataclass
class GachaSystem:
    """Mengelola sistem gacha dengan hadiah yang ditentukan pengguna."""
    saran_kegiatan: List[Dict[str, str]] = field(default_factory=list)

    def tambah_saran(self, kegiatan: str, deskripsi: str, durasi: str) -> None:
        self.saran_kegiatan.append({"kegiatan": kegiatan, "deskripsi": deskripsi, "durasi": durasi})

    def tarik_gacha(self) -> Optional[Dict[str, str]]:
        return random.choice(self.saran_kegiatan) if self.saran_kegiatan else None

@dataclass
class PengelolaKegiatan:
    """Mengelola berbagai jenis kegiatan."""
    kegiatan: Dict[str, pd.DataFrame] = field(default_factory=lambda: {
        "kuliah": pd.DataFrame(columns=["Tanggal", "Jam Mulai", "Jam Akhir", "Kegiatan", "Status"]),
        "rumah": pd.DataFrame(columns=["Tanggal", "Jam Mulai", "Jam Akhir", "Kegiatan", "Status"]),
    })
    gacha_system: GachaSystem = field(default_factory=GachaSystem)

    def tambah_kegiatan(self, jenis_kegiatan: str, tanggal: date, jam_mulai: time, jam_akhir: time, kegiatan: str) -> None:
        kegiatan_baru = pd.DataFrame({
            "Tanggal": [tanggal],
            "Jam Mulai": [jam_mulai],
            "Jam Akhir": [jam_akhir],
            "Kegiatan": [kegiatan],
            "Status": ["Belum Selesai"]
        })
        self.kegiatan[jenis_kegiatan] = pd.concat([self.kegiatan[jenis_kegiatan], kegiatan_baru], ignore_index=True)

    def ubah_status_kegiatan(self, jenis_kegiatan: str, index: int) -> None:
        df = self.kegiatan[jenis_kegiatan]
        if 0 <= index < len(df):
            df.at[index, "Status"] = "Selesai" if df.at[index, "Status"] == "Belum Selesai" else "Belum Selesai"

    def tingkat_penyelesaian(self) -> float:
        total = sum(len(df) for df in self.kegiatan.values())
        selesai = sum(len(df[df["Status"] == "Selesai"]) for df in self.kegiatan.values())
        return (selesai / total) * 100 if total > 0 else 0.0

def buat_form_kegiatan(pengelola_kegiatan: PengelolaKegiatan, jenis_kegiatan: str) -> None:
    with st.form(key=f'{jenis_kegiatan}_form'):
        st.subheader(f"Tambah Kegiatan {jenis_kegiatan.capitalize()}")
        tanggal = st.date_input("Tanggal")
        jam_mulai, jam_akhir = st.columns(2)
        jam_mulai = jam_mulai.time_input("Jam Mulai")
        jam_akhir = jam_akhir.time_input("Jam Akhir")
        kegiatan = st.text_input("Kegiatan")

        if st.form_submit_button("Tambah"):
            if jam_akhir <= jam_mulai:
                st.error("Jam akhir harus lebih besar dari jam mulai!")
            elif not kegiatan.strip():
                st.error("Kegiatan tidak boleh kosong!")
            else:
                pengelola_kegiatan.tambah_kegiatan(jenis_kegiatan, tanggal, jam_mulai, jam_akhir, kegiatan)
                st.success("Kegiatan berhasil ditambahkan!")
                st.balloons()

def tampilkan_kegiatan(pengelola_kegiatan: PengelolaKegiatan, jenis_kegiatan: str) -> None:
    df = pengelola_kegiatan.kegiatan[jenis_kegiatan]
    if df.empty:
        st.info("Belum ada kegiatan yang ditambahkan.")
        return

    st.subheader(f"Daftar Kegiatan {jenis_kegiatan.capitalize()}")
    for idx, row in df.iterrows():
        with st.expander(f"Kegiatan {idx + 1}", expanded=True):
            st.write(f"*Tanggal:* {row['Tanggal']}")
            st.write(f"*Jam Mulai:* {row['Jam Mulai']}")
            st.write(f"*Jam Akhir:* {row['Jam Akhir']}")
            st.write(f"*Kegiatan:* {row['Kegiatan']}")
            st.write(f"*Status:* {row['Status']}")
            status = "🟢 Selesai" if row['Status'] == "Selesai" else "🔴 Belum Selesai"
            if st.button(status, key=f"{jenis_kegiatan}status{idx}"):
                pengelola_kegiatan.ubah_status_kegiatan(jenis_kegiatan, idx)

def buat_form_gacha(pengelola_kegiatan: PengelolaKegiatan) -> None:
    with st.form(key='gacha_form'):
        st.subheader("Tambah Kegiatan ke Gacha")
        kegiatan = st.text_input("Nama Kegiatan")
        deskripsi = st.text_area("Deskripsi")
        durasi = st.text_input("Durasi (contoh: 30 menit)")

        if st.form_submit_button("Tambah ke Pool Gacha"):
            if not all([kegiatan.strip(), deskripsi.strip(), durasi.strip()]):
                st.error("Semua field harus diisi!")
            else:
                pengelola_kegiatan.gacha_system.tambah_saran(kegiatan, deskripsi, durasi)
                st.success("Saran kegiatan berhasil ditambahkan ke pool gacha!")

def main():
    st.set_page_config(page_title="Jadwal Kegiatan", page_icon="📅", layout="wide")

    # Custom CSS for styling the page
    st.markdown("""
        <style>
            /* Body styles */
            body {
                font-family: 'Arial', sans-serif;
                margin: 0;
                padding: 0;
            }
            .stApp{
              
                 background: linear-gradient(rgba(0, 0, 0, 0.3), rgba(0, 0, 0, 0.3)), 
              url('https://i.pinimg.com/736x/03/fc/2d/03fc2dbe36ea5fbf93691b8173d66931.jpg');
    background-size: cover;
    }
            /* Sidebar styles */
            .css-1d391kg {
                background-color: #2e3b47;
                color: #fff;
            }
            .css-1d391kg .stSidebarMenu, .css-1d391kg .stSidebar {
                padding-top: 20px;
            }

            /* Title styles */
            .stTitle {
                font-size: 36px;
                font-weight: bold;
                margin-top: 30px;
                text-align: center;
            }

            /* Tabs section styling */
            .stTab {
                font-size: 18px;
                font-weight: bold;
                padding: 10px;
                background-color: #e1e8;
                border-radius: 5px;
                transition: background-color 0.3s;
            }
            .stTab:hover {
                background-color: #d1d8;
            }

            /* Button style for "Tambah" and "Tarik Gacha" */
            .stButton {
                color: white;
                font-weight: bold;
                border-radius: 5px;
                padding: 10px 20px;
                margin-top: 10px;
                transition: background-color 0.3s;
            }

            /* Section heading styling */
            .stSubheader {
                font-size: 20px;
                font-weight: bold;
                color: #2e3b47;
            }

            /* Form inputs and text areas */
            .stTextInput, .stTextArea, .stDateInput, .stTimeInput {
                border-radius: 5px;
                border: 1px solid #ccf;
                padding: 10px;
                width: 100%;
                margin-top: 5px;
            }

            .stMetric {
                font-size: 24px;
                font-weight: bold;
                color: #333;
            }

            /* Table styling */
            .stTable {
                border-collapse: collapse;
                width: 100%;
                margin-top: 20px;
            }

            .stTable th, .stTable td {
                border: 1px solid #ddf;
                padding: 8px;
                text-align: center;
            }

            .stTable th {
                background-color: #663c1f;
                font-weight: bold;
            }

            /* Expander styles */
            .stExpanderHeader {
                background-color: #f7d;
                color: #333;
                font-size: 18px;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }

            .stExpanderContent {
                background-color: #ffcc00;
                color: #333;
                padding: 15px;
                font-size: 16px;
                border-radius: 5px;
            }

            /* Balloons effect */
            .stBalloons {
                font-size: 50px;
                color: #ffcc00;
            }

            /* Custom chart styling */
            .stBarChart {
                margin-top: 20px;
                border-radius: 10px;
                background-color: #ffcc00;
            }

            /* General padding and margin adjustment */
            .stApp {
                padding: 20px;
            }
        </style>
    """, unsafe_allow_html=True)

    # Initialize PengelolaKegiatan instance
    if 'pengelola_kegiatan' not in st.session_state:
        st.session_state.pengelola_kegiatan = PengelolaKegiatan()

    # Title of the app
    st.title("📅 Jadwal Kegiatan Produktif Mahasiswa")

    # Sidebar section
    st.sidebar.title("Dashboard")
    tabs = st.tabs(["Home", "Kuliah", "Rumah", "Review", "Challange"])

    with st.sidebar:
        st.metric("Tingkat Penyelesaian Kegiatan", f"{st.session_state.pengelola_kegiatan.tingkat_penyelesaian():.1f}%")
        st.subheader("Kegiatan yang Belum Selesai")
        belum_selesai = sum(len(df[df["Status"] == "Belum Selesai"]) for df in st.session_state.pengelola_kegiatan.kegiatan.values())
        st.write(f"Jumlah kegiatan yang belum selesai: {belum_selesai}")

    with tabs[0]:  # Home Tab
        st.subheader("Selamat datang di Aplikasi kami! 🎉")
        st.write("""
            Aplikasi ini dirancang untuk membantu Anda mengelola kegiatan produktif sehari-hari,
            baik di kampus (kuliah, organisasi) maupun di rumah (belajar, berolahraga, dll).
        """)
        st.write("""
            Di sini, Anda dapat menambahkan kegiatan, melacak kemajuan penyelesaian, dan bahkan
            mendapatkan saran kegiatan secara acak melalui sistem gacha.
        """)
        st.write("Selamat mencoba dan semoga Aplikasi ini bermanfaat!")
        st.image("image.png")
        
        
    with tabs[1]:  # Kuliah Tab
        buat_form_kegiatan(st.session_state.pengelola_kegiatan, "kuliah")
        st.divider()
        tampilkan_kegiatan(st.session_state.pengelola_kegiatan, "kuliah")

    with tabs[2]:  # Rumah Tab
        buat_form_kegiatan(st.session_state.pengelola_kegiatan, "rumah")
        st.divider()
        tampilkan_kegiatan(st.session_state.pengelola_kegiatan, "rumah")

    with tabs[3]:  # Review Tab
        rate = st.session_state.pengelola_kegiatan.tingkat_penyelesaian()

        st.subheader("Semua Kegiatan")
        for jenis_kegiatan, df in st.session_state.pengelola_kegiatan.kegiatan.items():
            st.write(f"### {jenis_kegiatan.capitalize()}")
            if df.empty:
                st.info(f"Tidak ada kegiatan untuk {jenis_kegiatan}.")
            else:
                st.table(df)
                
        # Tampilkan grafik tingkat penyelesaian
        st.subheader("Grafik Penyelesaian Kegiatan")
        penyelesaian_df = pd.DataFrame({
            "Kegiatan": ["Kuliah", "Rumah"],
            "Status": [sum(st.session_state.pengelola_kegiatan.kegiatan["kuliah"]["Status"] == "Selesai"),
                        sum(st.session_state.pengelola_kegiatan.kegiatan["rumah"]["Status"] == "Selesai")]
        })
        st.bar_chart(penyelesaian_df.set_index("Kegiatan"))
        

    with tabs[4]:  # Gacha Tab
        buat_form_gacha(st.session_state.pengelola_kegiatan)
        st.divider()
        st.subheader("Pool Gacha")

        if not st.session_state.pengelola_kegiatan.gacha_system.saran_kegiatan:
            st.info("Pool gacha kosong.")
        else:
            st.table(pd.DataFrame(st.session_state.pengelola_kegiatan.gacha_system.saran_kegiatan))

        if rate >= 80 and st.button("Gacha!"):
            saran = st.session_state.pengelola_kegiatan.gacha_system.tarik_gacha()
            if saran:
                st.success(f"🎉 {saran['kegiatan']} | 📝 {saran['deskripsi']} | ⏱ {saran['durasi']}")
                # Add a button to complete the task
                if st.button("Selesai"):
                    # You can add logic here to mark the task as complete
                    st.success("Kegiatan telah selesai!")
            else:
                st.warning("Pool gacha kosong.")

if __name__ == "__main__":
    main()