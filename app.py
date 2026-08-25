# --- GRÁFICA CORREGIDA: FONDO LIMPIO Y ETIQUETAS SEPARADAS ---
    st.markdown('<div class="section-box"><div class="section-title">EVOLUCIÓN DIARIA: CALIDAD (%) VS PRODUCCIÓN DE METROS CUADRADOS (M²)</div>', unsafe_allow_html=True)
    if not t2_dias.empty:
        t2_dias['DIA_STR'] = t2_dias['DIA'].astype(str).str.split().str[0]
        y_calidad = t2_dias['P1_P3_DIARIA'] * 100 if t2_dias['P1_P3_DIARIA'].max() <= 1.0 else t2_dias['P1_P3_DIARIA']
        y_mts2 = t2_dias['MTS2_DIA']

        fig_mix = make_subplots(specs=[[{"secondary_y": True}]])

        # 1. Columnas m² en Azul Grisáceo Tenue - Texto adentro al fondo (Eje Y2)
        fig_mix.add_trace(
            go.Bar(
                x=t2_dias['DIA_STR'],
                y=y_mts2,
                name="m² Producidos",
                marker_color="rgba(51, 65, 85, 0.45)",
                marker_line_color="#475569",
                marker_line_width=1,
                text=[fmt_num(v) for v in y_mts2],
                textposition="inside",
                insidetextanchor="bottom",
                textfont=dict(color="#94A3B8", size=9)
            ),
            secondary_y=True
        )

        # 2. Línea Calidad Diaria (%) en Verde Neón con Caja Destacada (Eje Y1)
        fig_mix.add_trace(
            go.Scatter(
                x=t2_dias['DIA_STR'],
                y=y_calidad,
                mode="lines+markers+text",
                name="Calidad Diaria (%)",
                text=[f" <b>{v:.2f}%</b> " for v in y_calidad],
                textposition="top center",
                textfont=dict(color="#FFFFFF", size=9),
                line=dict(color="#10B981", width=3),
                marker=dict(
                    size=8, 
                    color="#10B981", 
                    line=dict(color="#064E3B", width=1)
                )
            ),
            secondary_y=False
        )

        # 3. Línea Meta 94.50% (Eje Y1)
        fig_mix.add_trace(
            go.Scatter(
                x=t2_dias['DIA_STR'],
                y=[94.50] * len(t2_dias),
                mode="lines",
                name="Meta Calidad (94.50%)",
                line=dict(color="#EF4444", width=2, dash="dash")
            ),
            secondary_y=False
        )

        # Rango vertical holgado
        min_val = float(y_calidad.min()) if not y_calidad.empty and pd.notna(y_calidad.min()) else 70.0
        y_min_bound = float(min(min_val - 6.0, 60.0))
        max_mts2 = float(y_mts2.max()) if not y_mts2.empty and pd.notna(y_mts2.max()) else 20000.0

        # Estilo General y Eliminación de Cuadrícula
        fig_mix.update_layout(
            height=540,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#94A3B8",
            margin=dict(l=15, r=15, t=40, b=15),
            legend=dict(orientation="h", yanchor="bottom", y=1.04, xanchor="right", x=1)
        )

        # Configuración Eje X sin cuadrícula
        fig_mix.update_xaxes(
            type="category",
            tickangle=-45,
            showgrid=False,
            title_text="Días del Mes"
        )

        # Eje Y Primario (% Calidad) sin cuadrícula
        fig_mix.update_yaxes(
            title_text="% Calidad",
            showgrid=False,
            tickformat=".1f",
            range=[y_min_bound, 108.0],
            secondary_y=False
        )

        # Eje Y Secundario (m²) sin cuadrícula
        fig_mix.update_yaxes(
            title_text="Metros Cuadrados (m²)",
            showgrid=False,
            tickformat=",d",
            range=[0, max_mts2 * 1.2],
            secondary_y=True
        )

        st.plotly_chart(fig_mix, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
