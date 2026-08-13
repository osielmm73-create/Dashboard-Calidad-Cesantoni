import streamlit as st
2
import pandas as pd
3
import plotly.express as px
4
 
5
st.set_page_config(
6
page_title="Dashboard Calidad",
7
page_icon="📊",
8
layout="wide"
9
)
10
 
11
st.title("📊 Dashboard Ejecutivo de Calidad")
12
 
13
archivo = st.file_uploader(
14
"Sube tu archivo Excel",
15
type=["xlsx"]
16
)
17
 
18
if archivo:
19
 
20
try:
21
 
22
df = pd.read_excel(
23
archivo,
24
sheet_name="REPORTE DE CALIDAD",
25
header=8
26
)
27
 
28
df.columns = [
29
str(c).strip().upper()
30
for c in df.columns
31
]
32
 
33
# Eliminar columnas UNNAMED
34
df = df.loc[
35
:,
36
~df.columns.str.contains("UNNAMED")
37
]
38
 
39
# Filtrar calidades válidas
40
df = df[
41
df["CALIDAD"].isin(
42
[
43
"PRIMERA",
44
"SEGUNDA",
45
"TERCERA",
46
"QUINTA"
47
]
48
)
49
]
50
 
51
df["M2"] = pd.to_numeric(
52
df["M2"],
53
errors="coerce"
54
)
55
 
56
total = df["M2"].sum()
57
 
58
primera = df.loc[
59
df["CALIDAD"] == "PRIMERA",
60
"M2"
61
].sum()
62
 
63
segunda = df.loc[
64
df["CALIDAD"] == "SEGUNDA",
65
"M2"
66
].sum()
67
 
68
quinta = df.loc[
69
df["CALIDAD"] == "QUINTA",
70
"M2"
71
].sum()
72
 
73
calidad = (
74
primera / total * 100
75
if total > 0 else 0
76
)
77
 
78
brecha = calidad - 94.5
79
 
80
c1, c2, c3, c4, c5 = st.columns(5)
81
 
82
c1.metric(
83
"Calidad General",
84
f"{calidad:.2f}%"
85
)
86
 
87
c2.metric(
88
"Meta",
89
"94.50%"
90
)
91
 
92
c3.metric(
93
"Brecha",
94
f"{brecha:.2f}%"
95
)
96
 
97
c4.metric(
98
"M² Totales",
99
f"{total:,.0f}"
100
)
101
 
102
c5.metric(
103
"M² Segunda + Quinta",
104
f"{(segunda + quinta):,.0f}"
105
)
106
 
107
st.divider()
108
 
109
# CALIDAD POR PLANTA
110
 
111
planta = (
112
df.groupby("PLANTA")
113
.apply(
114
lambda x:
115
(
116
x.loc[
117
x["CALIDAD"] == "PRIMERA",
118
"M2"
119
].sum()
120
/
121
x["M2"].sum()
122
) * 100
123
)
124
.reset_index(name="CALIDAD")
125
)
126
 
127
fig_planta = px.bar(
128
planta,
129
x="PLANTA",
130
y="CALIDAD",
131
text="CALIDAD",
132
title="Calidad Acumulada por Planta"
133
)
134
 
135
fig_planta.update_traces(
136
texttemplate="%{text:.2f}%",
137
textposition="outside"
138
)
139
 
140
fig_planta.add_hline(
141
y=94.5,
142
line_dash="dash",
143
line_color="red",
144
annotation_text="Meta 94.5%"
145
)
146
 
147
st.plotly_chart(
148
fig_planta,
149
use_container_width=True
150
)
151
 
152
st.divider()
153
 
154
# PRODUCCIÓN POR HORNO
155
 
156
produccion = (
157
df.groupby("HORNO")["M2"]
158
.sum()
159
.reset_index()
160
)
161
 
162
fig_horno = px.bar(
163
produccion,
164
x="HORNO",
165
y="M2",
166
text="M2",
167
title="Producción Acumulada por Horno"
168
)
169
 
170
fig_
