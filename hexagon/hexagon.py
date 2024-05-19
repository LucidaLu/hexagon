from pathlib import Path
import shutil
import os, sys
import subprocess
import resource, psutil, time
from multiprocessing import Process, Queue
from tqdm import tqdm
import yaml


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

    with open(f"{fn}", "r") as stream:
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
        cn_name = open(p + "/1-CN-NAME").read()
        full_name = f"{cn_name}（{p}）"
        PROBLEM_TEMPLATE = (
            r"""
\renewcommand{\cnname}{\protect\input{1-CN-NAME}\unskip}
\renewcommand{\enname}{\protect\input{2-EN-NAME}\unskip}

\section["""
            + full_name
            + r"""]{\cnname（\englishname{\enname}）}

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
        )
        s += PROBLEM_TEMPLATE.replace(r"\input{", "\\input{%s/" % (p))

    data_dict["prob-statements"] = s
    for k, v in data_dict.items():
        if type(v) == str:
            content = content.replace("{{%s}}" % (k), v)

    with open("statement-full.tex", "w") as f:
        f.write(content)


def get_std_solution():
    for f in os.listdir("solutions"):
        if f.startswith("std"):
            return f
    assert 0


def generate_sample_output(fn=None):
    if fn is not None:
        os.chdir(fn)
    else:
        fn = Path.cwd().name

    if not Path("1-CN-NAME").exists():
        print(color("Problem not found", "red"))
        return

    Path("tmp").mkdir(exist_ok=True)
    print(
        color("Working on problem", "green"),
        color(
            open("1-CN-NAME", "r").read() + " (" + open("2-EN-NAME", "r").read() + ")",
            "blue",
        ),
    )

    std = get_std_solution()
    print(color("Selected std solution:", "green"), color(std, "blue"))
    compile_cpp(f"solutions/{std}", "tmp/exec")

    with open("9-samples-note.tex", "r") as f:
        sample_notes = {}
        for n in f.read().split("%%"):
            if not n.strip():
                continue
            lines = n.split("\n")
            sample_notes[int(lines[0])] = "\n".join(lines[1:])

    samples = []
    for f in os.listdir("testcases"):
        if f.startswith("sample"):
            shutil.copy(f"testcases/{f}", f"tmp/{fn}.in")

            run_program(1000, Queue())

            with open(f"testcases/{f}", "r") as file:
                input = file.read()
            with open(f"tmp/{fn}.out", "r") as file:
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
            if len(input) + len(output) < 200:
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

    shutil.rmtree("tmp")


def run_program(timeout, q):
    os.chdir("tmp")
    p = subprocess.Popen(["timeout", f"{timeout}s", "./exec"])
    p.wait()
    ro = resource.getrusage(resource.RUSAGE_CHILDREN)
    q.put((ro.ru_maxrss, ro.ru_utime))
    os.chdir("..")


def dos2unix(fn):
    with open(fn, "r") as f:
        content = f.read()
    with open(fn, "w") as f:
        f.write(content.replace("\r\n", "\n"))


def get_testcases():
    testcases = list(os.listdir("testcases"))

    def sort_key(x):
        if x.startswith("sample"):
            return (0, int(x.replace("sample", "")))
        else:
            return (1, int(x))

    testcases.sort(key=sort_key)

    return testcases


def compile_cpp(src, dest):
    subprocess.run(
        [
            "g++",
            src,
            "-w",
            "-std=c++14",
            "-o",
            dest,
            "-O2",
            "-I" + str(Path.home() / ".hexagon/assets"),
        ]
    )


def validate(fn=None):
    if fn is not None:
        os.chdir(fn)
    else:
        fn = Path.cwd().name

    if not Path("1-CN-NAME").exists():
        print(color("Problem not found", "red"))
        return

    if Path("ans").exists():
        shutil.rmtree("ans")
    Path("ans").mkdir()
    Path("tmp").mkdir(exist_ok=True)

    testcases = get_testcases()
    max_tc_name = max(len(tc) for tc in testcases)
    # convert to LF
    print(color("Building validator", "green"))
    compile_cpp("testlib/validator.cpp", "tmp/validator")

    print(color("Validating testcases", "green"))
    for tc in testcases:
        print(tc.rjust(max_tc_name, " "), end=" ")
        code = subprocess.run(
            [str(Path.cwd() / "tmp/validator")],
            stdin=open(f"testcases/{tc}", "r"),
        ).returncode
        assert code == 0
        print(color("passed", "green"))

    print()

    def execute(timelimit):
        q = Queue()
        p = Process(target=run_program, args=(timelimit, q))
        p.start()
        p.join()
        return q.get()

    datas = []

    std = get_std_solution()
    print(color("Selected std solution:", "green"), color(std, "blue"))
    compile_cpp(f"solutions/{std}", "tmp/exec")

    print(color("Generating std answer", "green"))
    Path("ans").mkdir(exist_ok=True)

    data = [('"' + std + '"', "std"), 100]
    for j, t in tqdm(enumerate(testcases), total=len(testcases)):
        shutil.copy(f"testcases/{t}", f"tmp/{fn}.in")
        mem, time = execute(1000)
        shutil.copy(f"tmp/{fn}.out", f"ans/{t}.out")
        data.append(
            (
                "%.3fs(%.0fmb)" % (time, int(mem / 1024)),
                "ok",
            )
        )
    datas.append(data)

    import pandas as pd

    print()
    timelimit = int(open("3-TIME-LIMIT", "r").read().strip())
    print(color("Time limit:", "green"), color(str(timelimit) + "s", "blue"))
    print(color("Building checker", "green"))
    compile_cpp("testlib/checker.cpp", "tmp/checker")

    print(color("Validating solutions", "green"))

    print()

    remains = list(filter(lambda x: x != std, os.listdir("solutions")))
    time_limit = int(open("3-TIME-LIMIT", "r").read().strip())
    for i, sol in enumerate(remains):
        compile_cpp(f"solutions/{sol}", "tmp/exec")
        print(
            color(
                "Running solution %d out of %d:" % (i + 1, len(remains)),
                "green",
            ),
            color(sol, "blue"),
        )
        data = [('"' + sol + '"', ""), 0]
        cnt = 0
        for j, t in enumerate(
            testcases
        ):  # tqdm(enumerate(testcases), total=len(testcases)):
            shutil.copy(f"testcases/{t}", f"tmp/{fn}.in")
            print(t.rjust(max_tc_name, " "), end=" ")
            mem, time = execute(time_limit)
            if os.path.exists(f"tmp/{fn}.out"):
                code = subprocess.run(
                    [
                        str(Path.cwd() / "tmp/checker"),
                        str(Path.cwd() / "tmp/{fn}.in"),
                        str(Path.cwd() / f"tmp/{fn}.out"),
                        str(Path.cwd() / f"ans/{t}.out"),
                        # str(Path.cwd() / "tmp/report"),
                    ]
                ).returncode
                os.remove(f"tmp/{fn}.out")
            else:
                time = timelimit

            ok = code == 0
            if not t.startswith("sample"):
                cnt += ok

            data.append(
                (
                    "%.3fs(%.0fmb)" % (time, int(mem / 1024)),
                    "ok" if ok else "fail",  # "green" if ok else "red",
                )
            )
        data[1] = int(
            100
            / len(list(filter(lambda x: not x.startswith("sample"), testcases)))
            * cnt
        )
        datas.append(data)

        print()

    def fmt1(x):
        if type(x) == tuple:
            if x[1] == "":
                return x[0]
            else:
                cmap = {"ok": "green", "fail": "red", "std": "blue"}
                return color(x[0], cmap[x[1]])
        else:
            return x

    def fmt2(x):
        if type(x) == tuple:
            if x[1] == "":
                return x[0]
            else:
                return x[1] + " " + x[0]
        else:
            return x

    print(color("Summary", "green"))

    def transpose_markdown(df):
        df = df.transpose()
        df.columns = ["" for i in range(len(df.columns))]
        # df.index = ["{}".format(idx) for idx in df.index]
        l = df.to_markdown(tablefmt="grid").split("\n")[2:]
        l[0], l[2] = l[2], l[0]
        return "\n".join(l)

    print(
        transpose_markdown(
            pd.DataFrame(
                [[fmt1(x) for x in d] for d in datas],
                columns=["solution", "score"] + testcases,
            )
        )
    )

    with open("validation report.md", "w") as f:
        f.write("# Validation Report\n\n")
        from datetime import datetime as dt

        f.write(dt.now().strftime("%Y-%m-%d %H:%M:%S") + "\n\n")
        f.write(
            pd.DataFrame(
                [
                    [
                        fn,
                        str(timelimit) + "s",
                        open("4-MEMORY-LIMIT", "r").read().strip() + " MiB",
                        len(
                            list(
                                filter(lambda x: not x.startswith("sample"), testcases)
                            )
                        ),
                    ]
                ],
                columns=["problem", "time limit", "memory limit", "testcases"],
            )
            # .transpose()
            .to_markdown(index=False)
            + "\n\n"
        )

        f.write(
            transpose_markdown(
                pd.DataFrame(
                    [[fmt2(x) for x in d] for d in datas],
                    columns=["solution", "score"] + testcases,
                )
            )
        )

    shutil.rmtree("tmp")


def validate_contest(fn):
    with open(f"{fn}", "r") as stream:
        data_dict = yaml.safe_load(stream)
    curdir = os.getcwd()
    print(
        color("Validating contest:", "green"), color(data_dict["title"], "blue") + "\n"
    )

    with open(curdir + "/" + "validation report.md", "w") as f:
        f.write("# Validation Report\n\n")
        for i, pname in enumerate(data_dict["problems"]):
            os.chdir(curdir + "/" + pname)
            print(color("Validating problem:", "green"), color(pname, "blue"))
            validate()
            f.write(
                f"## {pname}\n\n"
                + open(curdir + "/" + pname + "/validation report.md", "r")
                .read()
                .replace("# Validation Report\n\n", "")
                + "\n\n"
            )
            if i != len(data_dict["problems"]) - 1:
                f.write("\n\n")


def export_problem(fn=None):
    if fn is not None:
        os.chdir(fn)
    else:
        fn = Path.cwd().name

    if not Path("1-CN-NAME").exists():
        print(color("Problem not found", "red"))
        return

    print(color("Exporting problem", "green"), color(fn, "blue"))

    if Path("tmp").exists():
        shutil.rmtree("tmp")
    Path("tmp").mkdir()

    print(color("Compiling statement", "green"))

    with open("statement.tex", "r") as f:
        content = (
            f.read()
            .replace("\\cnname", open("1-CN-NAME", "r").read())
            .replace("\\enname", fn)
        )

    with open("statement-escape.tex", "w") as f:
        f.write(content)

    subprocess.run(
        ["xelatex", "-shell-escape", "statement-escape.tex"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    subprocess.run(
        ["xelatex", "-shell-escape", "statement-escape.tex"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    print(color("Copying files", "green"))

    shutil.copy("statement-escape.pdf", f"tmp/{fn}.pdf")

    os.system("rm statement-escape.*")

    for f in os.listdir("testcases"):
        if f.startswith("sample"):
            shutil.copy(f"testcases/{f}", f"tmp/{fn}{f[6:]}.in")
            shutil.copy(f"ans/{f}.out", f"tmp/{fn}{f[6:]}.ans")

    print(color("Zipping files", "green"))
    shutil.make_archive(fn, "zip", "tmp")

    print(color("Cleaning up", "green"))
    shutil.rmtree("tmp")


def export_contest(fn):
    with open(f"{fn}", "r") as stream:
        data_dict = yaml.safe_load(stream)

    fn = fn.replace(".yaml", "")

    print(color("Exporting contest:", "green"), color(data_dict["title"], "blue"))

    if Path("tmp").exists():
        shutil.rmtree("tmp")
    Path("tmp").mkdir()

    print(color("Compiling statement", "green"))

    subprocess.run(
        ["xelatex", "-shell-escape", "statement-full.tex"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    subprocess.run(
        ["xelatex", "-shell-escape", "statement-full.tex"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    shutil.copy("statement-full.pdf", f"tmp/statement.pdf")

    for pname in data_dict["problems"]:
        Path(f"tmp/{pname}").mkdir()
        for f in os.listdir(f"{pname}/testcases"):
            if f.startswith("sample"):
                shutil.copy(f"{pname}/testcases/{f}", f"tmp/{pname}/{pname}{f[6:]}.in")
                shutil.copy(f"{pname}/ans/{f}.out", f"tmp/{pname}/{pname}{f[6:]}.ans")

    print(color("Zipping files", "green"))
    shutil.make_archive(fn, "zip", "tmp")

    print(color("Cleaning up", "green"))
    shutil.rmtree("tmp")

    print(color("Building lemon package", "green"))
    Path("tmp").mkdir()
    Path("tmp/data").mkdir()
    Path("tmp/source").mkdir()

    empty_lists = [[] for _ in range(len(data_dict["problems"]))]
    meta = {
        "contestTitle": fn,
        "contestants": [
            {
                "checkJudged": [False] * len(data_dict["problems"]),
                "compileMesaage": [""] * len(data_dict["problems"]),
                "compileState": [1] * len(data_dict["problems"]),
                "contestantName": "std",
                "inputFiles": empty_lists,
                "judgingTime_date": 0,
                "judgingTime_time": 0,
                "judgingTime_timespec": 0,
                "memoryUsed": empty_lists,
                "message": empty_lists,
                "result": empty_lists,
                "score": empty_lists,
                "sourceFile": [""] * len(data_dict["problems"]),
                "timeUsed": empty_lists,
            }
        ],
        "tasks": [],
    }

    Path("tmp/source/std").mkdir()
    Path("tmp/checker").mkdir()

    for pname in data_dict["problems"]:
        # copy checker
        with open(f"{pname}/testlib/checker.cpp", "r") as f:
            code = f.read()
        code = code.replace("registerTestlibCmd", "registerLemonChecker")
        with open(f"tmp/checker/{pname}.cpp", "w") as f:
            f.write(code)

        # problem metadata
        problem_meta = {
            "answerFileExtension": "out",
            "comparisonMode": 4,
            "compilerConfiguration": {"g++": "C++14 O2"},
            "diffArguments": "--ignore-space-change --text --brief",
            "inputFileName": f"{pname}.in",
            "outputFileName": f"{pname}.out",
            "problemTitle": pname,
            "realPrecision": 4,
            "sourceFileName": pname,
            "specialJudge": f"{pname}/checker.exe",
            "standardInputCheck": False,
            "standardOutputCheck": False,
            "subFolderCheck": True,
            "taskType": 0,
            "testCases": [],
        }

        with open(f"{pname}/4-MEMORY-LIMIT", "r") as f:
            memlimit = int(f.read().strip())
        with open(f"{pname}/3-TIME-LIMIT", "r") as f:
            timelimit = int(f.read().strip())

        shutil.copytree(f"{pname}/solutions", f"tmp/source/std/{pname}")
        shutil.move(
            f"tmp/source/std/{pname}/std.cpp", f"tmp/source/std/{pname}/{pname}.cpp"
        )

        Path("tmp/data/" + pname).mkdir()

        # problem testcases
        testcases = list(
            filter(
                lambda x: not x.startswith("sample"),
                os.listdir(f"{pname}/testcases"),
            )
        )

        testcases.sort(key=lambda x: int(x))
        for f in testcases:
            shutil.copy(f"{pname}/testcases/{f}", f"tmp/data/{pname}/{f}.in")
            shutil.copy(f"{pname}/ans/{f}.out", f"tmp/data/{pname}/{f}.ans")
            problem_meta["testCases"].append(
                {
                    "fullScore": 100 / len(testcases),
                    "inputFiles": [f"{pname}/{f}.in"],
                    "memoryLimit": memlimit,
                    "outputFiles": [f"{pname}/{f}.ans"],
                    "timeLimit": timelimit * 1000,
                }
            )

        meta["tasks"].append(problem_meta)

    shutil.copy(
        str(Path.home() / ".hexagon/assets/testlib-lemon.h"), "tmp/checker/testlib.h"
    )

    compile_cmd = ""
    for pname in data_dict["problems"]:
        compile_cmd += f"g++ checker/{pname}.cpp -std=c++14 -O2 -o checker/{pname}\n"
        compile_cmd += f"mv checker/{pname}.exe data/{pname}/checker.exe\n"

    with open("tmp/generate_checkers.bat", "w") as f:
        f.write(compile_cmd)
    with open("tmp/generate_checkers.sh", "w") as f:
        f.write(compile_cmd.replace(".exe", ""))

    # create empty file
    open("tmp/GENERATE CHECKERS FIRST", "w").close()

    shutil.copy("statement-full.pdf", "tmp/statement.pdf")

    with open(f"tmp/{fn}.cdf", "w") as f:
        import json

        f.write(json.dumps(meta))

    shutil.make_archive("Lemon_package_" + fn, "zip", "tmp")

    print(color("Cleaning up", "green"))
    shutil.rmtree("tmp")


def main():
    UA = """Usage: hexagon.py [create|build|validate]
create:     'create problem-name' to create a new problem
build:      'build contest-name' to build a contest statement
            'build problem-name' to build a problem statement
            if no argument is given, then build the statement for the problem in the current directory
validate:   same as build, but doing validations instead
export:     same as build, but export problem/contest packages instead
"""
    if len(sys.argv) == 1:
        print(UA)
    else:
        if sys.argv[1] == "create":
            create_problem(sys.argv[2])
        elif sys.argv[1] == "build":
            if len(sys.argv) < 3:
                generate_sample_output()
            else:
                if Path(sys.argv[2]).is_dir():
                    generate_sample_output(sys.argv[2])
                else:
                    build_contest(sys.argv[2])
        elif sys.argv[1] == "validate":
            if len(sys.argv) < 3:
                validate()
            else:
                if Path(sys.argv[2]).is_dir():
                    validate(sys.argv[2])
                else:
                    validate_contest(sys.argv[2])
        elif sys.argv[1] == "export":
            if len(sys.argv) < 3:
                export_problem()
            else:
                if Path(sys.argv[2]).is_dir():
                    export_problem(sys.argv[2])
                else:
                    export_contest(sys.argv[2])
        else:
            print(UA)


if __name__ == "__main__":
    main()
