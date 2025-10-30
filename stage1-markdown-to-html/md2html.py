import re

def escape_html(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def process_inline(s):
    # s must be a string
    s = escape_html(s)
    s = re.sub(r'`(.+?)`', lambda m: "<code>" + escape_html(m.group(1)) + "</code>", s)
    s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
    s = re.sub(r'\*(.+?)\*', r'<em>\1</em>', s)
    s = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', s)
    return s

out_lines = ["<html><body>"]
in_list = False
in_code=False
para_lines=[]

with open('samples/test.md', 'r') as fin:
    for line in fin:
        if line.startswith("## "):
            content = line[3:].strip()
            content = process_inline(content) 
            html = f"<h2>{content}</h2>"
            out_lines.append(html)
        elif line.startswith("# "):
            content = line[2:].strip()
            content = process_inline(content) 
            html = f"<h1>{content}</h1>"
            out_lines.append(html)

        elif line.startswith("- "):
            if not in_list:
                out_lines.append("<ul>")
                in_list = True
            item = line[2:].strip()
            item = process_inline(item)                # <- inline processing
            out_lines.append(f"<li>{item}</li>")
        else:
            # when encountering a non-list line, we must close the list if it was open
            if in_list:
                out_lines.append("</ul>")
                in_list = False
        
            if line.strip():   # non-blank line -> collect for paragraph
                para_lines.append(line.strip())
            else:              # blank line -> flush paragraph
                if para_lines:
                    joined = " ".join(para_lines)
                    joined = process_inline(joined)      # <- IMPORTANT: a string goes in, string comes out
                    out_lines.append(f"<p>{joined}</p>")
                    para_lines = []
    
    # end of file reached: flush paragraph if any
    if para_lines:
        out_lines.append(f"<p>{process_inline(' '.join(para_lines))}</p>")
        para_lines = []

    # close an open list
    if in_list:
        out_lines.append("</ul>")
        in_list = False

    out_lines.append("</body></html>")



with open("samples/output.html", "w") as fout:
    fout.write("\n".join(out_lines))
        
 