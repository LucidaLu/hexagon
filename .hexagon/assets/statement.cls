\ProvidesClass{statement}[Statement Class for Olympiad in Informatics]
\NeedsTeXFormat{LaTeX2e}

\LoadClass[12pt]{ctexart}

\RequirePackage{geometry}
\geometry{bottom=20mm,top=25mm,left=27mm,right=27mm}

\RequirePackage{titling}

\newcommand\SubtitleContent{}
\newcommand\subtitle[1]{\renewcommand\SubtitleContent{#1}}
\pretitle{\vspace*{-20mm}\begin{center}\LARGE\bfseries}
\posttitle{\par\mdseries\LARGE\SubtitleContent\end{center}\vskip 0.5em}

\RequirePackage{fontspec}
\setmonofont[ExternalLocation=\string~/.hexagon/assets/]{Consolas.ttf}

\RequirePackage{titlesec}
\newcommand{\Attention}{\begingroup\titleformat{\subsection}{\bf}{}{0pt}{\hspace{0.5em}}\subsection[注意事项（请仔细阅读）]{【注意事项（请仔细阅读）】}\endgroup}
\titleformat{\section}{\Large\sf}{}{0pt}{\centering\label{sec:\thesection}}
\titleformat{\subsection}{\sf}{}{0.5em}{}
\titleformat{\subsubsection}{\bf}{}{0.5em}{}

\RequirePackage{enumitem}
\setenumerate[1]{itemsep=0pt,partopsep=0pt,parsep=\parskip,topsep=5pt}
\setitemize[1]{itemsep=0pt,partopsep=0pt,parsep=\parskip,topsep=5pt}


\RequirePackage{fancyhdr}
\RequirePackage{lastpage}
\RequirePackage{zref-totpages}

\RequirePackage{color}
\pagestyle{fancy}
\fancyhead[L]{\footnotesize \@title}
\fancyhead[R]{\footnotesize\MakeLowercase{\fancyplain{}{\leftmark}}}
\fancyfoot[C]{\footnotesize 第 \thepage 页 \hspace{2em} 共 { \color{blue} \ztotpages} 页}


\RequirePackage{lineno}
\RequirePackage{tikz}
\RequirePackage{tcolorbox}
\RequirePackage{lineno}
\RequirePackage{fancyvrb}
\renewcommand{\theFancyVerbLine}{\ttfamily\textcolor{gray}{\footnotesize\arabic{FancyVerbLine}}}
\tcbuselibrary{most}

\RequirePackage{etoolbox}
\BeforeBeginEnvironment{minted}{
    \begin{tcolorbox}[
        colframe=blue,
        breakable=true,
        colback = white,
        boxrule = 0.5pt,
        arc = 0pt, 
        left=1mm,
]}
\AfterEndEnvironment{minted}{\end{tcolorbox}}


\RequirePackage{xeCJKfntef}
\newcommand\stress[1]{\textbf{\sf \CJKunderdot{#1}}}
\newcommand\filename[1]{\textbf{\textit{#1}}}
\newcommand\ttstring[1]{\texttt{\uline{#1}}}
\newcommand\englishname[1]{\texorpdfstring{\textrm{\MakeLowercase{#1}}}{#1}}

\RequirePackage{tikz}
\RequirePackage{ulem}
\RequirePackage{tabularx}
\RequirePackage{makecell}
\RequirePackage{skak}
\RequirePackage{color}
\RequirePackage{xcolor}
\RequirePackage{hyperref}
\RequirePackage{listings}
\RequirePackage{algorithm}
\RequirePackage{algorithmic}
\RequirePackage{minted}
\RequirePackage{booktabs,array}

\fancyhead[R]{\footnotesize \MakeLowercase{\fancyplain{}{\leftmark}}}
\renewcommand{\sectionmark}[1]{\markboth{#1}{}} 

\newcommand{\cnname}{\protect\input{1-CN-NAME}\unskip}
\newcommand{\enname}{\protect\input{2-EN-NAME}\unskip}

\title{}