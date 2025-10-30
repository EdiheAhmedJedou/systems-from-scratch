import re

def escape_html(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def process_inline(s):
    # 1) extract inline code segments into placeholders
    code_blocks = []
    def repl_code(m):
        code_content = m.group(1)
        # store the escaped inner content (escape once)
        code_blocks.append(escape_html(code_content))
        return f"@@CODE{len(code_blocks)-1}@@"

    s = re.sub(r'`(.+?)`', repl_code, s)

    # 2) now escape the remaining text
    s = escape_html(s)

    # 3) restore code placeholders with proper <code> tags (they are already escaped)
    for i, cb in enumerate(code_blocks):
        s = s.replace(f"@@CODE{i}@@", f"<code>{cb}</code>")

    # 4) do other inline conversions (bold/italic/links) on the already-escaped text
    # Note: these replacements insert HTML tags; they should be done AFTER global escape
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

        if line.strip().startswith("```"):
            if not in_code:
                in_code = True
                out_lines.append("<pre><code>")
            else:
                in_code = False
                out_lines.append("</code></pre>")
            continue
        if in_code:
            out_lines.append(escape_html(line.rstrip("\n")))
            continue

        elif line.startswith("###"):
            content = line[4:].strip()
            content = process_inline(content) 
            html = f"<h3>{content}</h3>"
            out_lines.append(html)
        elif line.startswith("## "):
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
        
 