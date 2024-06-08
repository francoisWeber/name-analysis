from matplotlib import pyplot as plt
import pandas as pd
from typing import List, Optional, Tuple, Union
import streamlit as st
from unidecode import unidecode
from pydantic import BaseModel
import name_analysis.streamlit_pydantic as sp
from enum import IntEnum

st.title("Historique des prénoms depuis 1900")

CSV_URL = "https://raw.githubusercontent.com/francoisWeber/name-analysis/master/db_prenoms.csv"

if "df" not in st.session_state:
    df = pd.read_csv(CSV_URL)
    st.session_state["df"] = df

if "df_tot" not in st.session_state:
    df_tot = df.groupby(["sexe", "annee"]).agg({"nombre": "sum"}).reset_index()
    st.session_state["df_tot"] = df_tot

if "nb_names" not in st.session_state:
    st.session_state["nb_names"] = 1


def incr_name_list():
    st.session_state.nb_names += 1

class SexEnum(IntEnum):
    male = 1
    female = 2

class Name(BaseModel):
    name: str = "Jean-Eude"
    sex: SexEnum
    anno: int = 0
    

names = []

for i in range(st.session_state.nb_names):
    cols = st.columns([10, 1])
    with cols[0]:
        datum = sp.pydantic_fields(key=f"my_form{i}", model=Name)
        names.append(datum)
    # with cols[1]:
    #     st.button(":heavy_minus_sign:", on_click=incr_name_list, key=f"minus{i}", args=(i))
        
st.button(":heavy_plus_sign:", on_click=incr_name_list)


df = st.session_state.df
df_tot = st.session_state.df_tot

if len(names):
    fig, _ = plt.subplots(figsize=(7, 4))
    for _name in names:
        name = _name["name"]
        sexe = _name["sex"]
        anno = _name["anno"]
        name_upper = unidecode(name).upper()
        a = df[df.prenom == name_upper].set_index("annee")[["nombre"]].sort_index()
        b = df_tot[df_tot.sexe == sexe].set_index("annee")[["nombre"]]
        c = a.join(b, rsuffix="_tot", how="inner").sort_index()
        serie = c.nombre / c.nombre_tot * 100
        serie.plot(label=name)
        anno = anno if anno > 0 else 2022
        if anno in serie:
            plt.scatter(x=[anno], y=[serie[anno]], s=70)
    plt.yscale("linear") #  "log", "symlog", "logit
    plt.grid()
    plt.legend()

    st.pyplot(fig)
    
