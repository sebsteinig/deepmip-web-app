# app/Dockerfile

FROM python:3.9-slim

WORKDIR /deepmip_database_app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    python3-dev \
    libgeos-dev \
    pkg-config \
    libhdf5-dev \
    && rm -rf /var/lib/apt/lists/*


# install dependencies with pip
RUN git clone https://github.com/sebsteinig/deepmip_database_app.git .

# USER root
# RUN apt-get update                             \
#  && apt-get install -y --no-install-recommends \
#     ca-certificates curl firefox-esr           \
#  && rm -fr /var/lib/apt/lists/*                \
#  && curl -L https://github.com/mozilla/geckodriver/releases/download/v0.30.0/geckodriver-v0.30.0-linux64.tar.gz | tar xz -C /usr/local/bin \
#  && apt-get purge -y ca-certificates curl


USER root
RUN apt-get update                             \
 && apt-get install -y --no-install-recommends \
    ca-certificates curl firefox-esr           \
 && rm -fr /var/lib/apt/lists/*                \             
 && curl -L https://github.com/mozilla/geckodriver/releases/download/v0.30.0/geckodriver-v0.30.0-linux64.tar.gz | tar xz -C /usr/local/bin \
 && chmod +x /usr/local/bin/geckodriver
 
# libgeos-dev above and next two lines necessary to fix issues with cartopy projections
# RUN python3 -m pip install --upgrade pip setuptools wheel
# RUN pip3 install "shapely<2" --no-binary shapely


ADD requirements.txt .
RUN python3 -m pip install --no-cache-dir --compile -r requirements.txt

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "0_Home.py", "--server.port=8501", "--server.address=0.0.0.0"]
