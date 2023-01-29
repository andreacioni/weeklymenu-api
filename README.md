## weeklymenu-api

### Model Upload

```
flyctl sftp shell
    >> put models/ingredient_parser_model_v1.tar.gz /etc/weeklymenu/models/ingredient_parser_model_v1.tar.gz
```

```
flyctl ssh console
    >> cd /etc/weeklymenu/models/
    >> tar -xf ingredient_parser_model_v1.tar.gz
```
