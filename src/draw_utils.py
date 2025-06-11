from IPython.display import Image

def draw_graph(graph):
    try:
        img = Image(graph.get_graph().draw_mermaid_png())
        with open("1_simple_graph.png", "wb") as fout:
            fout.write(img.data)
    except Exception as e:
        print(e)