from pathlib import Path
import shutil
import os, sys


def color(text, color):
    codes = {
        "black": "0;30",
        "bright gray": "0;37",
        "blue": "1;34",
        "white": "1;37",
        "green": "1;32",
        "bright blue": "1;34",
        "cyan": "0;36",
        "bright green": "1;32",
        "red": "1;31",
        "bright cyan": "1;36",
        "purple": "0;35",
        "bright red": "1;31",
        "yellow": "0;33",
        "bright purple": "1;35",
        "dark gray": "1;30",
        "bright yellow": "1;33",
        "normal": "0",
    }
    return "\033[" + codes[color] + "m" + text + "\033[0m"


def create_problem(name):
    assert not Path(name).exists(), f"Problem {name} already exists"
    shutil.copytree(Path.home() / ".hexagon/template", name)
    with open(name + "/2-EN-NAME", "w") as f:
        f.write(name)


def build_contest(fn):
    rows = [
        "题目名称",
        "题目类型",
        "目录",
        "可执行文件名",
        "输入文件名",
        "输出文件名",
        "测试点时限",
        "内存限制",
        "测试点数目",
        "测试点是否等分",
    ]

    probs = []
    # read yaml
    import yaml

    with open(f"{fn}.yaml", "r") as stream:
        data_dict = yaml.safe_load(stream)

    for pname in data_dict["problems"]:
        pname = pname.strip()

        c = [
            open(f"{pname}/1-CN-NAME", "r").read().strip(),
            open(f"{pname}/2-EN-NAME", "r").read().strip(),
            open(f"{pname}/3-TIME-LIMIT", "r").read().strip(),
            open(f"{pname}/4-MEMORY-LIMIT", "r").read().strip(),
            len(
                list(
                    filter(
                        lambda x: not x.startswith("sample"),
                        os.listdir(f"{pname}/testcases"),
                    )
                )
            ),
        ]
        prob = [
            open(f"{pname}/1-CN-NAME", "r").read().strip(),
            "传统题",
            r"\texttt{%s}" % (c[1]),
            r"\texttt{%s}" % (c[1]),
            r"\texttt{%s}" % (c[1] + ".in"),
            r"\texttt{%s}" % (c[1] + ".out"),
            c[2] + "秒",
            str(c[3]) + " MiB",
            str(c[4]),
            "是",
            c[1],
        ]
        probs.append(prob)

    s = ""

    for i in range(len(rows)):
        s += " & ".join([rows[i]] + [prob[i] for prob in probs]) + r"\\ \hline "

    rowplh = "".join("X|" for _ in range(len(probs)))

    data_dict["meta"] = (
        r"""
\begin{tabularx}{\textwidth}{|p{3.2cm}|%s}
\hline
%s
\end{tabularx}\par
"""
        % (
            rowplh,
            s,
        )
    )

    data_dict["fns"] = (
        r"""
\begin{tabularx}{\textwidth}{|p{3.2cm}|%s}
\hline
对于 C++ & %s \\
\hline
\end{tabularx}\par
"""
        % (
            rowplh,
            " & ".join([r"\texttt{%s.cpp}" % (prob[-1]) for prob in probs]),
        )
    )

    with open(Path.home() / ".hexagon" / "statement-full.tex", "r") as f:
        content = f.read()
    s = ""

    for p in data_dict["problems"]:
        s += "%% problem statement for %s\n" % (p)
        PROBLEM_TEMPLATE = r"""
\renewcommand{\cnname}{\protect\input{1-CN-NAME}\unskip}
\renewcommand{\enname}{\protect\input{2-EN-NAME}\unskip}

\section{\cnname（\englishname{\enname}）}

\subsection[题目描述]{【题目描述】}
\input{5-legend}
\subsection[输入格式]{【输入格式】}
从文件 \filename{\enname.in} 中读入数据。
\input{6-input-format}
\subsection[输出格式]{【输出格式】}
输出到文件 \filename{\enname.in} 中。
\input{7-output-format}
\input{generated-samples}

\subsection[数据范围]{【数据范围】}
\input{8-testcases-spec}
\clearpage

"""
        s += PROBLEM_TEMPLATE.replace(r"\input{", "\\input{%s/" % (p))

    data_dict["prob-statements"] = s
    for k, v in data_dict.items():
        if type(v) == str:
            content = content.replace("{{%s}}" % (k), v)

    with open("statement-full.tex", "w") as f:
        f.write(content)


