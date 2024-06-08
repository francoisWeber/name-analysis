from matplotlib import pyplot as plt
import pandas as pd
from typing import List, Optional, Tuple, Union
import streamlit as st
from unidecode import unidecode
from pydantic import BaseModel
import name_analysis.streamlit_pydantic as sp
from enum import IntEnum
import numpy as np

st.title("Historique des prénoms depuis 1900")

CSV_URL = "https://raw.githubusercontent.com/francoisWeber/name-analysis/master/db_prenoms.csv"

if "df" not in st.session_state:
    df = pd.read_csv(CSV_URL)
    st.session_state["df"] = df

if "df_tot" not in st.session_state:
    df_tot = df.groupby(["sexe", "annee"]).agg({"nombre": "sum"}).reset_index()
    st.session_state["df_tot"] = df_tot
    
# TODO: make this happen only once
df_tot = st.session_state.df_tot
df_tot_1 = df_tot[df_tot.sexe == 1].set_index("annee")[["nombre"]]
df_tot_2 = df_tot[df_tot.sexe == 2].set_index("annee")[["nombre"]]

if "nb_names" not in st.session_state:
    st.session_state["nb_names"] = 1


def incr_name_list():
    st.session_state.nb_names += 1
    
def normalize(name: str) -> str:
    return unidecode(name).upper()

class SexEnum(IntEnum):
    male = 1
    female = 2

class NameInfo(BaseModel):
    name: str = ""
    sex: SexEnum
    anno: int = 0
    

names_infos: List[NameInfo] = []

for i in range(st.session_state.nb_names):
    cols = st.columns([10, 1])
    with cols[0]:
        datum = sp.pydantic_fields(key=f"my_form{i}", model=NameInfo)
        names_infos.append(datum)
    # with cols[1]:
    #     st.button(":heavy_minus_sign:", on_click=incr_name_list, key=f"minus{i}", args=(i))
        
st.button(":heavy_plus_sign:", on_click=incr_name_list)


df = st.session_state.df
df_tot = st.session_state.df_tot

sex2emoji = {
    1: "♂",
    2: "♀",
}

if len(names_infos):
    for name_info in names_infos:
        name = name_info["name"]
        name_norm = normalize(name)
        name += " " + sex2emoji[name_info["sex"]]
        name_df = df[np.logical_and(df.prenom == name_norm, df.sexe == name_info["sex"])][["annee", "nombre"]].rename(columns={"nombre": name})
        if name_info["sex"] == 1:
            df_tot_1 = df_tot_1.join(other=name_df.set_index(["annee"]), how="left")
        if name_info["sex"] == 2:
            df_tot_2 = df_tot_2.join(other=name_df.set_index(["annee"]), how="left")

    df_1 = df_tot_1.apply(lambda c: c/c.nombre*100, axis=1).drop(columns="nombre")
    df_2 = df_tot_2.apply(lambda c: c/c.nombre*100, axis=1).drop(columns="nombre")

    final_df = df_1.join(df_2)
    st.markdown("**Historique des proportions d'enfants par noms de naissance et par sexe**")
    st.line_chart(data=final_df)

    
