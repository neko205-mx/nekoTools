input_file = "1.txt"
output_file = "output1.txt"

with open(input_file, "r") as infile, open(output_file, "w") as outfile:
    for line in infile:
        clean_line = line.replace(" open", "").strip()
        outfile.write(clean_line + "\n")
print(f"处理完成，结果已保存到 {output_file}")
