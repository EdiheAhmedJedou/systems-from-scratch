out_lines = []
with open('samples/test.md', 'r') as fin:
    for line in fin:
        if line.startswith("# "):
            content = line[2:].strip()
            html = f"<h1>{content}</h1>"
            out_lines.append(html)
            

with open("samples/output.html", "w") as fout:
    fout.write("/n".join(out_lines))
        
    



    