def generate_sample_output(fn=None):
    if fn is not None:
        os.chdir(fn)

    Path("tmp").mkdir(exist_ok=True)
    print(
        color("Working on problem", "green"),
        color(
            open("1-CN-NAME", "r").read() + " (" + open("2-EN-NAME", "r").read() + ")",
            "blue",
        ),
    )

    for f in Path("solutions").iterdir():
        f = str(f)
        if f.startswith("solutions/100"):
            print(color("Selected std solution:", "green"), color(f, "blue"))
            os.system(f"g++ {f} -std=c++17 -o tmp/exec")
            break

    with open("9-samples-note.tex", "r") as f:
        sample_notes = {}
        for n in f.read().split("%%"):
            if not n.strip():
                continue
            lines = n.split("\n")
            sample_notes[int(lines[0])] = "\n".join(lines[1:])

    samples = []
    for root, dirs, files in os.walk("testcases"):
        for f in files:
            if f.startswith("sample"):
                os.system(f"tmp/exec < testcases/{f} > tmp/{f}.ans")
                with open(f"testcases/{f}", "r") as file:
                    input = file.read()
                with open(f"tmp/{f}.ans", "r") as file:
                    output = file.read()
                no = int(f.replace("sample", ""))
                if no not in sample_notes:
                    sample_notes[no] = ""
                samples.append((input, output, sample_notes[no]))

    cnt = [0, 0]
    with open("generated-samples.tex", "w") as f:
        f.write("%% this file is auto-generated. Do not edit it directly.\n\n")
        for i, s in enumerate(samples):
            no = "样例" + ("" if len(samples) == 1 else r" {\rm %s}" % (str(i + 1)))
            input, output, note = s

            # print(len(input) + len(output))
            if len(input) + len(output) < 50:
                cnt[0] += 1
                if input.endswith("\n"):
                    input = input[:-1]
                if output.endswith("\n"):
                    output = output[:-1]

                ifnote = ""
                if len(note) > 0:
                    ifnote = r"""
\subsection[%s]{【%s】}

%s
""" % (
                        no + " 解释",
                        no + " 解释",
                        note,
                    )
                f.write(
                    r"""
\subsection[%s]{【%s】}
\begin{minted}[linenos]{text}
%s
\end{minted}

\subsection[%s]{【%s】}
\begin{minted}[linenos]{text}
%s
\end{minted}

%s
"""
                    % (
                        no + " 输入",
                        no + " 输入",
                        input,
                        no + " 输出",
                        no + " 输出",
                        output,
                        ifnote,
                    )
                )
            else:
                cnt[1] += 1
                f.write(
                    r"""
\subsection[%s]{【%s】}
见选手目录下的\filename{\enname/\enname%d.in}与\filename{\enname/\enname%d.ans}。

%s
"""
                    % (no, no, i + 1, i + 1, note)
                )
    print(
        color("Found", "green"),
        color(str(cnt[0]), "blue"),
        color("small sample(s),", "green"),
        color(str(cnt[1]), "blue"),
        color("big sample(s)", "green"),
    )
    import shutil

    shutil.rmtree("tmp")


def validate(fn):
    if fn is not None:
        os.chdir(fn)

    Path("tmp").mkdir(exist_ok=True)
    testcases = list(os.listdir("testcases"))

    def sort_key(x):
        if x.startswith("sample"):
            return (0, int(x.replace("sample", "")))
        else:
            return (1, int(x))

    sys.path.append(str(Path.home() / ".hexagon"))
    import _judger

    testcases.sort(key=sort_key)
    for sol in os.listdir("solutions"):
        os.system(f"g++ solutions/{sol} -std=c++14 -o tmp/exec -O2")
        for t in testcases:
            job = _judger.run(
                max_cpu_time=1000,
                max_real_time=2000,
                max_memory=128 * 1024 * 1024,
                max_process_number=200,
                max_output_size=10000,
                max_stack=32 * 1024 * 1024,
                # five args above can be _judger.UNLIMITED
                exe_path="tmp/exec",
                input_path=f"testcases/{t}",
                output_path=f"tmp/{t}.out",
                error_path="/dev/null",
                args=[],
                env=[],
                log_path="",
                seccomp_rule_name="c_cpp",
                uid=0,
                gid=0,
            )
            print(job)

    shutil.rmtree("tmp")


if __name__ == "__main__":
    import sys

    if len(sys.argv) == 1:
        print("Usage: hexagon.py [create-problem|build-contest|generate-sample-output]")
    else:
        if sys.argv[1] == "create-problem":
            create_problem(sys.argv[2])
        elif sys.argv[1] == "build-contest":
            build_contest(sys.argv[2])
        elif sys.argv[1] == "build-problem":
            generate_sample_output(sys.argv[2])
        elif sys.argv[1] == "validate":
            validate(sys.argv[2])
        else:
            print(
                "Usage: hexagon.py [create-problem|build-contest|generate-sample-output]"
            )
