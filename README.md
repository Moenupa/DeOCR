# DeOCR

DeOCR (de-cor), A reverse OCR tool that transforms text datasets (JSON, CSV) to images of specified sizes (e.g., `512x512` or `1024x1024`). This tool can be considered as a text-to-image data pre-processing component in pipelines such as [DeepSeek-OCR](https://github.com/deepseek-ai/DeepSeek-OCR).

```mermaid
flowchart LR
  TEXTDATA[/"some context in text form"/]
  MMDATA[/"Does this particular car <br/> fa:fa-image (fa:fa-car) present in here fa:fa-image ?"/]
  HFDATASET[("huggingface dataset")] 
  subgraph DeOCR
    CSS1["cli --style red-text textit"]
    CSS2["cli --style default"]
    CSS3["cli --style default"]
    MAPPER["DeOCR Dataset Mapper"]
  end
  TEXTDATA --> CSS1 --> IMG1[["some context in text form"]]:::redText
  TEXTDATA --> CSS2 --> IMG2[["some context in text form"]]
  MMDATA --> CSS3 --> IMG3[["Does this particular car <br/> fa:fa-image <br/> present in here <br/>fa:fa-image <br/>?"]]
  HFDATASET --> MAPPER --> DEOCRDATASET[("fa:fa-image imagified dataset")]
  classDef redText color:#ff0000,font-style:italic;
  IMG1 ~~~|"fa:fa-mobile-screen A screenshot of text <br/>w. special formatting"| IMG1
  IMG2 ~~~|"fa:fa-mobile-screen A plain screenshot of text"| IMG2
  IMG3 ~~~|"fa:fa-mobile-screen A screenshot of both text and images"| IMG3
```

# Quick Start

```sh
# TODO: this is not ready yet
pip install deocr
```

<details><summary>Alternatively, install from source</summary>

```sh
# uv
uv add "deocr @ https://github.com/Moenupa/DeOCR.git"
# for pip or conda
pip install "git+https://github.com/Moenupa/DeOCR.git"
```

For development, please use uv to manage the environment:

```sh
git clone https://github.com/Moenupa/DeOCR.git
cd DeOCR
uv venv
uv sync --dev
pre-commit install
```

</details>
