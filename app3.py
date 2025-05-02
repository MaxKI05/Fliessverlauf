import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
import tempfile

# Titel und Upload
st.title("Flowchart Generator aus CSV")

uploaded_file = st.file_uploader("Lade deine CSV-Datei hoch", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    required_columns = {"Schritte", "Prozesse", "Verantwortung"}
    if not required_columns.issubset(df.columns):
        st.error(f"CSV muss die Spalten {required_columns} enthalten.")
    else:
        st.success("CSV erfolgreich geladen!")

        responsibilities = df['Verantwortung'].unique()
        responsibility_to_y = {resp: i for i, resp in enumerate(responsibilities[::-1])}

        fig = go.Figure()
        lane_height = 1
        swimlane_colors = ["#DCEEFF", "#CCE5FF", "#B3D7FF", "#99CAFF", "#80BDFF"]

        for idx, (resp, y_index) in enumerate(responsibility_to_y.items()):
            fig.add_shape(
                type="rect",
                x0=0, x1=1,
                y0=y_index * lane_height, y1=(y_index + 1) * lane_height,
                line=dict(width=0),
                fillcolor=swimlane_colors[idx % len(swimlane_colors)],
                layer="below"
            )
            fig.add_annotation(
                x=-0.02, y=(y_index + 0.5) * lane_height,
                text=resp,
                showarrow=False,
                xanchor="right",
                font=dict(size=14, color="black")
            )

        node_positions = {}
        step_counter = 0
        total_steps = len(df)
        x_range = total_steps + 1  # dynamische Breite

        for idx, row in df.iterrows():
            step = row['Schritte']
            process = row['Prozesse']
            responsibility = row['Verantwortung']

            x = step_counter + 1
            y = responsibility_to_y[responsibility] * lane_height + lane_height / 2
            node_positions[step] = (x, y)

            fig.add_shape(
                type="rect",
                x0=x - 0.5, x1=x + 0.5,
                y0=y - 0.2, y1=y + 0.2,
                line=dict(color="black", width=1),
                fillcolor="lightblue"
            )

            fig.add_annotation(
                x=x, y=y,
                text=process,
                showarrow=False,
                font=dict(size=12, color="black"),
                xanchor="center",
                yanchor="middle"
            )

            step_counter += 1

        # Pfeile zwischen Schritten
        steps = df['Schritte'].tolist()
        for i in range(len(steps) - 1):
            x0, y0 = node_positions[steps[i]]
            x1, y1 = node_positions[steps[i + 1]]
            fig.add_annotation(
                x=x1, y=y1,
                ax=x0, ay=y0,
                xref='x', yref='y',
                axref='x', ayref='y',
                showarrow=True,
                arrowhead=3,
                arrowsize=1.2,
                arrowwidth=2,
                arrowcolor="darkblue"
            )

        chart_width = 200 * total_steps  # für Export & Layout

        fig.update_layout(
            showlegend=False,
            margin=dict(l=100, r=100, t=50, b=50),
            xaxis=dict(visible=False, range=[0, x_range]),
            yaxis=dict(visible=False, range=[-0.5, len(responsibilities) * lane_height]),
            width=chart_width,
            height=300 + 120 * len(responsibilities)
        )

        st.plotly_chart(fig, use_container_width=False)

        # PNG-Download mit dynamischer Breite
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmpfile:
            pio.write_image(fig, tmpfile.name, format="png", width=chart_width, height=400 + 120 * len(responsibilities))
            tmpfile.seek(0)
            st.download_button(
                label="📥 Flowchart als PNG herunterladen",
                data=tmpfile.read(),
                file_name="flowchart.png",
                mime="image/png"
            )
