with open('samples/test.md', 'r') as f:
    for line in f:
        if line.startswith("#"):
            modified_line1 = line.replace("#", "<h1>", 1).replace("#", "</h1>", 1)
            with open("samples/output.html", "w") as f:
                f.write(modified_line1)
        elif line.startswith("##"):
            modified_line2 = line.replace("##", "<h2>", 1).replace("##", "</h2>", 1)
            with open("samples/output.html", "w") as f:
                f.write(modified_line2)
        elif line.startswith("-"):
            modified_line3 = line.replace("-", "<ul>", 1).replace("-", "</ul>", 1)  
            with open("samples/output.html", "w") as f:
                f.write(modified_line3)
        else :
            modified_line = line.replace("", "<p>", 1).replace("", "</p>", 1)
            with open("samples/output.html", "w") as f:
                f.write(modified_line)
    



    