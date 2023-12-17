#! /bin/bash
docker exec -i airflow-webserver /bin/bash <<EOF

airflow users create \
    --username admin \
    --firstname Jack \
    --lastname Sparrow \
    --role Admin \
    --email example@mail.org \
    --pass pass

pass
pass

exit

EOF

docker exec -i airflow-scheduler /bin/bash <<EOF

pip install confluent-kafka

airflow scheduler

EOF