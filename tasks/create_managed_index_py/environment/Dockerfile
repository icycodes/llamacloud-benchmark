FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep && \
    pip3 install --break-system-packages \
        pytest-json-ctrf \
        llama-index-core \
        llama-index-indices-managed-llama-cloud && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/user && chmod 0755 /home/user

RUN mkdir -p /home/user/myproject/data && \
    cat >/home/user/myproject/data/cats.txt <<'EOF'
Cats are small carnivorous mammals that are often kept as pets.
They are obligate carnivores, meaning their diet should consist primarily of meat.
Cats commonly enjoy eating fish, chicken, and specially formulated cat food.
Many cats love tuna and other seafood as occasional treats.
A balanced diet for a cat usually contains high-protein meats and a small amount of fat.
EOF

RUN cat >/home/user/myproject/data/dogs.txt <<'EOF'
Dogs are loyal domesticated mammals that have lived alongside humans for thousands of years.
They are omnivores and thrive on a varied diet of meats, grains, and vegetables.
Popular dog activities include fetching, running, and playing tug-of-war.
Different breeds have different temperaments, ranging from energetic working dogs to relaxed lap dogs.
EOF

RUN cat >/home/user/myproject/data/birds.txt <<'EOF'
Birds are warm-blooded vertebrates that have feathers, beaks, and lay eggs.
Many bird species undertake long seasonal migrations, traveling thousands of miles between breeding and wintering grounds.
Common backyard birds include sparrows, robins, and finches.
Bird diets vary widely: some eat seeds and fruit, while others hunt insects or small fish.
EOF

LABEL Author="generate-harbor-tasks"
LABEL Description="LlamaCloud managed index task: Python environment with llama-index-indices-managed-llama-cloud installed and a small text corpus under /home/user/myproject/data."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - pip3 packages for the LlamaCloud managed index task:
#       llama-index-core, llama-index-indices-managed-llama-cloud
#   - /home/user/myproject: working project directory
#   - /home/user/myproject/data/cats.txt: seed document about cats
#   - /home/user/myproject/data/dogs.txt: seed document about dogs
#   - /home/user/myproject/data/birds.txt: seed document about birds
