ARG DOCKER_REGISTRY=public.aml-repo.cms.waikato.ac.nz:443/
FROM ${DOCKER_REGISTRY}ubuntu:22.04

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
       git-core \
       wget \
       python3 \
       python3-dev \
       python3-venv \
       python3-pip \
       python3-pandas \
       python3-chardet \
       build-essential \
       libglib2.0-0 \
       libsm6 \
       libxrender-dev \
       libxext6 \
       libgl1-mesa-glx \
       libpq-dev && \
       antiword && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 --no-cache-dir install \
        git+https://github.com/waikato-llm/llm-dataset-converter.git \
        git+https://github.com/waikato-llm/ldc-doc.git \
        git+https://github.com/waikato-llm/ldc-docx.git \
        git+https://github.com/waikato-llm/ldc-google.git \
        git+https://github.com/waikato-llm/ldc-html.git \
        git+https://github.com/waikato-llm/ldc-openai.git \
        git+https://github.com/waikato-llm/ldc-pdf.git \
        git+https://github.com/waikato-llm/ldc-tint.git

COPY bash.bashrc /etc/bash.bashrc

WORKDIR /workspace
