#! /bin/bash
docker exec -i patinetes-kafka /bin/bash <<EOF

pip install confluent-kafka pandas

cd /usr/src/app

for i in {1..6}; do
    python3 envio_patinete.py
    sleep 5
done

EOF