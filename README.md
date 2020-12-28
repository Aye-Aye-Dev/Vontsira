# Vontsira
A data registry


## Running it locally

```shell
export PYTHONPATH=`pwd`
cd vontsira/settings
cp local_config_example.py local_config.py
cd ../..
python manage.py local update_database
```
