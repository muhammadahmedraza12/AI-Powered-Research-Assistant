# write_pdf.py

from langchain_core.tools import tool
from datetime import datetime
from pathlib import Path
import subprocess
import shutil
import re

def extract_latex_title(latex_content: str) -> str:
    """Extracts the title from LaTeX content (if defined)."""
    match = re.search(r'\\title\{(.+?)\}', latex_content)
    if match:
        return match.group(1).strip()
    return "document"  # fallback if no title found


@tool
def render_latex_pdf(latex_content: str) -> str:
    """
    Render a LaTeX document to PDF with improved formatting.
    If the content already contains \documentclass, compile as-is.
    Otherwise, wrap with a styled preamble.
    """

    if shutil.which("tectonic") is None:
        raise RuntimeError("tectonic is not installed. Install it first on your system.")

    try:
        # Step1: Create output directory
        output_dir = Path("output").absolute()
        output_dir.mkdir(exist_ok=True)

        # Step2: Extract safe title for filenames
        raw_title = extract_latex_title(latex_content)
        safe_title = re.sub(r'[^a-zA-Z0-9_-]', '_', raw_title)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        tex_filename = f"{safe_title}_{timestamp}.tex"
        pdf_filename = f"{safe_title}_{timestamp}.pdf"

        # Step3: Check if full LaTeX doc already exists
        if "\\documentclass" in latex_content:
            print("⚠️ Detected full LaTeX document. Compiling as-is.")
            full_latex = latex_content
        else:
            print("ℹ️ Detected body-only LaTeX. Wrapping with preamble.")
            preamble = r"""
\documentclass[12pt]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{lmodern}          % Modern font
\usepackage[margin=1in]{geometry}
\usepackage{setspace}         % Line spacing
\onehalfspacing
\usepackage{titlesec}         % Section formatting
\titleformat{\section}{\large\bfseries}{\thesection}{1em}{}
\titleformat{\subsection}{\normalsize\bfseries}{\thesubsection}{1em}{}
\usepackage{amsmath, amssymb} % Math support
\usepackage{hyperref}         % Clickable references
\hypersetup{
    colorlinks=true,
    linkcolor=blue,
    urlcolor=blue,
    citecolor=blue
}
\begin{document}
"""
            ending = r"\end{document}"
            full_latex = f"{preamble}\n{latex_content}\n{ending}"

        # Step4: Write .tex file
        tex_file = output_dir / tex_filename
        tex_file.write_text(full_latex)

        # Step5: Compile with tectonic
        result = subprocess.run(
            ["tectonic", tex_filename, "--outdir", str(output_dir)],
            cwd=output_dir,
            capture_output=True,
            text=True,
        )

        # Debug logs
        if result.returncode != 0:
            print("Tectonic error output:\n", result.stderr)

        # Step6: Check PDF
        final_pdf = output_dir / pdf_filename
        if not final_pdf.exists():
            raise FileNotFoundError("PDF file was not generated")

        print(f"✅ Successfully generated PDF at {final_pdf}")
        return str(final_pdf)

    except Exception as e:
        print(f"❌ Error rendering LaTeX: {str(e)}")
        raise



# # Step1: Install tectonic & Import deps
# from langchain_core.tools import tool
# from datetime import datetime
# from pathlib import Path
# import subprocess
# import shutil
# import re

# def extract_latex_title(latex_content: str) -> str:
#     """Extracts the title from LaTeX content (if defined)."""
#     match = re.search(r'\\title\{(.+?)\}', latex_content)
#     if match:
#         return match.group(1).strip()
#     return "document"  # fallback if no title found

# @tool
# def render_latex_pdf(latex_content: str) -> str:
    
#     """Render a LaTeX document to PDF.

#     Args:
#         latex_content: The LaTeX document content as a string

#     Returns:
#         Path to the generated PDF document
#     """
    
#     if shutil.which("tectonic") is None:
#         raise RuntimeError(
#             "tectonic is not installed. Install it first on your system."
#         )

#     print("LATEX CONTENT-------",latex_content)

#     try:
#         # Step2: Create directory
#         output_dir = Path("output").absolute()
#         output_dir.mkdir(exist_ok=True)

#         # Step3: Setup filenames
#         # timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#         # tex_filename = f"{latex_content.title}_{timestamp}.tex"
#         # pdf_filename = f"{latex_content.title}_{timestamp}.pdf"

#          # safe_title = re.sub(r'[^a-zA-Z0-9_-]', '_', raw_title) 

#          # Step3: Extract title and clean it for filename
#         raw_title = extract_latex_title(latex_content)
#         timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#         tex_filename = f"{raw_title}_{timestamp}.tex"
#         pdf_filename = f"{raw_title}_{timestamp}.pdf"

#         # Step4: Export as tex & pdf
#         tex_file = output_dir / tex_filename
#         tex_file.write_text(latex_content)

#         result = subprocess.run(
#                     ["tectonic", tex_filename, "--outdir", str(output_dir)],
#                     cwd=output_dir,
#                     capture_output=True,
#                     text=True,
#                 )

#         final_pdf = output_dir / pdf_filename
#         if not final_pdf.exists():
#             raise FileNotFoundError("PDF file was not generated")

#         print(f"Successfully generated PDF at {final_pdf}")
#         return str(final_pdf)

#     except Exception as e:
#         print(f"Error rendering LaTeX: {str(e)}")
#         raise